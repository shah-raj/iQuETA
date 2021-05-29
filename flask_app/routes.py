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

@app.route("/faq")
def faq():
    return render_template('faqs.html', title='FAQ',currentUserType = currentUserType)

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
    # if form.google.data:
    #     access_token = session.get('access_token')
    #     if access_token is None:
    #         return redirect(url_for('googleLogin'))
    #
    #     access_token = access_token[0]
    #
    #     headers = {'Authorization': 'OAuth '+access_token}
    #     req = Request('https://www.googleapis.com/oauth2/v1/userinfo',None, headers)
    #     try:
    #         res = urlopen(req)
    #     except URLError as e:
    #         if e.code == 401:
    #         # Unauthorized - bad token
    #             session.pop('access_token', None)
    #             return redirect(url_for('googleLogin'))
    #         res.read()
    #
    #     output = res.read().decode('utf-8')
    #     json_obj = json.loads(output)
    #     if currentUserType.isStudent():
    #         user = Student.query.filter_by(email=json_obj['email']).first()
    #     elif currentUserType.isTeacher():
    #         user = Teacher.query.filter_by(email=json_obj['email']).first()
    #     login_user(user, remember=form.remember.data)
    #     next_page = request.args.get('next')
    #     return redirect(next_page) if next_page else redirect(url_for('dashboard'))

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
    # print(session['filepath'])
    if session["filepath"][-3:] != 'pdf'  and session["filepath"][-3:] != 'txt':
        flash("Invalid file format!")
    else:
        objective_generator = ObjectiveTest(session["filepath"])
        question_list, answer_list, mcq_list = objective_generator.generate_test()
        testt=Test(subject=session["subject"],teacher_id=current_user.id,code=codd,status=0,tot_questions=request.form['tot_questions'],tot_time = request.form['tot_time'])
        db.session.add(testt)
        db.session.commit()
        # for ans in answer_list:
        #     global_answers.append(ans)
        for (q,a,m) in zip(question_list,answer_list,mcq_list):
            if '' in m:
                continue
            q_data = Questions(question_text=q,test_id=testt.id,ans=a,op1=m[0],op2=m[1],op3=m[2])
            db.session.add(q_data)
        db.session.commit()
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


        q_new = Questions(question_text=q,test_id=i,ans=a,op1=o1,op2=o2,op3=o3)
        db.session.add(q_new)
        db.session.commit()
        flash("Question added Successfully")
        return redirect(url_for('viewqns',id=i))



@app.route('/up_question/<id>/', methods = ['POST','GET'])
def up_question(id):
    i=request.form['checkboxvalue']
    k=list(map(int,i.split(',')))
    # print(k)
    allq = Questions.query.filter_by(test_id=id).all()
    for a in allq:
        if a.id in k:
            continue
        db.session.delete(a)
    db.session.commit()

    flash("Questions updated Successfully")
    return redirect(url_for('dashboard'))



