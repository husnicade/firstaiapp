# Salary Deduction Management System

A modern, web-based application for managing employee salaries and tracking absences with automatic deduction calculations.

## 🚀 Features

- **Employee Management**: Add, edit, and manage employee information
- **Absence Tracking**: Record and track employee absences by day, hours, and minutes
- **Automatic Calculations**: Calculate salary deductions based on absences
- **Modern UI**: Beautiful, responsive design with glass morphism effects
- **Reports & Export**: Generate detailed salary reports and export to CSV
- **Secure Authentication**: User login system with password visibility toggle

## 🎨 Modern Design Features

- **Glass Morphism**: Semi-transparent elements with backdrop blur effects
- **Gradient Backgrounds**: Beautiful color gradients throughout the interface
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Smooth Animations**: Subtle hover effects and transitions
- **Modern Typography**: Clean, professional font choices

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login
- **Icons**: Font Awesome

## 📋 Requirements

- Python 3.7+
- Flask 2.0.1
- Flask-SQLAlchemy 2.5.1
- Flask-Login 0.5.0
- Werkzeug 2.0.1

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/husnicade/firstaiapp.git
   cd firstaiapp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5001`
   - Default login credentials:
     - Username: `admin`
     - Password: `admin123`

## 📱 Usage

### Dashboard
- View total employees, absences, and financial summary
- Quick access to common actions

### Employee Management
- Add new employees with salary and working hours information
- Edit existing employee details
- Delete employees (with associated absence records)

### Absence Tracking
- Record employee absences by day, hours, and minutes
- Filter absences by day, month, and year
- Edit or delete absence records

### Reports
- Generate detailed salary reports
- Filter reports by day, month, and year
- Export reports to CSV format

## 🎯 Key Features

### Decimal Working Hours
- Support for decimal working hours (e.g., 7.5 hours per day)
- Accurate daily and hourly rate calculations

### Advanced Filtering
- Filter absences and reports by specific day, month, and year
- Flexible date range selection

### Modern Authentication
- Secure login system
- Password visibility toggle
- Session management

### Responsive Design
- Mobile-friendly interface
- Consistent design across all pages
- Modern glass morphism effects

## 🔧 Configuration

The application uses SQLite database by default. The database file (`salary_deduction.db`) will be created automatically on first run.

### Database Initialization
Visit `/init_db` to initialize the database and create the default admin user.

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password

### Employees Table
- `id`: Primary key
- `employee_id`: Unique employee identifier
- `name`: Employee name
- `base_salary`: Monthly base salary
- `working_days`: Working days per month (default: 22)
- `working_hours`: Working hours per day (supports decimals)

### Absences Table
- `id`: Primary key
- `employee_id`: Foreign key to employees
- `day`: Day of the month
- `days`: Number of days absent
- `hours`: Number of hours absent
- `minutes`: Number of minutes absent
- `month`: Month of absence
- `year`: Year of absence
- `reason`: Reason for absence
- `date_recorded`: When the absence was recorded

## 🎨 Design System

The application uses a consistent design system with:

- **Color Palette**: Purple-blue gradients with glass morphism effects
- **Typography**: Modern font stack with gradient text effects
- **Components**: Consistent button styles, form controls, and cards
- **Animations**: Smooth transitions and hover effects

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- CSRF protection
- Input validation and sanitization

## 📈 Future Enhancements

- [ ] User role management
- [ ] Email notifications
- [ ] Advanced reporting with charts
- [ ] Bulk import/export functionality
- [ ] API endpoints for mobile apps
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

**Eng. Hussein**
- Contact: 614323260
- GitHub: [@husnicade](https://github.com/husnicade)

---

Made with ❤️ using Flask and modern web technologies.
