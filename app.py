import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
import pandas as pd
from io import BytesIO
from data_manager import DataManager

# Configure logging
logging.basicConfig(level=logging.DEBUG, force=True)

app = Flask(__name__)

# Ensure data directory exists on startup
os.makedirs('data', exist_ok=True)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Initialize data manager
data_manager = DataManager()

@app.route('/')
def dashboard():
    """Dashboard with summary statistics and today's shifts"""
    try:
        # Get summary statistics
        employees = data_manager.get_employees()
        ambulances = data_manager.get_ambulances()
        shifts = data_manager.get_shifts()
        teams = data_manager.get_teams()
        tasks = data_manager.get_tasks()
        
        total_employees = len(employees)
        total_ambulances = len(ambulances)
        ready_ambulances = len([a for a in ambulances if a['status'] == 'جاهز'])
        
        # Get today's shifts and teams
        today = datetime.now().strftime('%Y-%m-%d')
        today_shifts = [s for s in shifts if s['date'] == today]
        today_teams = [t for t in teams if t['date'] == today]
        
        # Calculate total teams for today
        teams_morning = sum(int(t.get('morning_teams', 0)) for t in today_teams)
        teams_evening = sum(int(t.get('evening_teams', 0)) for t in today_teams)
        teams_full = sum(int(t.get('full_teams', 0)) for t in today_teams)
        total_teams_today = teams_morning + teams_evening + teams_full
        
        # Get active tasks count
        active_tasks = len(tasks)
        
        # Get last 30 days shifts for chart
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        chart_data = []
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            day_shifts = len([s for s in shifts if s['date'] == date_str])
            chart_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'count': day_shifts
            })
        
        return render_template('dashboard.html',
                             total_employees=total_employees,
                             total_ambulances=total_ambulances,
                             ready_ambulances=ready_ambulances,
                             today_shifts=today_shifts,
                             chart_data=chart_data,
                             total_teams_today=total_teams_today,
                             teams_morning=teams_morning,
                             teams_evening=teams_evening,
                             teams_full=teams_full,
                             active_tasks=active_tasks)
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        flash('حدث خطأ في تحميل لوحة التحكم', 'error')
        return render_template('dashboard.html',
                             total_employees=0,
                             total_ambulances=0,
                             ready_ambulances=0,
                             today_shifts=[],
                             chart_data=[],
                             total_teams_today=0,
                             teams_morning=0,
                             teams_evening=0,
                             teams_full=0,
                             active_tasks=0)

@app.route('/employees')
def employees():
    """Employee management page"""
    try:
        employees_data = data_manager.get_employees()
        return render_template('employees.html', employees=employees_data)
    except Exception as e:
        logging.error(f"Employees page error: {e}")
        flash('حدث خطأ في تحميل بيانات الموظفين', 'error')
        return render_template('employees.html', employees=[])

