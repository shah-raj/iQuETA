import os, secrets, json ,sys, random, string
from PIL import Image
from flask import *
from flask_app import app, db, bcrypt, mail, google, REDIRECT_URI, currentUserType
from flask_app.forms import *
from flask_app.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from urllib.request import Request, urlopen, URLError
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask_app.objective import ObjectiveTest
from datetime import date, datetime
from sqlalchemy import desc

global_answers=list()
global_questions = list()

@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html',currentUserType = currentUserType)

@app.route("/about")
def about():
    return render_template('about.html', title='About',currentUserType = currentUserType)

@app.route("/ourteam")
def ourteam():
    return render_template('ourteam.html', title='OurTeam',currentUserType = currentUserType)

@app.route("/create_test")
def create_test():
    return render_template('create_test.html', title='Create_test',currentUserType = currentUserType)

@app.route("/register", methods=['GET', 'POST'])
def register():
    userType = session['type']
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        if currentUserType.isStudent():
            user = Student(name=form.name.data, email=form.email.data, password=hashed_password)
        elif currentUserType.isTeacher():
            user = Teacher(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        if currentUserType.isStudent():
            return redirect(url_for('slogin'))
        elif currentUserType.isTeacher():
            return redirect(url_for('tlogin'))
    return render_template('register.html', title='Register', form=form,currentUserType = currentUserType)

@app.route("/slogin")
def slogin():
    session['type'] = 'student'
    return redirect(url_for('login'))

@app.route("/tlogin")
def tlogin():
    session['type'] = 'teacher'
    return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    userType = session['type']
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.google.data:
        access_token = session.get('access_token')
        if access_token is None:
            return redirect(url_for('googleLogin'))

        access_token = access_token[0]

        headers = {'Authorization': 'OAuth '+access_token}
        req = Request('https://www.googleapis.com/oauth2/v1/userinfo',None, headers)
        try:
            res = urlopen(req)
        except URLError as e:
            if e.code == 401:
            # Unauthorized - bad token
                session.pop('access_token', None)
                return redirect(url_for('googleLogin'))
            res.read()
            
        output = res.read().decode('utf-8')
        json_obj = json.loads(output)
        if currentUserType.isStudent():
            user = Student.query.filter_by(email=json_obj['email']).first()
        elif currentUserType.isTeacher():
            user = Teacher.query.filter_by(email=json_obj['email']).first()
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    if form.validate_on_submit():
        if currentUserType.isStudent():
            user = Student.query.filter_by(email=form.email.data).first()
            session['type'] = 'student'
        elif currentUserType.isTeacher():
            user = Teacher.query.filter_by(email=form.email.data).first() 
            session['type'] = 'teacher'
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            user.authenticated = True
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form,currentUserType = currentUserType)



@app.route('/insert', methods = ['POST','GET'])
def insert():
 
    file = request.files["file"]
    session["filepath"] = secure_filename(file.filename)
    file.save(secure_filename(file.filename))

    if request.method=='POST':
        session["subject"] = request.form['subject']
    else:
        session["subject"] = request.args.get['subject']

    codd=''.join(random.choice(string.ascii_uppercase + string.ascii_uppercase + string.digits) for _ in range(8))

    testt=Test(subject=session["subject"],date_created=date.today(),teacher_id=current_user.id,code=codd,status=1,max_score=10)
    db.session.add(testt)
    db.session.commit()
    

    
        # Generate objective test
    objective_generator = ObjectiveTest(session["filepath"])
    question_list, answer_list = objective_generator.generate_test()
    for ans in answer_list:
        global_answers.append(ans)
     
    flash("Test created Successfully")

    return redirect(url_for('dashboard'))
 
 
@app.route('/add_question', methods = ['POST','GET'])
def add_question():
    if request.method=='POST':
        i=request.form['test_id']
        q = request.form['question_text']
        a = request.form['ans']
        o1 = request.form['op1']
        o2 = request.form['op2']
        o3 = request.form['op3']
        o4 = request.form['op4']

        if a==o1 or a==o2 or a==o3 or a==o4:

            res=Questions(question_text=q,test_id=i,ans=a,op1=o1,op2=o2,op3=o3,op4=o4)
            db.session.add(res)
            db.session.commit()
            flash("Question added Successfully")
            return redirect(url_for('viewqns',id=i))
        else:
            flash("Invalid options")
            return redirect(url_for('viewqns',id=i))


