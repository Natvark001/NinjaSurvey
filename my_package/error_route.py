from flask import render_template,request,abort

from my_package import survey

@survey.errorhandler(404)
def page_not_found(error):
    return render_template('errors/notfound.html',error=error,title='page not found'),404

@survey.errorhandler(403)
def page_forbidden(error):
    return render_template('errors/forbidden.html',error=error,title='Forbidden'),403