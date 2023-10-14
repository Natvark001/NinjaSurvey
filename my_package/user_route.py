from functools import wraps
import random
from flask import render_template,request,flash,make_response,url_for,session,redirect
from werkzeug.security import generate_password_hash,check_password_hash

from sqlalchemy.sql import text


#local importations below
from my_package import survey,csrf,mail,Message
from my_package.models import db,User,Category,Survey,Question,Option,Response,ResponseQuestion
from my_package.forms import RegisterForm


def login_required(f): #must always be placed aboved any route that needs autentication
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('user') !=None:
            return f(*args,**kwargs)
        else:
            flash('You must be logged in')
            return redirect('/ninjasurvey/login/')
    return login_check

@survey.route('/ninjasurvey/survey/')
def temp_survey():
    template=db.session.query(Category).all()
    return render_template('users/survey.html',template=template)

@survey.route('/ninjasurvey/home/',methods=['post','get'])
def home_page():
    create=RegisterForm()
    total_category=Category.query.count()
    random_number=random.sample(range(1,(total_category+1)),12)
    samplecategory=db.session.query(Category).filter(Category.category_id.in_(random_number)).limit(6).all()
    if request.method =="GET":
        return render_template('users/index.html',create=create,samplecategory=samplecategory)
    else:
        if create.validate_on_submit():
            email=request.form.get('email')
            pwd=request.form.get('pwd')
            confpwd=request.form.get('confpwd')
            encpass=generate_password_hash(pwd)
            u=db.session.query(User).filter(User.user_email==email).first()
            if u:
                flash('Email already in use')
                return redirect('/ninjasurvey/home/')
            else:
                user=User(user_email=email,user_password=encpass)
                db.session.add(user)
                db.session.commit()
                msg = Message(subject="Ninja Survey",sender='From NinjaSurvey',recipients=[email])
                msg.html='''<div><h2>Thank you for Registering with Ninja Survey</h2>
                <p>Follow the link below to login</p>
                <p>http://127.0.0.1:7070/ninjasurvey/login/</p></div>'''
                mail.send(msg)
                flash(f'Account created, confirmation email has been sent to {email}',category='success')
                return redirect('/ninjasurvey/home/')
        else:
            return render_template('users/index.html',create=create,samplecategory=samplecategory)

@survey.route('/ninjasurvey/ourpage/')
def our_page():
    return render_template('users/others.html')

@survey.route('/surveystatus/<id>')
def survey_status(id):
    stat=db.session.query(Survey).get(id)
    if stat.survey_status=='1':
        stat.survey_status='0'
        db.session.commit()
        return redirect(url_for('create_survey'))
    else:
        stat.survey_status='1'
        db.session.commit()
        return redirect(url_for('create_survey'))

@survey.route('/ninjasurvey/login/',methods=['post','get'])
def login_page():
    if request.method=='GET':
        return render_template('users/login.html')
    else:
        mail=request.form.get('email')
        pwd=request.form.get('password')
        log=db.session.query(User).filter(User.user_email==mail).first()
        if log !=None:
            if log.user_email == mail and log.user_status=='1':
                encpass=log.user_password
                if check_password_hash(encpass,pwd)==True:
                    session['user']=mail #to keep session
                    return redirect(url_for('user_dashboard'))
                else:
                    flash('Invalid Login.Try Again')
                    return redirect('/ninjasurvey/login/')
            else:
                flash('Your account has been restricted')
                return redirect('/ninjasurvey/login/')
        else:
            flash('Invalid Login.Try Again')
            return redirect('/ninjasurvey/login/')

@survey.route('/ninjasurvey/userdashboard/')
@login_required
def user_dashboard():
    return render_template('users/userdashboard.html',title='DashBoard')

@survey.route('/ninjasurvey/createquestions/<id>/',methods=['post','get'])
@login_required
def add_questions(id):
    s=db.session.query(Survey).filter(Survey.survey_id==id).first()
    if request.method=="GET":
        return render_template('users/createquestion.html',survey=s)
    else:
        question=request.form.get('question')
        option1=request.form.get('option1')
        option2=request.form.get('option2')
        option3=request.form.get('option3')
        q=Question(question_text=question,survey_id=s.survey_id)
        db.session.add(q)
        qo=db.session.query(Question).filter(Question.question_text==question).first()
        opt1=Option(option_text=option1,question_id=qo.question_id)
        opt2=Option(option_text=option2,question_id=qo.question_id)
        opt3=Option(option_text=option3,question_id=qo.question_id)
        db.session.add(opt1)
        db.session.add(opt2)
        db.session.add(opt3)
        db.session.commit()
        return 'Question Added with options'


@survey.route('/ninjasurvey/createsurvey/',methods=['post','get'])
@login_required
def create_survey():
    if request.method=="GET":
        user=db.session.query(User).filter(User.user_email==session.get('user')).first()
        u=user.user_id
        s=db.session.query(Survey).filter(Survey.user_id==u).all()
        return render_template('users/createsurvey.html',surveys=s)