@app.route('/up_question/<id>/', methods = ['POST','GET'])
def up_question(id):
    i=request.form['checkboxvalue']
    k=list(map(int,i.split(',')))
    # print(m)
    # for i in m:
    #     if i==',':
    #         m.remove(',')
    #         continue
    # k=[]
    # for i in m:
    #     k.append(int(i))
    print(k)
    allqs=Questions.query.filter_by(test_id=id).with_entities(Questions.id).all()
    tot=[]
    for a in allqs:
        tot.append(a[0])
    final=tot.copy()
    # for i in k:
    #     if i in final:
    #         final.remove(i)
    for i in k:
        my_data = Questions.query.get(i)
        db.session.delete(my_data)
        db.session.commit()

    flash("Questions updated Successfully")
    return redirect(url_for('dashboard'))



@app.route('/update', methods = ['GET', 'POST'])
def update():
 
    if request.method == 'POST':
        my_data = Test.query.get(request.form.get('id'))
 
        my_data.subject = request.form['subject']
        my_data.max_score = request.form['max_score']
        my_data.status = request.form['status']
        if my_data.status=='False':
            my_data.status=0
        if my_data.status=='True':
            my_data.status=1
        else:
            my_data.status=int(my_data.status)
 
        db.session.commit()
        flash("Test Updated Successfully")
 
        return redirect(url_for('dashboard'))
 
 

 
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    firstt=Questions.query.filter_by(test_id=id).all()
    tests = Marks.query.filter_by(test_id=id).all()
    for x in firstt:
        db.session.delete(x)
        db.session.commit()
    for x in tests:
        db.session.delete(x)
        db.session.commit()
    my_data = Test.query.get(id)
    db.session.delete(my_data)
    db.session.commit()


    flash("Test Deleted Successfully")
 
    return redirect(url_for('dashboard'))



@app.route('/viewqns/<id>/', methods = ['GET', 'POST'])
def viewqns(id):
    my_data=Questions.query.filter_by(test_id=id).all()
    return render_template('viewqns.html', title='viewqns',currentUserType = currentUserType,rows=my_data,tid=id)


@app.route('/googleLogin')
def googleLogin():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('home'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')



@app.route("/logout")
def logout():
    logout_user()
    session.pop('type',None)
    return redirect(url_for('home'))


def save_picture(form_picture): #Picture resizing
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form,currentUserType = currentUserType)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        if currentUserType.isStudent():
            user = Student.query.filter_by(email=form.email.data).first()
        elif currentUserType.isTeacher():
            user = Teacher.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form, currentUserType = currentUserType)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if currentUserType.isStudent():
        user = Student.verify_reset_token(token)
    elif currentUserType.isTeacher():
        user = Teacher.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form,currentUserType = currentUserType)

@app.route("/generate_test", methods=["GET", "POST"])
def generate_test():
    file = request.files["file"]
    session["filepath"] = secure_filename(file.filename)
    file.save(secure_filename(file.filename))

    if request.method=='POST':
        session["subject"] = request.form['subject']
    else:
        session["subject"] = request.args.get['subject']

    codd=''.join(random.choice(string.ascii_uppercase + string.ascii_uppercase + string.digits) for _ in range(8))

    testt=Test(subject=session["subject"],date_created=date.today(),teacher_id=current_user.id,code=codd,status=1,max_score=10)
    db.session.add(testt)
    db.session.commit()
    

    
        # Generate objective test
    objective_generator = ObjectiveTest(session["filepath"])
    question_list, answer_list = objective_generator.generate_test()
    for ans in answer_list:
        global_answers.append(ans)
    
    return render_template(
        "objective_test.html",
        testname=session["subject"],
        question1=question_list[0],
        question2=question_list[1],
        question3=question_list[2]
    )
    