@app.route('/employees/add', methods=['POST'])
def add_employee():
    """Add new employee"""
    try:
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', '').strip()
        
        if not all([code, name, phone, role]):
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('employees'))
        
        # Check if employee code already exists
        employees = data_manager.get_employees()
        if any(emp['code'] == code for emp in employees):
            flash('رمز الموظف موجود مسبقاً', 'error')
            return redirect(url_for('employees'))
        
        employee = {
            'code': code,
            'name': name,
            'phone': phone,
            'role': role
        }
        
        data_manager.add_employee(employee)
        flash('تم إضافة الموظف بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Add employee error: {e}")
        flash('حدث خطأ في إضافة الموظف', 'error')
    
    return redirect(url_for('employees'))

@app.route('/employees/edit/<code>', methods=['POST'])
def edit_employee(code):
    """Edit existing employee"""
    try:
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', '').strip()
        
        if not all([name, phone, role]):
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('employees'))
        
        employee = {
            'code': code,
            'name': name,
            'phone': phone,
            'role': role
        }
        
        data_manager.update_employee(code, employee)
        flash('تم تحديث بيانات الموظف بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Edit employee error: {e}")
        flash('حدث خطأ في تحديث بيانات الموظف', 'error')
    
    return redirect(url_for('employees'))

@app.route('/employees/delete/<code>', methods=['POST'])
def delete_employee(code):
    """Delete employee"""
    try:
        data_manager.delete_employee(code)
        flash('تم حذف الموظف بنجاح', 'success')
    except Exception as e:
        logging.error(f"Delete employee error: {e}")
        flash('حدث خطأ في حذف الموظف', 'error')
    
    return redirect(url_for('employees'))

@app.route('/employees/export')
def export_employees():
    """Export employees to CSV"""
    try:
        employees = data_manager.get_employees()
        df = pd.DataFrame(employees)
        
        if df.empty:
            flash('لا توجد بيانات للتصدير', 'warning')
            return redirect(url_for('employees'))
        
        # Rename columns to Arabic
        df.columns = ['رمز الموظف', 'الاسم', 'رقم الهاتف', 'الوظيفة']
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=employees_{datetime.now().strftime('%Y%m%d')}.csv"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        logging.error(f"Export employees error: {e}")
        flash('حدث خطأ في تصدير البيانات', 'error')
        return redirect(url_for('employees'))

@app.route('/ambulances')
def ambulances():
    """Ambulance management page"""
    try:
        ambulances_data = data_manager.get_ambulances()
        return render_template('ambulances.html', ambulances=ambulances_data)
    except Exception as e:
        logging.error(f"Ambulances page error: {e}")
        flash('حدث خطأ في تحميل بيانات سيارات الإسعاف', 'error')
        return render_template('ambulances.html', ambulances=[])

@app.route('/ambulances/add', methods=['POST'])
def add_ambulance():
    """Add new ambulance"""
    try:
        plate = request.form.get('plate', '').strip()
        model = request.form.get('model', '').strip()
        status = request.form.get('status', '').strip()
        last_service = request.form.get('last_service', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not all([plate, model, status]):
            flash('الحقول المطلوبة: رقم اللوحة، الطراز، الحالة', 'error')
            return redirect(url_for('ambulances'))
        
        # Check if plate number already exists
        ambulances = data_manager.get_ambulances()
        if any(amb['plate'] == plate for amb in ambulances):
            flash('رقم اللوحة موجود مسبقاً', 'error')
            return redirect(url_for('ambulances'))
        
        ambulance = {
            'plate': plate,
            'model': model,
            'status': status,
            'last_service': last_service or '',
            'notes': notes
        }
        
        data_manager.add_ambulance(ambulance)
        flash('تم إضافة سيارة الإسعاف بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Add ambulance error: {e}")
        flash('حدث خطأ في إضافة سيارة الإسعاف', 'error')
    
    return redirect(url_for('ambulances'))

@app.route('/ambulances/edit/<plate>', methods=['POST'])
def edit_ambulance(plate):
    """Edit existing ambulance"""
    try:
        model = request.form.get('model', '').strip()
        status = request.form.get('status', '').strip()
        last_service = request.form.get('last_service', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not all([model, status]):
            flash('الحقول المطلوبة: الطراز، الحالة', 'error')
            return redirect(url_for('ambulances'))
        
        ambulance = {
            'plate': plate,
            'model': model,
            'status': status,
            'last_service': last_service or '',
            'notes': notes
        }
        
        data_manager.update_ambulance(plate, ambulance)
        flash('تم تحديث بيانات سيارة الإسعاف بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Edit ambulance error: {e}")
        flash('حدث خطأ في تحديث بيانات سيارة الإسعاف', 'error')
    
    return redirect(url_for('ambulances'))

@app.route('/ambulances/delete/<plate>', methods=['POST'])
def delete_ambulance(plate):
    """Delete ambulance"""
    try:
        data_manager.delete_ambulance(plate)
        flash('تم حذف سيارة الإسعاف بنجاح', 'success')
    except Exception as e:
        logging.error(f"Delete ambulance error: {e}")
        flash('حدث خطأ في حذف سيارة الإسعاف', 'error')
    
    return redirect(url_for('ambulances'))

@app.route('/ambulances/export')
def export_ambulances():
    """Export ambulances to CSV"""
    try:
        ambulances = data_manager.get_ambulances()
        df = pd.DataFrame(ambulances)
        
        if df.empty:
            flash('لا توجد بيانات للتصدير', 'warning')
            return redirect(url_for('ambulances'))
        
        # Rename columns to Arabic
        df.columns = ['رقم اللوحة', 'الطراز', 'الحالة', 'تاريخ آخر صيانة', 'ملاحظات']
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=ambulances_{datetime.now().strftime('%Y%m%d')}.csv"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        logging.error(f"Export ambulances error: {e}")
        flash('حدث خطأ في تصدير البيانات', 'error')
        return redirect(url_for('ambulances'))

@app.route('/shifts')
def shifts():
    """Shift management page"""
    try:
        shifts_data = data_manager.get_shifts()
        employees = data_manager.get_employees()
        
        # Filter by month if specified
        month_filter = request.args.get('month', '')
        if month_filter:
            shifts_data = [s for s in shifts_data if s['date'].startswith(month_filter)]
        
        return render_template('shifts.html', shifts=shifts_data, employees=employees, month_filter=month_filter)
    except Exception as e:
        logging.error(f"Shifts page error: {e}")
        flash('حدث خطأ في تحميل بيانات الوردايات', 'error')
        return render_template('shifts.html', shifts=[], employees=[], month_filter='')

@app.route('/shifts/add', methods=['POST'])
def add_shift():
    """Add new shift"""
    try:
        date = request.form.get('date', '').strip()
        period = request.form.get('period', '').strip()
        employee_code = request.form.get('employee_code', '').strip()
        sector = request.form.get('sector', '').strip()
        chief_name = request.form.get('chief_name', '').strip()
        
        if not all([date, period, employee_code, sector]):
            flash('الحقول المطلوبة: التاريخ، الفترة، رمز الموظف، القطاع', 'error')
            return redirect(url_for('shifts'))
        
        # Validate employee exists
        employees = data_manager.get_employees()
        if not any(emp['code'] == employee_code for emp in employees):
            flash('رمز الموظف غير موجود', 'error')
            return redirect(url_for('shifts'))
        
        shift = {
            'date': date,
            'period': period,
            'employee_code': employee_code,
            'sector': sector,
            'chief_name': chief_name
        }
        
        data_manager.add_shift(shift)
        flash('تم إضافة الوردية بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Add shift error: {e}")
        flash('حدث خطأ في إضافة الوردية', 'error')
    
    return redirect(url_for('shifts'))

@app.route('/shifts/edit/<int:shift_id>', methods=['POST'])
def edit_shift(shift_id):
    """Edit existing shift"""
    try:
        date = request.form.get('date', '').strip()
        period = request.form.get('period', '').strip()
        employee_code = request.form.get('employee_code', '').strip()
        sector = request.form.get('sector', '').strip()
        chief_name = request.form.get('chief_name', '').strip()
        
        if not all([date, period, employee_code, sector]):
            flash('الحقول المطلوبة: التاريخ، الفترة، رمز الموظف، القطاع', 'error')
            return redirect(url_for('shifts'))
        
        # Validate employee exists
        employees = data_manager.get_employees()
        if not any(emp['code'] == employee_code for emp in employees):
            flash('رمز الموظف غير موجود', 'error')
            return redirect(url_for('shifts'))
        
        shift = {
            'date': date,
            'period': period,
            'employee_code': employee_code,
            'sector': sector,
            'chief_name': chief_name
        }
        
        data_manager.update_shift(shift_id, shift)
        flash('تم تحديث الوردية بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Edit shift error: {e}")
        flash('حدث خطأ في تحديث الوردية', 'error')
    
    return redirect(url_for('shifts'))

@app.route('/shifts/delete/<int:shift_id>', methods=['POST'])
def delete_shift(shift_id):
    """Delete shift"""
    try:
        data_manager.delete_shift(shift_id)
        flash('تم حذف الوردية بنجاح', 'success')
    except Exception as e:
        logging.error(f"Delete shift error: {e}")
        flash('حدث خطأ في حذف الوردية', 'error')
    
    return redirect(url_for('shifts'))

@app.route('/shifts/export')
def export_shifts():
    """Export shifts to CSV"""
    try:
        shifts = data_manager.get_shifts()
        
        # Filter by month if specified
        month_filter = request.args.get('month', '')
        if month_filter:
            shifts = [s for s in shifts if s['date'].startswith(month_filter)]
        
        df = pd.DataFrame(shifts)
        
        if df.empty:
            flash('لا توجد بيانات للتصدير', 'warning')
            return redirect(url_for('shifts'))
        
        # Rename columns to Arabic
        df.columns = ['التاريخ', 'الفترة', 'رمز الموظف', 'القطاع', 'اسم الرئيس']
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        filename = f"shifts_{month_filter}_{datetime.now().strftime('%Y%m%d')}.csv" if month_filter else f"shifts_{datetime.now().strftime('%Y%m%d')}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        logging.error(f"Export shifts error: {e}")
        flash('حدث خطأ في تصدير البيانات', 'error')
        return redirect(url_for('shifts'))

@app.route('/roster')
def roster():
    """Monthly roster page"""
    try:
        # Get current month or specified month
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        employees = data_manager.get_employees()
        shifts = data_manager.get_shifts()
        
        # Filter shifts for the specified month
        month_shifts = [s for s in shifts if s['date'].startswith(month)]
        
        # Generate days for the month
        year, month_num = month.split('-')
        year, month_num = int(year), int(month_num)
        
        from calendar import monthrange
        _, days_in_month = monthrange(year, month_num)
        days = [f"{year:04d}-{month_num:02d}-{day:02d}" for day in range(1, days_in_month + 1)]
        
        # Create roster data structure
        roster_data = {}
        for emp in employees:
            roster_data[emp['code']] = {
                'name': emp['name'],
                'shifts': {},
                'total_hours': 0
            }
            for day in days:
                roster_data[emp['code']]['shifts'][day] = ''
        
        # Fill in shifts
        for shift in month_shifts:
            emp_code = shift['employee_code']
            date = shift['date']
            period = shift['period']
            
            if emp_code in roster_data and date in roster_data[emp_code]['shifts']:
                roster_data[emp_code]['shifts'][date] = period
                
                # Calculate hours (D=12, N=12, F=24)
                hours = {'D': 12, 'N': 12, 'F': 24}.get(period, 0)
                roster_data[emp_code]['total_hours'] += hours
        
        return render_template('roster.html', 
                             roster_data=roster_data, 
                             days=days, 
                             month=month,
                             employees=employees)
    except Exception as e:
        logging.error(f"Roster page error: {e}")
        flash('حدث خطأ في تحميل جدول المناوبات', 'error')
        return render_template('roster.html', 
                             roster_data={}, 
                             days=[], 
                             month=datetime.now().strftime('%Y-%m'),
                             employees=[])

@app.route('/roster/update', methods=['POST'])
def update_roster():
    """Update roster assignments"""
    try:
        month = request.form.get('month')
        employee_code = request.form.get('employee_code')
        date = request.form.get('date')
        period = request.form.get('period', '').strip()
        
        if not all([month, employee_code, date]):
            flash('بيانات غير مكتملة', 'error')
            return redirect(url_for('roster', month=month))
        
        # Remove existing shift for this employee on this date
        shifts = data_manager.get_shifts()
        existing_shift_id = None
        for i, shift in enumerate(shifts):
            if shift['employee_code'] == employee_code and shift['date'] == date:
                existing_shift_id = i
                break
        
        if period and period != 'O':  # If not off day
            shift_data = {
                'date': date,
                'period': period,
                'employee_code': employee_code,
                'sector': 'عام',  # Default sector
                'chief_name': ''
            }
            
            if existing_shift_id is not None:
                data_manager.update_shift(existing_shift_id, shift_data)
            else:
                data_manager.add_shift(shift_data)
        else:
            # Remove shift if setting to off or empty
            if existing_shift_id is not None:
                data_manager.delete_shift(existing_shift_id)
        
        flash('تم تحديث الجدول بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Update roster error: {e}")
        flash('حدث خطأ في تحديث الجدول', 'error')
    
    return redirect(url_for('roster', month=month))

@app.route('/teams')
def teams():
    """Teams preparation page"""
    try:
        teams_data = data_manager.get_teams()
        # Filter by date if specified
        date_filter = request.args.get('date', '')
        if date_filter:
            teams_data = [t for t in teams_data if t['date'] == date_filter]
        
        return render_template('teams.html', teams=teams_data, date_filter=date_filter)
    except Exception as e:
        logging.error(f"Teams page error: {e}")
        flash('حدث خطأ في تحميل بيانات الفرق', 'error')
        return render_template('teams.html', teams=[], date_filter='')

@app.route('/teams/add', methods=['POST'])
def add_team():
    """Add new team preparation"""
    try:
        date = request.form.get('date', '').strip()
        morning_teams = request.form.get('morning_teams', '0').strip()
        evening_teams = request.form.get('evening_teams', '0').strip()
        full_teams = request.form.get('full_teams', '0').strip()
        notes = request.form.get('notes', '').strip()
        
        if not date:
            flash('التاريخ مطلوب', 'error')
            return redirect(url_for('teams'))
        
        # Check if entry for this date already exists
        teams = data_manager.get_teams()
        existing_team_id = None
        for i, team in enumerate(teams):
            if team['date'] == date:
                existing_team_id = i
                break
        
        team_data = {
            'date': date,
            'morning_teams': morning_teams or '0',
            'evening_teams': evening_teams or '0',
            'full_teams': full_teams or '0',
            'notes': notes
        }
        
        if existing_team_id is not None:
            # Update existing entry
            data_manager.update_team(existing_team_id, team_data)
            flash('تم تحديث بيانات الفرق بنجاح', 'success')
        else:
            # Add new entry
            data_manager.add_team(team_data)
            flash('تم إضافة بيانات الفرق بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Add team error: {e}")
        flash('حدث خطأ في إضافة بيانات الفرق', 'error')
    
    return redirect(url_for('teams'))

@app.route('/teams/edit/<int:team_id>', methods=['POST'])
def edit_team(team_id):
    """Edit existing team preparation"""
    try:
        date = request.form.get('date', '').strip()
        morning_teams = request.form.get('morning_teams', '0').strip()
        evening_teams = request.form.get('evening_teams', '0').strip()
        full_teams = request.form.get('full_teams', '0').strip()
        notes = request.form.get('notes', '').strip()
        
        if not date:
            flash('التاريخ مطلوب', 'error')
            return redirect(url_for('teams'))
        
        team_data = {
            'date': date,
            'morning_teams': morning_teams or '0',
            'evening_teams': evening_teams or '0',
            'full_teams': full_teams or '0',
            'notes': notes
        }
        
        data_manager.update_team(team_id, team_data)
        flash('تم تحديث بيانات الفرق بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Edit team error: {e}")
        flash('حدث خطأ في تحديث بيانات الفرق', 'error')
    
    return redirect(url_for('teams'))

@app.route('/teams/delete/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    """Delete team preparation"""
    try:
        data_manager.delete_team(team_id)
        flash('تم حذف بيانات الفرق بنجاح', 'success')
    except Exception as e:
        logging.error(f"Delete team error: {e}")
        flash('حدث خطأ في حذف بيانات الفرق', 'error')
    
    return redirect(url_for('teams'))

@app.route('/teams/export')
def export_teams():
    """Export teams to CSV"""
    try:
        teams = data_manager.get_teams()
        
        # Filter by date if specified
        date_filter = request.args.get('date', '')
        if date_filter:
            teams = [t for t in teams if t['date'] == date_filter]
        
        df = pd.DataFrame(teams)
        
        if df.empty:
            flash('لا توجد بيانات للتصدير', 'warning')
            return redirect(url_for('teams'))
        
        # Rename columns to Arabic
        df.columns = ['التاريخ', 'فرق الصباح', 'فرق المساء', 'فرق 24 ساعة', 'ملاحظات']
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        filename = f"teams_{date_filter}_{datetime.now().strftime('%Y%m%d')}.csv" if date_filter else f"teams_{datetime.now().strftime('%Y%m%d')}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        logging.error(f"Export teams error: {e}")
        flash('حدث خطأ في تصدير البيانات', 'error')
        return redirect(url_for('teams'))

@app.route('/tasks')
def tasks():
    """Logistics support tasks page"""
    try:
        tasks_data = data_manager.get_tasks()
        employees = data_manager.get_employees()
        
        # Filter by employee or supervisor if specified
        employee_filter = request.args.get('employee', '')
        supervisor_filter = request.args.get('supervisor', '')
        
        if employee_filter:
            tasks_data = [t for t in tasks_data if employee_filter.lower() in t.get('employee_name', '').lower()]
        if supervisor_filter:
            tasks_data = [t for t in tasks_data if supervisor_filter.lower() in t.get('supervisor_name', '').lower()]
        
        return render_template('tasks.html', 
                             tasks=tasks_data, 
                             employees=employees,
                             employee_filter=employee_filter,
                             supervisor_filter=supervisor_filter)
    except Exception as e:
        logging.error(f"Tasks page error: {e}")
        flash('حدث خطأ في تحميل بيانات المهام', 'error')
        return render_template('tasks.html', tasks=[], employees=[], employee_filter='', supervisor_filter='')

@app.route('/tasks/add', methods=['POST'])
def add_task():
    """Add new logistics support task"""
    try:
        employee_name = request.form.get('employee_name', '').strip()
        task_description = request.form.get('task_description', '').strip()
        supervisor_name = request.form.get('supervisor_name', '').strip()
        
        if not all([employee_name, task_description, supervisor_name]):
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('tasks'))
        
        task_data = {
            'employee_name': employee_name,
            'task_description': task_description,
            'supervisor_name': supervisor_name,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        data_manager.add_task(task_data)
        flash('تم إضافة المهمة بنجاح', 'success')
        
    except Exception as e:
        logging.error(f"Add task error: {e}")
        flash('حدث خطأ في إضافة المهمة', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    """Edit existing task"""
    try:
        employee_name = request.form.get('employee_name', '').strip()
        task_description = request.form.get('task_description', '').strip()
        supervisor_name = request.form.get('supervisor_name', '').strip()
        
        if not all([employee_name, task_description, supervisor_name]):
            flash('جميع الحقول مطلوبة', 'error')
            return redirect(url_for('tasks'))
        
        # Get original task to preserve created_at
        tasks = data_manager.get_tasks()
        if task_id < len(tasks):
            original_task = tasks[task_id]
            
            task_data = {
                'employee_name': employee_name,
                'task_description': task_description,
                'supervisor_name': supervisor_name,
                'created_at': original_task.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            data_manager.update_task(task_id, task_data)
            flash('تم تحديث المهمة بنجاح', 'success')
        else:
            flash('المهمة غير موجودة', 'error')
        
    except Exception as e:
        logging.error(f"Edit task error: {e}")
        flash('حدث خطأ في تحديث المهمة', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """Delete task"""
    try:
        data_manager.delete_task(task_id)
        flash('تم حذف المهمة بنجاح', 'success')
    except Exception as e:
        logging.error(f"Delete task error: {e}")
        flash('حدث خطأ في حذف المهمة', 'error')
    
    return redirect(url_for('tasks'))

@app.route('/tasks/export')
def export_tasks():
    """Export tasks to CSV"""
    try:
        tasks = data_manager.get_tasks()
        
        # Filter by employee or supervisor if specified
        employee_filter = request.args.get('employee', '')
        supervisor_filter = request.args.get('supervisor', '')
        
        if employee_filter:
            tasks = [t for t in tasks if employee_filter.lower() in t.get('employee_name', '').lower()]
        if supervisor_filter:
            tasks = [t for t in tasks if supervisor_filter.lower() in t.get('supervisor_name', '').lower()]
        
        df = pd.DataFrame(tasks)
        
        if df.empty:
            flash('لا توجد بيانات للتصدير', 'warning')
            return redirect(url_for('tasks'))
        
        # Rename columns to Arabic
        column_mapping = {
            'employee_name': 'اسم الموظف',
            'task_description': 'وصف المهمة',
            'supervisor_name': 'اسم المشرف',
            'created_at': 'تاريخ الإنشاء',
            'updated_at': 'تاريخ التحديث'
        }
        df = df.rename(columns=column_mapping)
        
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        response = make_response(output.getvalue())
        filters = []
        if employee_filter:
            filters.append(f"employee_{employee_filter}")
        if supervisor_filter:
            filters.append(f"supervisor_{supervisor_filter}")
        
        filename_parts = ["tasks"]
        if filters:
            filename_parts.extend(filters)
        filename_parts.append(datetime.now().strftime('%Y%m%d'))
        filename = "_".join(filename_parts) + ".csv"
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "text/csv; charset=utf-8"
        
        return response
        
    except Exception as e:
        logging.error(f"Export tasks error: {e}")
        flash('حدث خطأ في تصدير البيانات', 'error')
        return redirect(url_for('tasks'))


@app.route('/health')
def health():
    try:
        # simple check: return counts length of current datasets
        employees = data_manager.get_employees()
        ambulances = data_manager.get_ambulances()
        return jsonify({
            "status": "ok",
            "employees": len(employees),
            "ambulances": len(ambulances)
        }), 200
    except Exception as e:
        logging.exception("Health check failed")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