@survey.route('/ninjasurvey/newsurvey',methods=['post','get'])
def new_survey():
    if request.method=='GET':
        cat=db.session.query(Category).all()
        return render_template('users/newsurvey.html',cats=cat)
    else:
        user=db.session.query(User).filter(User.user_email==session.get('user')).first()
        u=user.user_id
        surveytitle=request.form.get('surveytitle')
        category=request.form.get('surveycategory')
        newsurvey=Survey(survey_name=surveytitle,category_id=category,user_id=u)
        db.session.add(newsurvey)
        db.session.commit()
        su=db.session.query(Survey).filter(Survey.survey_name==surveytitle).first()
        survid=su.survey_id
        return redirect(url_for('add_questions',id=survid))



@survey.route('/ninjasurvey/participate/')
@login_required
def participate():
        pat=db.session.query(Survey).filter(Survey.survey_status=='1').all()
        return render_template('users/participate.html',pat=pat)
        

@survey.route('/ninjasurvey/allquestions/<id>',methods=['post','get'])
@login_required
def answer(id): #need to work on this
    if request.method=="GET":
        suv=db.session.query(Survey).get(id)
        all=db.session.query(Question).filter(Question.survey_id==id).all()
        if all :
            for q in all:
                opt=db.session.query(Option).filter(Option.question_id==q.question_id).all()
            return render_template('users/answer.html',all=all,opt=opt,suv=suv)
        else:
            flash('No questions available')
            return redirect(url_for('participate'))
    else:
        surv=db.session.query(Survey).get(id)
        user=db.session.query(User).filter(User.user_email==session.get('user')).first()
        u=user.user_id
        rspq=Response(survey_id=surv.survey_id,user_id=u)
        db.session.add(rspq)
        for question in Question.query.all():
            response_option_id=request.form.get(f'opt_{question.question_id}') 
            if response_option_id:
                r=db.session.query(Response).get(rspq.response_id)
                response=ResponseQuestion(response_id=r.response_id,question_id=question.question_id,option_id=response_option_id)
                db.session.add(response)      
                db.session.commit()
        
        flash('Thank you for your response',category='success')
        return redirect(url_for('participate'))

@survey.route('/ninjasurvey/track')  
@login_required
def track():
    user=db.session.query(User).filter(User.user_email==session['user']).first()
    u=user.user_id
    survey=db.session.query(Survey).filter(Survey.user_id==u).all()
    return render_template('users/track.html',survey=survey) 

@survey.route('/ninjasurvey/track/answer/<id>/') 
@login_required
def track_answer(id):
    response=db.session.query(Response).filter(Response.survey_id==id).all()
    return render_template('users/trackanswer.html',response=response)

@survey.route('/ninjasurvey/surveyparticipated')
@login_required
def survey_participated():
    user=db.session.query(User).filter(User.user_email==session['user']).first()
    svpart=db.session.query(Response).filter(Response.user_id==user.user_id).all()
    return render_template('users/surveyparticipated.html',svpart=svpart)
               

@survey.route('/ninjasurvey/survey/questions/<id>') 
def all_question(id):
    question=db.session.query(Question).filter(Question.survey_id==id).all()
    return render_template('users/questions.html',questions=question) 

@survey.route('/ninjasurvey/editquestion/<int:id>/',methods=['post','get']) 
@login_required
def edit_question(id): #need to work on this
    if request.method=="GET":
        option=db.session.query(Option).filter(Option.question_id==id).all()
        questions=db.session.query(Question).get_or_404(id)
        return render_template('users/editquestion.html',option=option,questions=questions)
    else:
        option2update=db.session.query(Option).filter(Option.question_id==id).all()
        question2update=db.session.query(Question).get_or_404(id)
        question2update.question_text=request.form.get('question')
        option2update[0].option_text=request.form.get('option1')
        option2update[1].option_text=request.form.get('option2')
        option2update[2].option_text=request.form.get('option3')
        db.session.commit()
        return 'Question has been edited'
    
@survey.route('/ninjasurvey/editsurvey/<id>',methods=['post','get'])
@login_required
def edit_survey(id):
    if request.method=="GET":
        survey=db.session.query(Survey).get(id)
        return render_template('users/editsurvey.html',survey=survey)
    else:
        survey=db.session.query(Survey).get(id)
        survey.survey_name=request.form.get('surveytitle')
        db.session.commit()
        flash('Survey Updated')
        return redirect(url_for('create_survey'))

@survey.route('/deletesurvey/<id>/')
@login_required
def delete_survey(id):
    s=db.session.query(Survey).get(id)
    db.session.delete(s)
    db.session.commit()
    flash('Survey deleted',category='danger')
    return redirect(url_for('create_survey'))
    
    

@survey.route('/deletequestion/<id>/')
@login_required
def delete_question(id):
    q=db.session.query(Question).get(id)
    db.session.delete(q)
    db.session.commit()
    flash('question deleted',category='danger')
    return redirect(url_for('create_survey'))
    
          
        
        
   
@survey.route('/ninjasurvey/user/logout')
def logout():
    if session.get('user') != None:
        session.pop('user',None)
        flash('you are logged out')
    return redirect('/ninjasurvey/login/')

@survey.after_request #solve the issue of user going back to a protected page
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    return response