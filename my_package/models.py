from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class User(db.Model):
    user_id=db.Column(db.Integer(),primary_key=True)
    user_email=db.Column(db.String(60),nullable=False,unique=True)
    user_password=db.Column(db.String(200),nullable=False)
    user_registration_date=db.Column(db.DateTime(),default=datetime.utcnow)
    user_status=db.Column(db.Enum('0','1'),nullable=False,server_default=('1'))
    #relationship below:
    userdeets=db.relationship('Survey',back_populates='survdeets',cascade='all, delete-orphan')
    userrsp=db.relationship('Response',back_populates='rspuser',cascade='all, delete-orphan')
    
    
class Question(db.Model):
    question_id=db.Column(db.Integer(),primary_key=True)
    question_text=db.Column(db.Text(),nullable=False)
    survey_id=db.Column(db.Integer(),db.ForeignKey('survey.survey_id'),nullable=False)
    date_added=db.Column(db.DateTime(),default=datetime.utcnow)
    #relationship below:
    questsurv=db.relationship('Survey', back_populates='survquest')
    questopt=db.relationship('Option',back_populates='optquest',cascade='all, delete-orphan')
    questrsp=db.relationship('ResponseQuestion',back_populates='rspquest',cascade='all, delete-orphan')

class Category(db.Model):
    category_id=db.Column(db.Integer(),primary_key=True)
    category_name=db.Column(db.String(60),nullable=False)
    category_image=db.Column(db.String(200),nullable=False)
    category_icon=db.Column(db.String(200),nullable=False)
    date_added=db.Column(db.DateTime(),default=datetime.utcnow)
    # relationship below:
    catsurv=db.relationship('Survey', back_populates='survcat',cascade='all, delete-orphan')
       
class Admin(db.Model):
    admin_id=db.Column(db.Integer(),primary_key=True)
    admin_username=db.Column(db.String(20),nullable=False,unique=True)
    admin_pwd=db.Column(db.String(200),nullable=False)
    
class Survey(db.Model):
    survey_id=db.Column(db.Integer(),primary_key=True)
    survey_name=db.Column(db.String(60),nullable=False)
    survey_status=db.Column(db.Enum('1','0'),nullable=False,server_default=('0'))
    date_opened=db.Column(db.DateTime(),default=datetime.utcnow)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False)
    category_id=db.Column(db.Integer(),db.ForeignKey('category.category_id'),nullable=False)
    #Relationship below:
    survdeets=db.relationship('User',back_populates='userdeets')
    surveyrsp=db.relationship('Response',back_populates='rspsurvey',cascade='all, delete-orphan')
    survcat=db.relationship('Category', back_populates='catsurv')
    survquest=db.relationship('Question', back_populates='questsurv',cascade='all, delete-orphan')
    
class Response(db.Model):
    response_id=db.Column(db.Integer(),primary_key=True)
    survey_id=db.Column(db.Integer(),db.ForeignKey('survey.survey_id'),nullable=False)
    user_id=db.Column(db.Integer(),db.ForeignKey('user.user_id'),nullable=False)
    response_time=db.Column(db.DateTime(),default=datetime.utcnow)
    #relationship below:
    rspsurvey=db.relationship('Survey',back_populates='surveyrsp')
    rspuser=db.relationship('User',back_populates='userrsp')
    rspdeets=db.relationship('ResponseQuestion',back_populates='rspres',cascade='all, delete-orphan')
      
class ResponseQuestion(db.Model):
    response_question_id=db.Column(db.Integer(),primary_key=True)
    response_id=db.Column(db.Integer(),db.ForeignKey('response.response_id'),nullable=False)
    question_id=db.Column(db.Integer(),db.ForeignKey('question.question_id'),nullable=False)
    option_id=db.Column(db.Integer(),db.ForeignKey('option.option_id'),nullable=False)
    #relationship below:
    rspres=db.relationship('Response',back_populates='rspdeets')
    rspquest=db.relationship('Question',back_populates='questrsp')
    rspopt=db.relationship('Option',back_populates='optrsp')
    
    
class Option(db.Model):
    option_id=db.Column(db.Integer(),primary_key=True)
    option_text=db.Column(db.Text(),nullable=False)
    question_id=db.Column(db.Integer(),db.ForeignKey('question.question_id'),nullable=False)
    #relationship below:
    optquest=db.relationship('Question',back_populates='questopt')
    optrsp=db.relationship('ResponseQuestion',back_populates='rspopt',cascade='all, delete-orphan')
    
