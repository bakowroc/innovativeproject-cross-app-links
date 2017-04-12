from flask import Flask, make_response, jsonify, render_template, redirect, session, request, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from passlib.hash import sha256_crypt
from api import app
from api.models import User, Group, App, Log, Invites
from api.database import db
from api.mail import send_email, send_email_register



#-----------
#FUNCTIONS
#-----------
def commituser(token,userpassword):
    new = Invites.query.filter_by(token = token).first()
    useremail = new.email
    new = User(useremail,sha256_crypt.encrypt(userpassword))
    db.session.add(new)
    db.session.commit()
    removeinvite(useremail)


def commitinvite(email,maker):
    new = Invites(email,maker.id)
    db.session.add(new)
    db.session.commit()
    receiver = [email]
    send_email_register(maker.email,receiver)




def removeuser(email):
    sadman = User.query.filter_by(email = email).first()
    db.session.delete(sadman)
    db.session.commit()



def removeinvite(email):
    sadman = Invites.query.filter_by(email = email).first()
    db.session.delete(sadman)
    db.session.commit()

#-----------
#STATIC VAL
#-----------

#Registered list of available templates
index_content_list = [
    'dashboard',
    'stats',
    'action-log',
    'links',
    'add-link',
    'users',
    'groups',
    'add-user',
    'settings',
    'ver'
]

#Login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# put @login_required to deny access for unknown visitors

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

#-----------
#ROUTING
#-----------
#Auth route
# User verification
@app.route('/api/auth', methods=['POST'])
def auth():
    session.pop('user', None)
    user = User.query.filter_by(email=request.form['email']).first()
    if user:
        if sha256_crypt.verify(request.form['password'], user.password_hash):
            login_user(user)
            session['user'] = user.username
            return redirect('/')
        else:
            return make_response(open('api/templates/login-page.html').read())
    else:
        return make_response(open('api/templates/login-page.html').read())


#Logout user and close session
@app.route('/api/auth/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect('/')

#Register new user in database
#Send email after successful registration
@app.route('/api/auth/register', methods=['POST'])
@login_required
def register():
    if not User.query.filter_by(email=request.form['email']).first():
        commitinvite(request.form['email'],current_user)
        return redirect('/add-user')
    else:
        return 'Error. Email already in use!'


# #Confirm account
@app.route('/api/auth/setpassword', methods=['GET','POST'])
def setpassword():
    if request.method == 'POST':
        temp = request.args.get('token')
        givenpassword = request.form['password']
        commituser(temp,givenpassword)
        return redirect('/')
    else:
        return make_response(open('api/templates/create-user.html').read())


# Delete user
@app.route('/api/auth/remove', methods=['POST'])
@login_required
def remove():
    if User.query.filter_by(email=request.form['email']).first():
        removeuser(request.form['email'])
        if Invites.query.filter_by(email=request.form['email']).first():
            removeinvite(request.form['email'])
        return redirect('/add-user')
    else:
        return 'Error. Email not found!'

#Default templates for Flask route
@app.route('/')
@app.route('/<content>')
@app.route('/<content>/<content_id>')
def main(content='dashboard', content_id=None):
        if content in index_content_list:
            if not g.user:
                return make_response(open('api/templates/login-page.html').read())
            else:
                return make_response(open('api/templates/index.html').read())
        else:    
            return make_response(open('api/templates/404.html').read())
        

#Routes for components data
@app.route('/component_data/iframe')
def component():
	# apps = App.query.all()
    # return render_template('iframe-web-component.html')
    return make_response(open('api/templates/iframe-web-component.html').read())


#Routes for components test
@app.route('/component/<component_type>')
def component_test(component_type):
    if component_type=='iframe':
        return make_response(open('api/static/web-components/iframe/iframe-index.html').read())
    elif component_type=='json':
        return make_response(open('api/static/web-components/json/json-index.html').read())
    return None

@app.route('/webpack')
def webpack():
    return make_response(open('api/static/src/test.html').read())
