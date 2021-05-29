# from datetime import datetime
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask_app import db, login_manager, app, currentUserType
# from flask_login import UserMixin, current_user
#
# @login_manager.user_loader
# def load_user(user_id):
#     if currentUserType.isTeacher():
#         return Teacher.query.get(int(user_id))
#     else:
#         return Student.query.get(int(user_id))
#
#
# class Teacher(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     password = db.Column(db.String(60), nullable=False)
#     tests = db.relationship('Test', backref='teacher', lazy=True)
#
#     def get_reset_token(self, expires_sec=1800):
#         s = Serializer(app.config['SECRET_KEY'], expires_sec)
#         return s.dumps({'user_id': self.id}).decode('utf-8')
#
#     @staticmethod
#     def verify_reset_token(token):
#         s = Serializer(app.config['SECRET_KEY'])
#         try:
#             user_id = s.loads(token)['user_id']
#         except:
#             return None
#         return Teacher.query.get(user_id)
#
#     def __repr__(self):
#         return f"Teacher('{self.name}', '{self.email}')"
#
# class Student(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
#     password = db.Column(db.String(60), nullable=False)
#     marks = db.relationship('Marks', backref='student', lazy=True)
#
#     def get_reset_token(self, expires_sec=1800):
#         s = Serializer(app.config['SECRET_KEY'], expires_sec)
#         return s.dumps({'user_id': self.id}).decode('utf-8')
#
#     @staticmethod
#     def verify_reset_token(token):
#         s = Serializer(app.config['SECRET_KEY'])
#         try:
#             user_id = s.loads(token)['user_id']
#         except:
#             return None
#         return Student.query.get(user_id)
#
#     def __repr__(self):
#         return f"Student('{self.name}', '{self.email}')"
#
#
# class Test(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     subject = db.Column(db.String(100), nullable=False)
#     date_created = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#     teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
#     code = db.Column(db.String(8),nullable = False)
#     status = db.Column(db.Boolean,nullable = False)
#     questions = db.relationship('Questions', backref='test', lazy=True)
#     max_score = db.Column(db.Integer)
#     date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     # marks = db.relationship('Marks', backref='test', lazy=True)
#     def __repr__(self):
#         return f"Test('{self.subject}' - '{self.date_created}')"
#
# class Questions(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     question_text = db.Column(db.String(200), nullable=False)
#     test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
#     ans = db.Column(db.String(200),nullable=False)
#     op1 = db.Column(db.String(200))
#     op2 = db.Column(db.String(200))
#     op3 = db.Column(db.String(200))
#     # op4 = db.Column(db.String(200))
#     def __repr__(self):
#         return f"Question('{self.question_text}' - '{self.ans}')"
#
# class Marks(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
#     score = db.Column(db.Integer,nullable=False)
#     date_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     def __repr__(self):
#         return f"Marks('{self.student_id}' - '{self.test_id}' = '{self.score}')"
#
# class Answers(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     marks_id = db.Column(db.Integer, db.ForeignKey('marks.id'), nullable=False)
#     q_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
#     student_ans = db.Column(db.String(200),nullable=False)
#     right_ans = db.Column(db.Boolean,nullable = False)
#     def __repr__(self):
#         return f"Answers('{self.makrs_id}' - '{self.q_id}' - '{self.right_ans}')"