@app.route("/test/<int:testId>", methods=['POST', 'GET'])
def test(testId):
    global global_questions
    questions = Questions.query.filter_by(test_id=testId).all()
    t = Test.query.filter_by(id=testId).first()
    teach = Teacher.query.filter_by(id=t.teacher_id).first()
    if request.method == 'GET':
        if len(questions)>t.max_score:
            questions = random.sample(questions,t.max_score)
        random.shuffle(questions)
        global_questions = questions
        m = Marks.query.filter_by(student_id=current_user.id,test_id=testId).first()
        if m:
            return render_template("test.html", data=questions, currentUserType=currentUserType, restricted=True)
        return render_template("test.html", data=questions, currentUserType=currentUserType, restricted=False, teacher=teach, subject = t.subject, duration=t.max_score*10)
    else:
        questions = global_questions
        result = 0
        for q in questions:             
            selected = str(q.id)
            try:
                if request.form[selected] == str(q.ans):
                    result += 1
            except:
                pass
        m = Marks(test_id=testId,student_id=current_user.id, score=result,date_of_attempt=datetime.now())
        db.session.add(m)
        db.session.commit()
        return redirect(url_for("result",testId=testId))

@app.route("/result/<int:testId>", methods=['POST', 'GET'])
def result(testId):
    r = Marks.query.filter_by(test_id=testId,student_id=current_user.id).first()
    t = Test.query.filter_by(id=r.test_id).first()
    prc = (r.score/t.max_score) * 100 
    return render_template('result.html', percentage=prc, subject=t.subject ,currentUserType=currentUserType)

@app.template_filter('shuffle')
def filter_shuffle(seq):
    try:
        result = list(seq)
        random.shuffle(result)
        return result
    except:
        return seq

@app.route("/solution/<int:testId>", methods=['GET'])
def solution(testId):
    r = Marks.query.filter_by(test_id=testId,student_id=current_user.id).first()
    t = Test.query.filter_by(id=r.test_id).first()
    teach = Teacher.query.filter_by(id=t.teacher_id).first()
    prc = (r.score/t.max_score) * 100
    questions = Questions.query.filter_by(test_id=testId).all()
    random.shuffle(questions)
    return render_template('view_test.html', percentage=prc, subject=t.subject ,currentUserType=currentUserType, data=questions, teacher = teach)


@app.route("/dashboard",methods=['POST', 'GET'])
@login_required
def dashboard():
    if currentUserType.isStudent():
        code_form = CodeForm()
        if code_form.validate_on_submit():
            c = code_form.code.data
            t = Test.query.filter_by(code=c).first()
            if t:
                m = Marks.query.filter_by(student_id=current_user.id,test_id=t.id).first()
                if t.status == 0:
                    flash('Enter a valid Test Code', 'error')
                elif m:
                    flash('You have already attempted this test', 'error')
                else:
                    return redirect(url_for("test",testId=t.id))
            else:
                flash('Enter a valid Test Code', 'error')
        elif code_form.code.data:
            flash('Enter a valid Test Code of 8 characters', 'warning')
        dat=Marks.query.filter_by(student_id=current_user.id).order_by(desc(Marks.date_of_attempt)).all()
        res = []
        for row in dat:
            temp = dict()
            tempTest = Test.query.filter_by(id = row.test_id).first()
            tempTeacher = Teacher.query.filter_by(id = tempTest.teacher_id).first()
            temp['subject'] = tempTest.subject
            temp['date'] = row.date_of_attempt
            temp['score'] = row.score
            temp['maxscore'] = tempTest.max_score
            temp['teacher'] = tempTeacher.name
            temp['code'] = tempTest.code
            temp['id'] = row.id
            temp['testId'] = row.test_id
            res.append(temp)
        return render_template('student_dash.html', title='Dashboard', form=code_form ,currentUserType = currentUserType, rows=res)
    elif currentUserType.isTeacher():
        dat=Test.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher_dash.html', title='Dashboard',currentUserType = currentUserType,rows=dat)
    else:
        return redirect(url_for('home'))
