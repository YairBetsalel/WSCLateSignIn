from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from pytz import timezone
from datetime import datetime, timedelta
import ssl
from models import db, Student, Teacher, LateSignIn
#import admin part
from admin_route import admin_r

app = Flask(__name__)



#session security
app.secret_key = os.urandom(24)
#session time: 7 days
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

#Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///latesignininfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialise database and admin blueprint
db.init_app(app)
app.register_blueprint(admin_r)

# Late Sign In Page Request
@app.route('/', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        full_name = request.form['full_name']
        reason = request.form['reason']
        selected_student_id = request.form.get('selected_student_id')

        # Find matching students
        matches = Student.query.filter(Student.full_name.ilike(f"%{full_name}%")).all()

        # Not allowed to proceed if no matching name
        if not matches:
            message = "No matching name found"
            return render_template('late_signin.html', message=message)
        elif len(matches) == 1 or selected_student_id:
            # If selected, or only one match, proceed
            student = None
            if selected_student_id:
                student = Student.query.filter_by(student_id=selected_student_id).first()
            else:
                student = matches[0]

            #Get NZ time
            nz_time = datetime.now(timezone('Pacific/Auckland'))
            entry = LateSignIn(
                full_name=student.full_name,
                student_id=student.student_id,
                reason=reason,
                time=nz_time
            )
            db.session.add(entry)
            student.total_late_count += 1
            db.session.commit()
            session['last_signed_in_id'] = entry.id
            return redirect(url_for('signin_info', entry_id=entry.id))
        else:
            # Multiple matches and no student ID selected
            message = "Multiple students found. Please select your student ID to proceed."
            return render_template('confirm_id.html', matches=matches, full_name=full_name, reason=reason, message=message)

    return render_template('late_signin.html')

#sign in detail
@app.route('/signin/<int:entry_id>', methods=['GET', 'POST'])
def signin_info(entry_id):
    entry = LateSignIn.query.get_or_404(entry_id)
    # Check if the student just signed in
    if session.get('last_signed_in_id') == entry_id:
        # Clear session
        session.pop('last_signed_in_id', None)
        return render_template(
            'signin.html',
            full_name=entry.full_name,
            reason=entry.reason,
            signin_id=entry.id,
            time=entry.time.strftime("%Y-%m-%d %H:%M %Z"),
            validated_status = entry.validated,
            message="You have signed in successfully. You may take a screenshot to save the detail, or view this page again via this link."
        )
    # Not from a sign-in - verify identity
    if request.method == 'POST':
        name_input = request.form.get('full_name', '').strip().lower()
        if name_input == entry.full_name.lower():
            return render_template(
                'signin.html',
                full_name=entry.full_name,
                reason=entry.reason,
                signin_id=entry.id,
                validated_status = entry.validated,
                time=entry.time.strftime("%Y-%m-%d %H:%M %Z"),
            )
        else:
            message = "Name does not match. Please try again."
            return render_template('verify_name.html', message=message)
    message = "Identity verification is needed. Access will be granted if the name entered matches the sign-in detail."
    return render_template('verify_name.html', message = message)


#Auto Search
@app.route('/search-students')
def search_students():
    query = request.args.get('q', '')
    results = Student.query.filter(Student.full_name.ilike(f"%{query}%")).all()
    return jsonify([{"full_name": s.full_name, "student_id": s.student_id} for s in results])


# Teacher login
@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        code = request.form.get('teacher_code')
        password = request.form.get('password')
        #Verify Teacher Code and Password
        teacher = Teacher.query.filter_by(teacher_code=code, password=password).first()

        if teacher:
            session['teacher_logged_in'] = True
            session['teacher_name'] = teacher.full_name
            session['teacher_code'] = teacher.teacher_code
            session.permanent = True  # session lasts 7 days
            return redirect(url_for('teacher_panel'))
        else:
            message = "Invalid Teacher Code or Password"
            return render_template('teacher_login.html', message=message)
    
    return render_template('teacher_login.html')

#teacher log out
@app.route('/teacher/logout')
def teacher_logout():
    session.clear()
    return redirect(url_for('teacher_login'))

# teache panel
@app.route('/teacher', methods=['GET'])
def teacher_panel():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))

    page = request.args.get('page', 1, type=int)
    per_page = 15
    late_signins = LateSignIn.query.order_by(LateSignIn.id.desc()).paginate(page=page, per_page=per_page)

    return render_template('teacher_panel.html', full_name=session.get('teacher_name'), late_signins=late_signins)

# teacher panel - search by name or Signin
@app.route('/teacher/search')
def teacher_search():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))

    query = request.args.get('q', '').strip()
    results = []

    if query.isdigit():
        result = LateSignIn.query.filter_by(id=int(query)).all()
    else:
        result = LateSignIn.query.filter(LateSignIn.full_name.ilike(f"%{query}%")).all()
    
    return render_template('teacher_search_results.html', results=result)

# teacher panel - see detail
@app.route('/teacher/detail/<int:signin_id>', methods=['GET', 'POST'])
def teacher_detail(signin_id):
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))

    entry = LateSignIn.query.get_or_404(signin_id)
    student = Student.query.filter_by(student_id=entry.student_id).first()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'validate':
            entry.validated = True
            entry.validator = session['teacher_name']
        elif action == 'validate with updated time':
            entry.validated = True
            #update sign-in time
            nz_time = datetime.now(timezone('Pacific/Auckland'))
            entry.time = nz_time
            entry.validator = session['teacher_name']
        elif action == 'invalidate':
            entry.validated = False
            entry.validator = session['teacher_name']
        db.session.commit()
    
    return render_template('teacher_detail.html', entry=entry, student=student)


#password change for teachers
@app.route('/teacher/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('teacher_logged_in'):
        return redirect(url_for('teacher_login'))

    teacher = Teacher.query.filter_by(teacher_code=session['teacher_code']).first()

    if request.method == 'POST':
        old_pass = request.form.get('old_password')
        new_pass = request.form.get('new_password')

        if teacher and teacher.password == old_pass:
            teacher.password = new_pass
            db.session.commit()
            return redirect(url_for('teacher_logout'))
        else:
            message = "Old password is incorrect"

        return render_template('change_password.html', message=message)
    
    return render_template('change_password.html')


if __name__ == '__main__':    
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("server.crt", "server.key")  
    #Create database file
    with app.app_context():
        db.create_all()
    # Run app with HTTPS on port 5500
    app.run(host='127.0.0.1', port=5500, debug=True, ssl_context=context)