@app.route('/update', methods = ['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = Test.query.get(request.form.get('id'))

        my_data.subject = request.form['subject']
        my_data.tot_time = request.form['tot_time']

        q = Questions.query.filter_by(test_id=my_data.id).all()
        if int(request.form['tot_questions'])<=len(q):
            my_data.tot_questions = request.form['tot_questions']
            if request.form['status']=='False':
                my_data.status=0
            elif request.form['status']=='True':
                my_data.status=1
            else:
                my_data.status=int(my_data.status)
            db.session.commit()
            flash("Test Updated Successfully")
        else:
            flash(f'This test has only {len(q)} generated questions')



        return redirect(url_for('dashboard'))




@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    firstt=Questions.query.filter_by(test_id=id).all()
    tests = Marks.query.filter_by(test_id=id).all()
    for x in firstt:
        anss = Answers.query.filter_by(q_id=x.id).all()
        for a in anss:
            db.session.delete(a)
        db.session.commit()
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

# @app.route("/generate_test", methods=["GET", "POST"])
# def generate_test():
#     file = request.files["file"]
#     session["filepath"] = secure_filename(file.filename)
#     file.save(secure_filename(file.filename))
#
#     if request.method=='POST':
#         session["subject"] = request.form['subject']
#     else:
#         session["subject"] = request.args.get['subject']
#
#     codd=''.join(random.choice(string.ascii_uppercase + string.ascii_uppercase + string.digits) for _ in range(8))
#
#     testt=Test(subject=session["subject"],date_created=date.today(),teacher_id=current_user.id,code=codd,status=1,max_score=10)
#     db.session.add(testt)
#     db.session.commit()
#
#
#
#         # Generate objective test
#     objective_generator = ObjectiveTest(session["filepath"])
#     question_list, answer_list = objective_generator.generate_test()
#     for ans in answer_list:
#         global_answers.append(ans)
#
#     return render_template(
#         "objective_test.html",
#         testname=session["subject"],
#         question1=question_list[0],
#         question2=question_list[1],
#         question3=question_list[2]
#     )


@app.route("/test/<int:testId>", methods=['POST', 'GET'])
def test(testId):
    global global_questions
    questions = Questions.query.filter_by(test_id=testId).all()
    t = Test.query.filter_by(id=testId).first()
    teach = Teacher.query.filter_by(id=t.teacher_id).first()
    if request.method == 'GET':
        questions = random.sample(questions,t.tot_questions)
        random.shuffle(questions)
        q_str = []
        for i in questions:
            q_str.append(str(i.id))
        session['questions'] = ' '.join(q_str)
        global_questions = questions
        m = Marks.query.filter_by(student_id=current_user.id,test_id=testId).first()
        if m:
            return render_template("test.html", data=questions, currentUserType=currentUserType, restricted=True)
        # print(global_questions)
        return render_template("test.html", data=questions, currentUserType=currentUserType, restricted=False, teacher=teach, subject = t.subject, duration=t.tot_time*60)
    else:
        # questions = global_questions
        questions = session['questions'].split(' ')
        result = 0
        m = Marks(test_id=testId,student_id=current_user.id, score=result)
        db.session.add(m)
        db.session.commit()
        for q_str in questions:
            # print(q_str)
            q = Questions.query.filter_by(id=int(q_str)).first()
            selected = str(q.id)
            try:
                student_ans = request.form[selected]
                if student_ans == str(q.ans):
                    ans = Answers(marks_id=m.id,q_id=q.id,student_ans=student_ans,right_ans=True)
                    result += 1
                else:
                    ans = Answers(marks_id=m.id,q_id=q.id,student_ans=student_ans,right_ans=False)
                db.session.add(ans)
            except Exception as e:
                ans = Answers(marks_id=m.id,q_id=q.id,student_ans='',right_ans=False)
                db.session.add(ans)
                # print(e)
            m.score = result
            db.session.commit()
        return redirect(url_for("solution",testId=testId))

@app.route("/result/<int:testId>", methods=['POST', 'GET'])
def result(testId):
    r = Marks.query.filter_by(test_id=testId,student_id=current_user.id).first()
    t = Test.query.filter_by(id=r.test_id).first()
    prc = (r.score/t.tot_questions) * 100
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
    a = Answers.query.filter_by(marks_id=r.id).all()
    teach = Teacher.query.filter_by(id=t.teacher_id).first()
    prc = (r.score/t.tot_questions) * 100
    questionsAll = Questions.query.filter_by(test_id=testId).all()
    questions = []
    for q in a:
        temp = dict()
        new_q = Questions.query.filter_by(id=q.q_id).first()
        temp['q_id'] = new_q.id
        temp['question_text'] = new_q.question_text
        temp['test_id'] = new_q.test_id
        temp['ans'] = new_q.ans
        temp['op1'] = new_q.op1
        temp['op2'] = new_q.op2
        temp['op3'] = new_q.op3
        temp['student_ans'] = q.student_ans
        temp['right_ans'] = q.right_ans
        questions.append(temp)
    # random.shuffle(questions)
    return render_template('view_test.html', percentage=round(prc,2), subject=t.subject ,currentUserType=currentUserType, data=questions, teacher = teach)


@app.route("/dashboard",methods=['POST', 'GET'])
@login_required
def dashboard():
    if currentUserType.isStudent():
        my_all=Marks.query.filter_by(student_id=current_user.id).with_entities(Marks.score).all()
        my_all_marks=[x[0] for x in my_all]
        my_temp=Marks.query.filter_by(student_id=current_user.id).with_entities(Marks.test_id).all()
        my_temp_tests=[x[0] for x in my_temp]
        # print(my_temp_tests)
        my_all_tests=[]
        for i in my_temp_tests:
            t=Test.query.filter_by(id=i).with_entities(Test.subject).all()
            temp=[x[0] for x in t]
            my_all_tests.append(temp[0])
        # print(my_all_tests,my_all_marks)
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
            temp['date'] = row.date_of_attempt.date()
            temp['score'] = row.score
            temp['tot_questions'] = tempTest.tot_questions
            temp['teacher'] = tempTeacher.name
            temp['code'] = tempTest.code
            temp['id'] = row.id
            temp['testId'] = row.test_id
            temp['tot_questions'] = tempTest.tot_questions
            res.append(temp)
        return render_template('student_dash.html', title='Dashboard', form=code_form ,currentUserType = currentUserType, rows=res, values=my_all_marks, labels=my_all_tests)
    elif currentUserType.isTeacher():
        dat=Test.query.filter_by(teacher_id=current_user.id).all()
        my_subjects,grand_totals,test_ids=[],[],[]
        for i in dat:
            test_ids.append(i.id)
            my_subjects.append(i.subject)
            grand_totals.append(i.tot_questions)
        passs,fail=[0]*len(test_ids),[0]*len(test_ids)
        for i in range(len(test_ids)):

            t=Marks.query.filter_by(test_id=test_ids[i]).with_entities(Marks.score).all()
            temp=[x[0] for x in t]
            for k in temp:

                if k/grand_totals[i]>=0.35:
                    passs[i]+=1
                else:
                    fail[i]+=1
        # print("This is some data",passs,fail,my_subjects)
        pass_col=["green"]*len(test_ids)
        fail_col=["red"]*len(test_ids)
        # passs=[]
        # fail=[]
        return render_template('teacher_dash.html', title='Dashboard',currentUserType = currentUserType,rows=dat,passs=passs,fail=fail,labels=my_subjects,pass_col=pass_col,fail_col=fail_col)

    else:
        return redirect(url_for('home'))

@app.route("/graph/<int:testId>",methods=['POST', 'GET'])
def graph(testId):

    all_studs = Marks.query.filter_by(test_id=testId).with_entities(Marks.id).all()
    labels=[x[0] for x in all_studs]
    all_marks=Marks.query.filter_by(test_id=testId).with_entities(Marks.score).all()
    values=[x[0] for x in all_marks]
    # print(labels,values)
    my_mark=Marks.query.filter_by(test_id=testId,student_id=current_user.id).with_entities(Marks.score).all()
    my_marks=[x[0] for x in my_mark]

    three_values=[min(values),sum(values)/len(values),max(values),my_marks[0]]
    plot_three_labels=['Minimum','Average','Maximum','Your score']

    leader=Marks.query.filter_by(test_id=testId).order_by(desc(Marks.score)).all()
    # print(leader)

    leader_board = []
    for row in leader:
        temp = dict()
        temp['Srno']=row.id
        temp['student_id'] = row.student_id
        temp['date'] = row.date_of_attempt
        temp['score'] = row.score
        name=Student.query.filter_by(id=row.student_id).with_entities(Student.name).first()
        s_name=name[0]
        # print(s_name)
        temp['name']=s_name

        leader_board.append(temp)
    # print(leader_board)

    if len(leader_board)>=3:
        fin_lead=leader_board[:3]
    else:
        fin_lead=leader_board

    #For pie Chart
    all_qs = Questions.query.filter_by(test_id = testId).all()
    marks_row=Marks.query.filter_by(test_id=testId,student_id=current_user.id).first()
    stud_ans = Answers.query.filter_by(marks_id = marks_row.id).all()
    stats = {'right':0,'wrong':0,'unattempted':0}
    for i in stud_ans:
        if i.student_ans == '' or i.student_ans == None:
            stats['unattempted'] += 1
        elif i.right_ans==0:
            stats['wrong'] += 1
        elif i.right_ans==1:
            stats['right'] +=1

    return render_template("graph.html", title="Statistics",labels=labels, values=values,plot_three_labels=plot_three_labels,three_values=three_values,rows=fin_lead,currentUserType = currentUserType, stats=stats)

@app.route('/teach_graph/<id>/', methods = ['GET', 'POST'])
def teach_graph(id):
    t=Marks.query.filter_by(test_id=id).all()
    sub=Test.query.filter_by(id=id).with_entities(Test.subject).first()
    subj=sub[0]
    student_list=[]
    for row in t:
        temp = dict()
        temp['Srno']=row.id
        temp['student_id'] = row.student_id
        temp['date'] = row.date_of_attempt
        temp['score'] = row.score
        name=Student.query.filter_by(id=row.student_id).with_entities(Student.name).first()
        s_name=name[0]
        temp['name']=s_name
        dat=Test.query.filter_by(teacher_id=current_user.id,id=row.test_id).with_entities(Test.tot_questions).first()
        out_of=[x for x in dat]
        temp['out_of']=out_of[0]


        student_list.append(temp)
    t_name=current_user.name
    pp=t_name.split(' ')
    # print(pp)

    filename=subj + '_' + pp[0] + '_' + 'results.csv'
    # print(filename)
    return render_template("teach_graph.html", title="Result",rows=student_list,filename=filename,currentUserType = currentUserType)
