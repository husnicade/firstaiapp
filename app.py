from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import csv
from io import StringIO
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salary_deduction.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    base_salary = db.Column(db.Float, nullable=False)
    working_days = db.Column(db.Integer, default=22)
    working_hours = db.Column(db.Float, default=8.0)
    absences = db.relationship('Absence', backref='employee', lazy=True)
    
    def calculate_daily_rate(self):
        return self.base_salary / self.working_days
    
    def calculate_hourly_rate(self):
        return self.calculate_daily_rate() / self.working_hours
    
    def calculate_deduction(self, month, year):
        absences = Absence.query.filter_by(
            employee_id=self.id,
            month=month,
            year=year
        ).all()
        
        total_days = sum(absence.days for absence in absences)
        total_hours = sum(absence.hours for absence in absences)
        
        daily_rate = self.calculate_daily_rate()
        hourly_rate = self.calculate_hourly_rate()
        
        deduction = (total_days * daily_rate) + (total_hours * hourly_rate)
        return deduction
    
    def calculate_net_salary(self, month, year):
        deduction = self.calculate_deduction(month, year)
        return self.base_salary - deduction

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    day = db.Column(db.Integer, default=1)  # Added day field
    days = db.Column(db.Integer, default=0)
    hours = db.Column(db.Integer, default=0)
    minutes = db.Column(db.Integer, default=0)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    employees_count = Employee.query.count()
    
    # Get current month and year
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Calculate total absences
    total_days = db.session.query(db.func.sum(Absence.days)).scalar() or 0
    total_hours = db.session.query(db.func.sum(Absence.hours)).scalar() or 0
    total_minutes = db.session.query(db.func.sum(Absence.minutes)).scalar() or 0
    
    # Calculate total deduction and net salary for all employees
    total_deduction = 0
    total_salary = 0
    
    employees = Employee.query.all()
    for employee in employees:
        total_deduction += employee.calculate_deduction(current_month, current_year)
        total_salary += employee.calculate_net_salary(current_month, current_year)
    
    return render_template('dashboard.html', 
                          employees_count=employees_count,
                          total_days=total_days,
                          total_hours=total_hours,
                          total_minutes=total_minutes,
                          total_deduction=total_deduction,
                          total_salary=total_salary)

# Employee Management
@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@app.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        base_salary = float(request.form.get('base_salary'))
        working_days = int(request.form.get('working_days'))
        working_hours = float(request.form.get('working_hours'))
        
        # Check if employee ID already exists
        existing_employee = Employee.query.filter_by(employee_id=employee_id).first()
        if existing_employee:
            flash('Employee ID already exists')
            return redirect(url_for('add_employee'))
        
        new_employee = Employee(
            employee_id=employee_id,
            name=name,
            base_salary=base_salary,
            working_days=working_days,
            working_hours=working_hours
        )
        
        db.session.add(new_employee)
        db.session.commit()
        
        flash('Employee added successfully')
        return redirect(url_for('employees'))
    
    return render_template('add_employee.html')

@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        employee.employee_id = request.form.get('employee_id')
        employee.name = request.form.get('name')
        employee.base_salary = float(request.form.get('base_salary'))
        employee.working_days = int(request.form.get('working_days'))
        employee.working_hours = float(request.form.get('working_hours'))
        
        db.session.commit()
        
        flash('Employee updated successfully')
        return redirect(url_for('employees'))
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/employees/delete/<int:id>')
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    # Delete associated absences
    Absence.query.filter_by(employee_id=employee.id).delete()
    
    db.session.delete(employee)
    db.session.commit()
    
    flash('Employee deleted successfully')
    return redirect(url_for('employees'))

# Absence Management
@app.route('/absences')
@login_required
def absences():
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    day = request.args.get('day', type=int)
    
    # Build query with filters
    query = Absence.query.filter_by(month=month, year=year)
    if day:
        query = query.filter_by(day=day)
    
    absences = query.all()
    employees = Employee.query.all()
    
    return render_template('absences.html', 
                          absences=absences, 
                          employees=employees, 
                          month=month, 
                          year=year,
                          day=day)

@app.route('/absences/add', methods=['GET', 'POST'])
@login_required
def add_absence():
    if request.method == 'POST':
        employee_id = int(request.form.get('employee_id'))
        days = int(request.form.get('days', 0))
        hours = int(request.form.get('hours', 0))
        minutes = int(request.form.get('minutes', 0))
        month = int(request.form.get('month'))
        year = int(request.form.get('year'))
        reason = request.form.get('reason', '')
        
        day = int(request.form.get('day', 1))
        
        new_absence = Absence(
            employee_id=employee_id,
            day=day,
            days=days,
            hours=hours,
            minutes=minutes,
            month=month,
            year=year,
            reason=reason
        )
        
        db.session.add(new_absence)
        db.session.commit()
        
        flash('Absence recorded successfully')
        return redirect(url_for('absences', month=month, year=year))
    
    employees = Employee.query.all()
    now = datetime.now()
    return render_template('add_absence.html', employees=employees, now=now)

