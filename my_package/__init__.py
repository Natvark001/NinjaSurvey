from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail,Message
from flask_migrate import Migrate


csrf=CSRFProtect()
mail=Mail()

def create_app():
    #here all import that may cause infinite recursion is kept. none of the statement is executed
    from my_package.models import db
    survey=Flask(__name__,instance_relative_config=True)
    survey.config.from_pyfile('config.py',silent=True)
    db.init_app(survey)
    migrate=Migrate(survey,db)
    csrf.init_app(survey)
    mail.__init__(survey)
    return survey
    
survey=create_app()
from my_package import admin_route,user_route,error_route #loading of routes is done here
from my_package.forms import *