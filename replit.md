# Overview

This is an Arabic RTL (Right-to-Left) management system called "تحضير قطاع الجموم" built with Flask. The application manages ambulances, employees, and shift schedules for medical emergency services. It features a comprehensive dashboard with statistics, employee management, ambulance tracking, and monthly roster scheduling. The system is designed specifically for Arabic-speaking medical organizations with full RTL support and Arabic UI text.

# User Preferences

Preferred communication style: Simple, everyday language.
Design preferences: Professional modern design with sky blue colors, Arabic fonts (Cairo/Tajawal), rounded corners, subtle shadows, responsive design for mobile/tablet.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 RTL for Arabic language support
- **UI Framework**: Bootstrap 5 RTL with Font Awesome icons for consistent Arabic interface
- **Typography**: Cairo Arabic font from Google Fonts for professional appearance
- **Design System**: Modern professional design with sky blue color scheme, rounded corners, and subtle shadows
- **Client-Side**: Vanilla JavaScript with Chart.js for data visualization and smooth animations
- **Responsive Design**: Mobile-first approach with RTL-specific CSS customizations and tablet support

## Backend Architecture
- **Web Framework**: Flask with Python for lightweight web application development
- **Route Structure**: RESTful endpoints for CRUD operations on employees, ambulances, shifts, teams, and tasks
- **Data Layer**: Custom DataManager class for JSON-based data persistence
- **Session Management**: Flask sessions with configurable secret key

## Data Storage
- **Primary Storage**: JSON files for simple deployment without database dependencies
- **File Structure**: Separate JSON files for employees, ambulances, shifts, teams, and tasks
- **Data Directory**: Organized data folder with automatic initialization
- **Export Functionality**: CSV export capabilities using pandas for all data types

## Key Features
- **Dashboard**: Real-time statistics with live clock, 30-day shift trend visualization, and teams summary with animated cards
- **Employee Management**: Full CRUD operations with role-based categorization and modern form design
- **Ambulance Management**: Vehicle tracking with status monitoring and maintenance records
- **Roster Management**: Monthly shift scheduling with visual calendar interface
- **Teams Management**: Daily team preparation tracking with morning/evening/24-hour shifts and enhanced filtering
- **Logistics Support Tasks**: Employee task management with supervisor tracking and timestamp records
- **Modern UI/UX**: Professional design with Cairo Arabic font, sky blue colors, rounded corners, shadows, and smooth animations
- **Multi-language Support**: Arabic RTL interface with proper text direction handling

## Design Patterns
- **MVC Pattern**: Clear separation between data (DataManager), views (templates), and controllers (Flask routes)
- **Single Responsibility**: DataManager handles all data operations independently
- **Configuration Management**: Environment-based configuration for deployment flexibility

# External Dependencies

## Core Dependencies
- **Flask**: Web framework for HTTP handling and template rendering
- **pandas**: Data manipulation and CSV export functionality
- **logging**: Built-in Python logging for debugging and monitoring

## Frontend Libraries
- **Bootstrap 5 RTL**: UI framework specifically for right-to-left languages
- **Font Awesome 6.0**: Icon library for consistent visual elements
- **Chart.js**: JavaScript charting library for dashboard analytics with enhanced styling
- **Google Fonts (Cairo)**: Professional Arabic typography for improved readability
- **Custom CSS**: Modern design system with animations, gradients, and responsive layouts

## Runtime Environment
- **Python Runtime**: Requires Python 3.x environment
- **File System**: Local file system access for JSON data persistence
- **Port Configuration**: Configurable port binding (default 5000)

## Recent Updates (August 2025)
- **Complete UI Redesign**: Implemented modern professional design with sky blue color scheme
- **Typography Enhancement**: Added Cairo Arabic font from Google Fonts for better readability
- **Responsive Improvements**: Enhanced mobile and tablet support with flexible layouts
- **Animation System**: Added smooth fade-in and slide-in animations for better user experience
- **Component Styling**: Updated all cards, buttons, forms, and tables with rounded corners and shadows
- **Dashboard Enhancement**: Added real-time clock, improved statistics cards, and enhanced chart styling

## Optional Enhancements
The system is designed to potentially integrate with:
- **Database Systems**: Can be extended to use PostgreSQL or other databases
- **Authentication Systems**: Ready for user authentication implementation
- **External APIs**: Extensible for third-party medical service integrations