@app.route('/absences/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_absence(id):
    from datetime import datetime
    
    absence = Absence.query.get_or_404(id)
    
    if request.method == 'POST':
        absence.employee_id = request.form.get('employee_id')
        absence.day = int(request.form.get('day', 1))
        absence.days = int(request.form.get('days', 0))
        absence.hours = int(request.form.get('hours', 0))
        absence.minutes = int(request.form.get('minutes', 0))
        absence.month = int(request.form.get('month'))
        absence.year = int(request.form.get('year'))
        absence.reason = request.form.get('reason', '')
        
        db.session.commit()
        
        flash('Absence updated successfully!', 'success')
        return redirect(url_for('absences'))
    
    employees = Employee.query.all()
    now = datetime.now()
    return render_template('edit_absence.html', absence=absence, employees=employees, now=now)

@app.route('/absences/delete/<int:id>')
@login_required
def delete_absence(id):
    absence = Absence.query.get_or_404(id)
    month = absence.month
    year = absence.year
    
    db.session.delete(absence)
    db.session.commit()
    
    flash('Absence deleted successfully')
    return redirect(url_for('absences', month=month, year=year))

# Salary Reports
@app.route('/reports')
@login_required
def reports():
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    day = request.args.get('day', type=int)
    
    employees = Employee.query.all()
    salary_data = []
    
    for employee in employees:
        # Build query with filters
        query = Absence.query.filter_by(
            employee_id=employee.id,
            month=month,
            year=year
        )
        if day:
            query = query.filter_by(day=day)
        
        absences = query.all()
        
        total_days = sum(absence.days for absence in absences)
        total_hours = sum(absence.hours for absence in absences)
        
        # For day-specific reports, we need to calculate deductions differently
        if day:
            # Calculate deduction only for the specific day
            daily_rate = employee.calculate_daily_rate()
            hourly_rate = employee.calculate_hourly_rate()
            deduction = (total_days * daily_rate) + (total_hours * hourly_rate)
            # For daily reports, show daily salary instead of monthly
            daily_salary = employee.base_salary / employee.working_days
            net_salary = daily_salary - deduction
        else:
            # Use existing monthly calculation
            deduction = employee.calculate_deduction(month, year)
            net_salary = employee.calculate_net_salary(month, year)
        
        salary_data.append({
            'id': employee.id,
            'employee_id': employee.employee_id,
            'name': employee.name,
            'base_salary': employee.base_salary if not day else employee.base_salary / employee.working_days,
            'absent_days': total_days,
            'absent_hours': total_hours,
            'deduction': deduction,
            'net_salary': net_salary
        })
    
    return render_template('reports.html', salary_data=salary_data, month=month, year=year, day=day)

@app.route('/export/csv')
@login_required
def export_csv():
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    day = request.args.get('day', type=int)
    
    employees = Employee.query.all()
    
    # Create a StringIO object
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Employee ID', 'Name', 'Gross Salary', 'Absent Days', 'Absent Hours', 'Deduction Amount', 'Net Salary'])
    
    # Write data
    for employee in employees:
        # Build query with filters
        query = Absence.query.filter_by(
            employee_id=employee.id,
            month=month,
            year=year
        )
        if day:
            query = query.filter_by(day=day)
        
        absences = query.all()
        
        total_days = sum(absence.days for absence in absences)
        total_hours = sum(absence.hours for absence in absences)
        
        # For day-specific reports, calculate deductions differently
        if day:
            daily_rate = employee.calculate_daily_rate()
            hourly_rate = employee.calculate_hourly_rate()
            deduction = (total_days * daily_rate) + (total_hours * hourly_rate)
            daily_salary = employee.base_salary / employee.working_days
            net_salary = daily_salary - deduction
            gross_salary = daily_salary
        else:
            deduction = employee.calculate_deduction(month, year)
            net_salary = employee.calculate_net_salary(month, year)
            gross_salary = employee.base_salary
        
        writer.writerow([
            employee.employee_id,
            employee.name,
            f"${gross_salary:.2f}",
            total_days,
            total_hours,
            f"${deduction:.2f}",
            f"${net_salary:.2f}"
        ])
    
    # Create response
    output.seek(0)
    month_name = datetime.strptime(str(month), "%m").strftime("%B")
    if day:
        filename = f"Salary_Report_{month_name}_{day}_{year}.csv"
    else:
        filename = f"Salary_Report_{month_name}_{year}.csv"
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    
    return response

# Initialize the database
@app.route('/init_db')
def init_db():
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    return 'Database initialized with admin user (username: admin, password: admin123)'

# Helper functions
def get_month_name(month_number):
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    return months.get(month_number, '')

def get_month_days(month, year, exclude_fridays=True):
    """Generate days of the month excluding Fridays if specified"""
    cal = calendar.monthcalendar(year, month)
    days = []
    
    # In Python's calendar module, weekday 4 is Friday (0 is Monday)
    for week in cal:
        for day in week:
            if day != 0:  # Skip days that are 0 (not part of the month)
                # Check if it's not Friday (weekday 4) or if we're not excluding Fridays
                day_date = datetime(year, month, day)
                if not exclude_fridays or day_date.weekday() != 4:
                    days.append(day)
    
    return days

if __name__ == '__main__':
    with app.app_context():
        # Check if the minutes column exists in the Absence table
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('absence')]
        
        # If minutes column doesn't exist, add it
        if 'minutes' not in columns:
            db.engine.execute('ALTER TABLE absence ADD COLUMN minutes INTEGER DEFAULT 0')
            
        db.create_all()
        # Create admin user if not exists
        if User.query.filter_by(username='admin').first() is None:
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    app.run(debug=True, port=5001)