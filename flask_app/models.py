from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_app import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    try:
        return Teacher.query.get(int(user_id))
    except:
        return Student.query.get(int(user_id))


class Teacher(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    tests = db.relationship('Test', backref='teacher', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Teacher.query.get(user_id)

    def __repr__(self):
        return f"Teacher('{self.name}', '{self.email}')"

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    marks = db.relationship('Marks', backref='student', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Student.query.get(user_id)

    def __repr__(self):
        return f"Student('{self.name}', '{self.email}')"


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    code = db.Column(db.String(8),nullable = False)
    status = db.Column(db.Boolean,nullable = False)
    questions = db.relationship('Questions', backref='test', lazy=True)
    max_score = db.Column(db.Integer)
    marks = db.relationship('Marks', backref='test', lazy=True)
    def __repr__(self):
        return f"Test('{self.subject}' - '{self.date_created}')"

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(200), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    ans = db.Column(db.String(200),nullable=False)
    op1 = db.Column(db.String(200))
    op2 = db.Column(db.String(200))
    op3 = db.Column(db.String(200))
    op4 = db.Column(db.String(200))
    def __repr__(self):
        return f"Question('{self.question_text}' - '{self.ans}')"

class Marks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    score = db.Column(db.Integer,nullable=False)
    date_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return f"Question('{self.student_id}' - '{self.test_id}' - '{self.score}')"

# db.create_all()
# t1 = Teacher(username="ran",name="Rohini Nair",email="ran@somaiya.edu",password="password")
# db.session.add(t1)
# db.session.commiit()