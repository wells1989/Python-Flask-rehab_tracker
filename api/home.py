from flask import Blueprint, session, render_template, redirect, request, jsonify
import os
from db import *
from utils.utils import request_missing_fields

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

main_bp = Blueprint('main', __name__, url_prefix='/', template_folder=template_dir)

# homepage route
@main_bp.route('/', methods=["GET"])
def homepage():
    logged_in_user = session.get('logged_in_user')
    if logged_in_user:

        profile, profile_status_code = db_block(view_profile, logged_in_user['id'], logged_in_user)

        programs, programs_status_code = db_block(view_all_user_programs, logged_in_user, logged_in_user['id'])
        if programs_status_code != 200:
            programs = []

        return render_template('homepage.html', logged_in_user = logged_in_user, profile=profile, programs=programs)
    else:
        return render_template('login.html')
 
## Register / login / logout
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
     
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        try:
            fields = ('name', 'email', 'password', 'profile_pic', 'bio')

            missing_fields, status_code = request_missing_fields(request, ['name', 'email', 'password'])
            if status_code != 200:
                return render_template("error_template.html", message=missing_fields), status_code
            
            values = process_request(request, *fields)
            
            name, email, password, profile_pic, bio = values['name'], values["email"], values['password'], values['profile_pic'], values['bio']

            logged_in_user, status_code = db_block(register_user, name, email, password, profile_pic, bio)
            
            # dev only
            if not request.form:
                return jsonify({'result': logged_in_user})
            
            if status_code != 200:
                return render_template("register.html", error=logged_in_user)
            else:
                session['logged_in_user'] = logged_in_user 
                return redirect("/", code=301)

        except:
            return redirect("/")


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
            fields = ('email', 'password')

            missing_fields, status_code = request_missing_fields(request, fields)
            if status_code != 200:
                return render_template("error_template.html", message=missing_fields), status_code
                
            values = process_request(request, *fields)
            
            email, password = values['email'], values['password']

            logged_in_user, status_code = db_block(log_in, email, password)

            if status_code != 200:
                return render_template('login.html', error=logged_in_user)
            else:
                session['logged_in_user'] = logged_in_user 
                # dev only
                if not request.form:
                    return f'logged_in_user: {logged_in_user}', 200
                
                return redirect("/", code=301) # NOTE: need 301 status for successful redirects, otherwise will get continued "should be redirected" message ...

@main_bp.route('/logout', methods=["POST"])
def logout():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template('login.html', error="no logged in user")
    else:
        session["logged_in_user"] = None
        return redirect("/", code=301)

