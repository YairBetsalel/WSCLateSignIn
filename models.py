from flask_sqlalchemy import SQLAlchemy

#regsiter database
db = SQLAlchemy()

#Define database models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)  #Unique Database ID
    student_id = db.Column(db.String(20), unique=True, nullable=False)  #School ID
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    total_late_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Student {self.student_id} - {self.full_name}>"

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)  #Unique Database ID
    teacher_code = db.Column(db.String(50), unique=True, nullable=False)  #Teacher Code
    full_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f"<Teacher {self.teacher_code} - {self.full_name}>"

class LateSignIn(db.Model):
    id = db.Column(db.Integer, primary_key=True) # sign-in unique id
    full_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=False) # student school id
    reason = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    validated = db.Column(db.Boolean, default=False)
    validator = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<LateSignIn {self.id} - {self.full_name}>"