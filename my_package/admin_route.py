from functools import wraps
import random
from flask import render_template,request,abort,redirect,url_for,flash,session

from my_package import survey,csrf
from my_package.models import db,Category,Admin,Survey,User
from my_package.forms import *
@survey.after_request
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    return response

def admin_required(f): #must always be placed aboved any route that needs autentication
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('admin') !=None:
            return f(*args,**kwargs)
        else:
            flash('You must be logged in')
            return redirect('/ninjasurvey/admin/login/')
    return login_check

@survey.route('/ninjasurvey/admin/',methods=['post','get'])
@admin_required
def admin_dashboard():
        return render_template('admin/admin_dashboard.html')


@survey.route('/ninjasurvey/admin/addcategory/',methods=['post','get'])
def add_category():
    if request.method=='GET':
        return render_template('admin/add_category.html',title='Add Category')
    else:
        iconobj=request.files['icon']
        filesobj=request.files['picture']
        filename=filesobj.filename
        iconname=iconobj.filename
        if filename !='':
            newname=filename.split('.')
            newicon=iconname.split('.')
            ext=newname[-1].lower()
            con=newicon[-1].lower()
            if ext in ['jpg','png','jpeg'] and con in ['jpg','png','jpeg']:
                categorypicture=str(int(random.random()*10000000000))+filename
                iconpix=str(int(random.random()*10000000000))+iconname
                filesobj.save('my_package/static/template_uploads/'+categorypicture)
                iconobj.save('my_package/static/templateicons/'+iconpix)
            else:
                flash('Template Picture is required')
                return redirect(url_for('add_category'))
        
        categoryname=request.form.get('name')
        category=Category(category_name=categoryname,category_image=categorypicture,category_icon=iconpix)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('all_category'))
        

@survey.route('/ninjasurvey/admin/Category/')
def all_category():
    cat=db.session.query(Category).all()
    return render_template('admin/allcategory.html',title='All Category',cat=cat)

@survey.route('/ninjasurvey/admin/login/',methods=['post','get'])
def admin_login():
    reg=AdminForm()
    if request.method=='GET':
        return render_template('admin/adminlogin.html',reg=reg)
    else:
        if reg.validate_on_submit():
            admin=request.form.get('adminname')
            pwd=request.form.get('pwd')
            ent=db.session.query(Admin).filter(Admin.admin_username==admin,Admin.admin_pwd==pwd)
            if ent:
                session['admin']=admin
                return redirect('/ninjasurvey/admin/')
            else:
                flash('Invalid Login Details')
                return render_template('admin/adminlogin.html',reg=reg)
        else:
            flash('Invalid Login Details')
            return render_template('admin/adminlogin.html',reg=reg)
        
@survey.route('/ninjasurvey/admin/allsurvey')
def see_survey():
    surveys=db.session.query(Survey).all()
    return render_template('admin/allsurvey.html',surveys=surveys)

@survey.route('/editstatus/<id>')
def edit_status(id):
    stat=db.session.query(Survey).get(id)
    if stat.survey_status=='1':
        stat.survey_status='0'
        db.session.commit()
        return redirect(url_for('see_survey'))
    else:
        stat.survey_status='1'
        db.session.commit()
        return redirect(url_for('see_survey'))

@survey.route('/ninjasurvey/restrict/<id>/')
@admin_required
def restrict(id):
    rest=db.session.query(User).get(id)
    if rest.user_status=='1':
        rest.user_status='0'
        db.session.commit()
        return redirect(url_for('allusers'))
    else:
        rest.user_status='1'
        db.session.commit()
        return redirect(url_for('allusers'))

@survey.route('/ninjasurvey/admin/allusers/') 
@admin_required
def allusers():
    users=db.session.query(User).all() 
    return render_template('admin/allusers.html',users=users)  

@survey.route('/ninjasurvey/admin/logout/')
def admin_logout():
    if session.get('admin') != None:
        session.pop('admin',None)
    return redirect('/ninjasurvey/admin/login/')

@survey.route('/deletecategory/<id>/')
@admin_required
def delete_category(id):
    q=db.session.query(Category).get(id)
    db.session.delete(q)
    db.session.commit()
    flash('Template deleted',category='danger')
    return redirect(url_for('all_category'))

   
    