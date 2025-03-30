from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Student, Teacher, LateSignIn
from datetime import datetime, timedelta

admin_r = Blueprint('admin', __name__, url_prefix='/admin1022')

@admin_r.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #CHANGE ADMIN USERNAME AND PASSWORD HERE
        if request.form['username'] == 'admin1022' and request.form['password'] == 'WSCLateSignInAdmin10221022':
            session['admin_logged_in'] = True
            return redirect(url_for('admin.panel'))
        return render_template('admin_login.html', message="Invalid username or password")
    return render_template('admin_login.html')

@admin_r.route('/')
def panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    return render_template('admin_panel.html')

@admin_r.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_r.route('/students')
def students():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    page = request.args.get('page', 1, type=int)
    students = Student.query.order_by(Student.student_id.desc()).paginate(page=page, per_page=30)
    return render_template('admin_students.html', students=students)

@admin_r.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        student = Student(
            student_id=request.form['student_id'],
            full_name=request.form['full_name'],
            email=request.form['email']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('admin.students'))
    return render_template('admin_add_student.html')

@admin_r.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.student_id = request.form['student_id']
        student.full_name = request.form['full_name']
        student.email = request.form['email']
        student.total_late_count = int(request.form.get('total_late_count', 0))
        db.session.commit()
        return redirect(url_for('admin.students'))
    return render_template('admin_edit_student.html', student=student)

@admin_r.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('admin.students'))

@admin_r.route('/teachers')
def teachers():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    page = request.args.get('page', 1, type=int)
    per_page = 15
    teachers = Teacher.query.order_by(Teacher.id.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin_teachers.html', teachers=teachers)

@admin_r.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        teacher = Teacher(
            full_name=request.form['full_name'],
            teacher_code=request.form['teacher_code'],
            password=request.form['password'],
            email=request.form['email']
        )
        db.session.add(teacher)
        db.session.commit()
        return redirect(url_for('admin.teachers'))
    return render_template('admin_add_teacher.html')

@admin_r.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    return redirect(url_for('admin.teachers'))

@admin_r.route('/teachers/edit/<int:teacher_id>', methods=['GET', 'POST'])
def edit_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    teacher = Teacher.query.get_or_404(teacher_id)
    if request.method == 'POST':
        teacher.full_name = request.form['full_name']
        teacher.teacher_code = request.form['teacher_code']
        teacher.email = request.form['email']
        if request.form['password']:
            teacher.password = request.form['password']
        db.session.commit()
        return redirect(url_for('admin.teachers'))
    return render_template('admin_edit_teacher.html', teacher=teacher)
    
@admin_r.route('/signins')
def signins():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    page = request.args.get('page', 1, type=int)
    per_page = 15
    entries = LateSignIn.query.order_by(LateSignIn.time.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin_signins.html', entries=entries)

@admin_r.route('/signins/add', methods=['GET', 'POST'])
def add_signin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        entry = LateSignIn(
            full_name=request.form['full_name'],
            student_id=request.form['student_id'],
            reason=request.form['reason'],
            time=datetime.strptime(request.form['time'], "%Y-%m-%d %H:%M"),
            validated=request.form.get('validated') == 'on'
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('admin.signins'))
    return render_template('admin_add_signin.html')

@admin_r.route('/signins/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_signin(entry_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    entry = LateSignIn.query.get_or_404(entry_id)
    if request.method == 'POST':
        entry.full_name = request.form['full_name']
        entry.student_id = request.form['student_id']
        entry.reason = request.form['reason']
        try:
             entry.time = datetime.strptime(request.form['time'], "%Y-%m-%d %H:%M")
        except ValueError:
             message = "Invalid date/time format. Please use YYYY-MM-DD HH:MM"
             return render_template('admin_edit_signin.html', entry=entry, message=message)
        entry.validated = request.form.get('validated') == 'on'
        db.session.commit()
        return redirect(url_for('admin.signins'))
    return render_template('admin_edit_signin.html', entry=entry)

@admin_r.route('/signins/delete/<int:entry_id>', methods=['POST'])
def delete_signin(entry_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    entry = LateSignIn.query.get_or_404(entry_id)
    db.session.delete(entry)