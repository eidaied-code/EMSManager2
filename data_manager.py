import json
import os
import logging
from typing import List, Dict, Any

class DataManager:
    """Manages data persistence using JSON files"""
    
    def __init__(self):
        self.data_dir = 'data'
        self.employees_file = os.path.join(self.data_dir, 'employees.json')
        self.ambulances_file = os.path.join(self.data_dir, 'ambulances.json')
        self.shifts_file = os.path.join(self.data_dir, 'shifts.json')
        self.teams_file = os.path.join(self.data_dir, 'teams.json')
        self.tasks_file = os.path.join(self.data_dir, 'tasks.json')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty data if they don't exist"""
        files = [
            (self.employees_file, []),
            (self.ambulances_file, []),
            (self.shifts_file, []),
            (self.teams_file, []),
            (self.tasks_file, [])
        ]
        
        for file_path, default_data in files:
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logging.error(f"Error initializing {file_path}: {e}")
    
    def _load_json(self, file_path: str) -> List[Dict[Any, Any]]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading {file_path}: {e}")
            return []
    
    def _save_json(self, file_path: str, data: List[Dict[Any, Any]]):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving {file_path}: {e}")
            raise
    
    # Employee management
    def get_employees(self) -> List[Dict[str, str]]:
        """Get all employees"""
        return self._load_json(self.employees_file)
    
    def add_employee(self, employee: Dict[str, str]):
        """Add new employee"""
        employees = self.get_employees()
        employees.append(employee)
        self._save_json(self.employees_file, employees)
    
    def update_employee(self, code: str, employee: Dict[str, str]):
        """Update existing employee"""
        employees = self.get_employees()
        for i, emp in enumerate(employees):
            if emp['code'] == code:
                employees[i] = employee
                break
        self._save_json(self.employees_file, employees)
    
    def delete_employee(self, code: str):
        """Delete employee"""
        employees = self.get_employees()
        employees = [emp for emp in employees if emp['code'] != code]
        self._save_json(self.employees_file, employees)
    
    # Ambulance management
    def get_ambulances(self) -> List[Dict[str, str]]:
        """Get all ambulances"""
        return self._load_json(self.ambulances_file)
    
    def add_ambulance(self, ambulance: Dict[str, str]):
        """Add new ambulance"""
        ambulances = self.get_ambulances()
        ambulances.append(ambulance)
        self._save_json(self.ambulances_file, ambulances)
    
    def update_ambulance(self, plate: str, ambulance: Dict[str, str]):
        """Update existing ambulance"""
        ambulances = self.get_ambulances()
        for i, amb in enumerate(ambulances):
            if amb['plate'] == plate:
                ambulances[i] = ambulance
                break
        self._save_json(self.ambulances_file, ambulances)
    
    def delete_ambulance(self, plate: str):
        """Delete ambulance"""
        ambulances = self.get_ambulances()
        ambulances = [amb for amb in ambulances if amb['plate'] != plate]
        self._save_json(self.ambulances_file, ambulances)
    
    # Shift management
    def get_shifts(self) -> List[Dict[str, str]]:
        """Get all shifts"""
        return self._load_json(self.shifts_file)
    
    def add_shift(self, shift: Dict[str, str]):
        """Add new shift"""
        shifts = self.get_shifts()
        shifts.append(shift)
        self._save_json(self.shifts_file, shifts)
    
    def update_shift(self, shift_id: int, shift: Dict[str, str]):
        """Update existing shift"""
        shifts = self.get_shifts()
        if 0 <= shift_id < len(shifts):
            shifts[shift_id] = shift
            self._save_json(self.shifts_file, shifts)
    
    def delete_shift(self, shift_id: int):
        """Delete shift"""
        shifts = self.get_shifts()
        if 0 <= shift_id < len(shifts):
            shifts.pop(shift_id)
            self._save_json(self.shifts_file, shifts)
    
    # Teams management
    def get_teams(self) -> List[Dict[str, str]]:
        """Get all team preparations"""
        return self._load_json(self.teams_file)
    
    def add_team(self, team: Dict[str, str]):
        """Add new team preparation"""
        teams = self.get_teams()
        teams.append(team)
        self._save_json(self.teams_file, teams)
    
    def update_team(self, team_id: int, team: Dict[str, str]):
        """Update existing team preparation"""
        teams = self.get_teams()
        if 0 <= team_id < len(teams):
            teams[team_id] = team
            self._save_json(self.teams_file, teams)
    
    def delete_team(self, team_id: int):
        """Delete team preparation"""
        teams = self.get_teams()
        if 0 <= team_id < len(teams):
            teams.pop(team_id)
            self._save_json(self.teams_file, teams)
    
    # Tasks management
    def get_tasks(self) -> List[Dict[str, str]]:
        """Get all logistics support tasks"""
        return self._load_json(self.tasks_file)
    
    def add_task(self, task: Dict[str, str]):
        """Add new logistics support task"""
        tasks = self.get_tasks()
        tasks.append(task)
        self._save_json(self.tasks_file, tasks)
    
    def update_task(self, task_id: int, task: Dict[str, str]):
        """Update existing task"""
        tasks = self.get_tasks()
        if 0 <= task_id < len(tasks):
            tasks[task_id] = task
            self._save_json(self.tasks_file, tasks)
    
    def delete_task(self, task_id: int):
        """Delete task"""
        tasks = self.get_tasks()
        if 0 <= task_id < len(tasks):
            tasks.pop(task_id)
            self._save_json(self.tasks_file, tasks)
