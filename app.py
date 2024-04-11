from flask import Flask, jsonify, request, url_for
from db import *
from flask import session, render_template, redirect
from utils.utils import process_request

app = Flask(__name__)

# DEV ONLY test route
@app.route('/test', methods=["GET"])
def test():
    logged_in_user = session.get('logged_in_user')
    return f' logged_in_user : {logged_in_user}'

# homepage route
@app.route('/', methods=["GET"])
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
@app.route('/register', methods=['GET', 'POST'])
def register():
     
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        fields = ('name', 'email', 'password', 'profile_pic', 'bio')
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
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
        fields = ('email', 'password')
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

@app.route('/logout', methods=["POST"])
def logout():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return f'no user logged in', 400
    else:
        session["logged_in_user"] = None
        return redirect("/", code=301)
        # dev only return f'user logged out', 200

@app.route('/deleted', methods=["GET", "DELETE"])
def deleted():
    return render_template("user_deleted.html")

## User routes
@app.route('/users', methods=["GET"])
def users():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "Unauthorised", 401

    result = db_block(view_all_users, logged_in_user)
    if result:
            return result
    else:
        return 404


## individual User routes
@app.route("/users/<int:id>", methods=["GET", "PUT", "DELETE"])
def user(id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user or id != logged_in_user["id"]:
        return render_template("not_authorised.html")

    if request.method == "GET":
        result = db_block(view_user, id, logged_in_user)
        if result:
            profile = db_block(view_profile, id, logged_in_user)[0]
            return render_template("profile_page.html", user=logged_in_user, profile=profile)
        else: 
            return redirect("/")
        
    elif request.method == "PUT":
        
        result, status_code = update_wrapper(request, ["name", "email"], id, update_user, logged_in_user)

        if status_code > 400:
            return "Failed to update user", status_code

        updated_user, status_code = db_block(view_user, id, logged_in_user)

        session['logged_in_user'] = updated_user 
        # dev only for postman testing
        user_agent = request.headers.get('User-Agent', '')
        if 'Postman' in user_agent:
            return "User updated successfully", 200
            # slight BUG in that postman updates aren't reflected until user logs out and in again
        else:
            return updated_user, 200
    
    elif request.method == "DELETE":
        
        result, status_code = db_block(delete_user, id, logged_in_user)
        if status_code != 200:
            return result, status_code
        elif result:
            session["logged_in_user"] = None

            # dev only, postman testing
            user_agent = request.headers.get('User-Agent', '')
            if 'Postman' in user_agent:
                return "User deleted successfully", 200
            return redirect("/deleted")
        else:
            return 404

## User profile routes
@app.route("/users/profiles/<int:user_id>", methods=["GET", "PUT"]) # user_id, NOT profile id
def profile(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    if request.method == "GET": 
        profile, status_code = db_block(view_profile, user_id, logged_in_user)
        if profile:
            if status_code == 401:
                return render_template("not_authorised.html")
            # dev only, for postman queries
            if request.accept_mimetypes.accept_json:
                return jsonify({"user": logged_in_user, "profile": profile}), 200
            else:
                return render_template("profile_page.html", user=user, profile=profile)
        else:
            return 404

    elif request.method == "PUT":
        return update_wrapper(request, ["profile_pic", "bio"], user_id, update_profile, logged_in_user)

# password reset
@app.route('/users/<int:user_id>/password_reset', methods=["GET", "POST"])
def password_reset(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "Unauthorized", 401
    
    if request.method == "GET":
        if user_id == logged_in_user["id"]:
            return render_template ("password_reset.html", user=logged_in_user)
        else:
            return render_template("not_authorised.html")

    if request.method == "POST":
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('confirm_password')

        result, status_code = db_block(change_password, old_password, new_password, logged_in_user, user_id)

        if status_code != 200:
            return result, status_code
        else:
            return f'password changed!'


## exercise routes (viewing exercises or posting new one)
@app.route('/exercises', methods=["GET", "POST"])
def exercises():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401

    if request.method == "GET":
        result = db_block(view_all_exercises)
        if result:
                return result
    elif request.method == "POST":

        try:
            fields = ("name", "image")
            values = process_request(request, *fields)

            name, image = values['name'], values["image"]
        
            result = db_block(create_exercise, logged_in_user, name, image)

            return jsonify({'result': result})
        except:
            return "error occurred", 400
    
"""
# viewing a users exercises (to allow deletion or editing ...)
@app.route('/exercises/user/<int:creator_id>', methods=["GET"])
def view_users_exercises(creator_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    try:
        users_exercises, status_code = db_block(view_users_exercises, logged_in_user)

        if status_code != 200:
            return 'issue getting exercises', status_code
        else:
            return jsonify(f'result: {users_exercises}')
    except:
        return "error", 400
"""

# individual exercise routes (selecting, updating or deleting)
@app.route('/exercises/<int:id>', methods=["GET", "PUT", "DELETE"])
def exercise(id):
    # DEV ONLY not being used yet 11/4 GET or PUT ??
    if request.method == "GET":
        result = db_block(view_exercise, id)
        if result:
                return result
        else:
            return 404
        
    # DEV ONLY not being used yet 11/4 GET or PUT ??
    if request.method == "PUT":
        logged_in_user = session.get('logged_in_user')
        if not logged_in_user:
            return "Unauthorized", 401
        
        return update_wrapper(request, ["name", "image"], id, update_exercise, logged_in_user)


    if request.method == "DELETE":
        try:
            logged_in_user = session.get('logged_in_user')
            if not logged_in_user:
                return "Unauthorized", 401
            
            result, status_code = db_block(delete_exercise, id, logged_in_user)
            if status_code == 200:
                return result
            else:
                return result, status_code
        except:
            return 'error occurred'
 

# User program routes
@app.route('/programs/<int:user_id>', methods=["GET", "POST"])
def programs_get_and_post(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401
        
    if request.method == "GET":
        result = db_block(view_all_user_programs, logged_in_user, user_id)
        if result:
                return result
        
    elif request.method == "POST":

        fields = ('start_date', 'end_date', 'description')
        values = process_request(request, *fields)

        start_date, end_date, description = values['start_date'], values["end_date"], values['description']
        
        if request.form.get('rating'):
            rating = request.form.get('rating')
        else:
            rating = None 
        
        result, status_code = db_block(create_program, logged_in_user, start_date, end_date, rating, description)

        if status_code != 200:
            return result, status_code

        return redirect("/", code=301)

# individual program routes (getting, updating, deleting)
@app.route('/programs/program/<int:user_id>/<int:program_id>', methods=["GET"])
def user_program(user_id, program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    try:
        program, p_status_code = db_block(view_program, logged_in_user, user_id, program_id)
        if p_status_code != 200:
            return redirect("/", code=301)

        program_exercises, pe_status_code  = db_block(view_programs_exercises, logged_in_user, user_id, program_id)
        if pe_status_code == 401:
            return render_template("not_authorised.html")

        exercises, e_status_code = db_block(view_all_exercises)

        users_exercises, ue_status_code = db_block(view_users_exercises, logged_in_user)
        if ue_status_code == 401:
            return render_template("not_authorised.html")

        user_agent = request.headers.get('User-Agent', '')
        if 'Postman' in user_agent:
            return program, program_exercises

        else:
            return render_template("program_page.html", program=program, program_exercises=program_exercises, exercises=exercises, users_exercises=users_exercises)
    except:
        return redirect("/", code=301)


@app.route('/programs/<int:program_id>', methods=["PUT", "DELETE"])
def programs_update_and_delete(program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    user_id = logged_in_user['id']
    if request.method == "PUT":

        try:
            data = request.get_json()
            if not all(field in data for field in ["start_date", "end_date", "rating", "description"]):
                return redirect(f'/programs/{program_id}')
            
            # print(data) # {'start_date': '2024-04-12', 'end_date': '2024-04-19', 'rating': '1', 'user_id': '62', 'description': 'h there'}

            result = update_wrapper(request, ["start_date", "end_date", "rating", "description"], program_id, update_program, logged_in_user)

            status_code = result[1]

            if status_code not in [200, 201]:
                return "Failed to update program", status_code
            else:
                return "success", status_code
        except:
            return redirect(url_for('user_program', user_id=user_id, program_id=program_id))


    elif request.method == "DELETE":
        try:
            result, status_code = db_block(delete_program, program_id, logged_in_user)
            
            user_agent = request.headers.get('User-Agent', '')
            if 'Postman' in user_agent:
                return result, status_code

            if status_code == 401:
                return redirect("not_authorised.html")
            else:
                return redirect("/", code=301)
        except:
            return redirect("/", code=301)


# adding exercises to a program
@app.route('/details', methods=["POST"])
def details():

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")

    if request.method == "POST":
        
        try: 
            form_data = request.form.to_dict()
            exercise_id = form_data.get('exercise_id')

            exercise_info, status_code = db_block(view_exercise, exercise_id)
            if status_code != 200:
                return exercise_info, status_code
        
            exercise_name = exercise_info['name']
            user_id = logged_in_user['id']
            program_id = form_data.get('program_id')

            notes = form_data.get('notes')
            sets = form_data.get('sets')
            reps = form_data.get('reps')
            rating = int(form_data.get('rating')) if form_data.get('rating') is not '' else None
            result, status_code = db_block(add_exercise_to_program, program_id, exercise_id, notes, sets, reps, rating, logged_in_user)

            # DEV ONLY
            user_agent = request.headers.get('User-Agent', '')
            if 'Postman' in user_agent:
                return jsonify({'result': result})

            return redirect(f'/programs/program/{user_id}/{program_id}')

        except:
            return redirect(f'/programs/program/{user_id}/{program_id}')

# removing / updating exercises in a program

@app.route('/details/<int:exercise_id>/<int:program_id>', methods=["PUT", "DELETE"])
def update_or_remove_program_exercise(exercise_id, program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    else:
        user_id = logged_in_user['id']
    
    if request.method == "PUT":
        pass

    if request.method == "DELETE":
        try:
            result, status_code = db_block(delete_exercise_from_program, program_id, exercise_id, logged_in_user)

            return result, status_code
        except:
            return redirect(f'/programs/program/{user_id}/{program_id}')


# DEV ONLY, REPLACE /programs/details route, interfering with programs GET
## program_exercise routes (adding, updating or deleting an exercise from a program)
@app.route('/programs/details/<int:program_id>/<int:exercise_id>', methods=["POST", "PUT", "DELETE"])
def prog_exercises(program_id, exercise_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")

    if request.method == "POST":
        
        form_data = request.form.to_dict()
    
        # Print form data
        print("Form Data:", form_data)
        return

        data = request.get_json()
        notes = data.get('notes')
        sets = data.get('sets')
        reps = data.get('reps')
        rating = data.get('rating')

        result = db_block(add_exercise_to_program, program_id, exercise_id, notes, sets, reps, rating, logged_in_user)

        return jsonify({'result': result})
    
    elif request.method == "PUT":
        data = request.get_json()
        allowed_fields = ["notes", "sets", "reps", "rating"]

        fields = {}
        for field in allowed_fields:
            if field in data:
                fields[field] = data[field]

        query = "SET "
        num_fields = len(fields)
        for index, (key, value) in enumerate(fields.items()):
            if value is not None:
                query += f"{key} = '{value}'"
                if index < num_fields - 1:
                    query += ", "

        result = db_block(update_exercise_in_program, program_id, exercise_id, logged_in_user, query)
        if result:
            return result
        else:
            return 404
        
    elif request.method == "DELETE":
        result = db_block(delete_exercise_from_program, program_id, exercise_id, logged_in_user)

        if result:
            return result
        else: return 404
        


# getting exercises and details in a program (ie. sets and reps etc)
@app.route("/programs/details/<int:user_id>/<int:program_id>", methods=["GET"])
def get_exercise_programs(user_id, program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401

    if program_id == 0:
        # returning all a users programs_exercises
        result = db_block(view_users_past_exercises, logged_in_user, user_id)
        if result:
            return result
        else:
            return 404
    else:
        # returning a specific users program with exercises etc
        result = db_block(view_programs_exercises, logged_in_user, program_id, user_id)
        if result:
            return result
        else:
            return 404


