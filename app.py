from flask import Flask, jsonify, request
from db import *
from flask import session

app = Flask(__name__)

# test route
@app.route('/', methods=["GET"])
def test():
    return f'route working'


## Register / login / logout
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    profile_pic = data.get('profile_pic')
    bio = data.get('bio')
    
    result = db_block(register_user, name, email, password, profile_pic, bio)

    return jsonify({'result': result})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    logged_in_user = log_in(email, password)

    if logged_in_user:
        session['logged_in_user'] = logged_in_user 

        return f'logged_in_user: {logged_in_user}', 200
    else:
        return 'Invalid email or password', 401

@app.route('/logout', methods=["POST"])
def logout():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return f'no user logged in', 200
    else:
        session["logged_in_user"] = None
        return f'user logged out', 200


## User routes
@app.route('/users', methods=["GET"])
def users():
    logged_in_user = session.get('logged_in_user')
    if logged_in_user:
        result = db_block(select_users, logged_in_user)
        if result:
                return result
        else:
            return 404
    else:
        return "Unauthorized", 401


## individual User routes
@app.route("/users/<int:id>", methods=["GET", "PUT", "DELETE"])
def user(id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "Unauthorised", 401

    if request.method == "GET":
        result = db_block(select_user, id, logged_in_user)
        if result:
            return result
        else:
            return "User not found", 404
        
    elif request.method == "PUT":
        return update_wrapper(request, ["name", "email", "password"], id, update_user, logged_in_user)
        
    elif request.method == "DELETE":
        
        result = db_block(delete_user, id, logged_in_user)
        if result:
            return result
        else:
            return 404


## User profile routes
@app.route("/users/profiles/<int:user_id>", methods=["GET", "PUT"]) # user_id, NOT profile id
def profile(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "Unauthorized", 401
    
    if request.method == "GET":
        result = db_block(select_profile, user_id, logged_in_user)
        if result:
            return result
        else:
            return 404

    elif request.method == "PUT":
        return update_wrapper(request, ["profile_pic", "bio"], user_id, update_profile, logged_in_user)


## exercise routes (viewing exercises or posting new one)
@app.route('/exercises', methods=["GET", "POST"])
def exercises():
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401

    if request.method == "GET":
        result = db_block(select_exercises)
        if result:
                return result
    elif request.method == "POST":
        data = request.get_json()
        name = data.get('name')
        image = data.get('image')
        
        result = db_block(create_exercise, logged_in_user, name, image)

        return jsonify({'result': result})
    

# individual exercise routes (selecting, updating or deleting)
@app.route('/exercises/<int:id>', methods=["GET", "PUT", "DELETE"])
def exercise(id):
    if request.method == "GET":
        result = db_block(select_exercise, id)
        if result:
                return result
        else:
            return 404
    
    if request.method == "PUT":
        logged_in_user = session.get('logged_in_user')
        if not logged_in_user:
            return "Unauthorized", 401
        
        return update_wrapper(request, ["name", "image"], id, update_exercise, logged_in_user)

    if request.method == "DELETE":
        logged_in_user = session.get('logged_in_user')
        if not logged_in_user:
            return "Unauthorized", 401
        
        result = db_block(delete_exercise, id, logged_in_user)
        if result:
            return result
        else:
            return 404
        

# User program routes
@app.route('/programs/<int:user_id>', methods=["GET", "POST"])
def programs_get_and_post(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401
        
    if request.method == "GET":
        result = db_block(select_programs, logged_in_user, user_id)
        if result:
                return result
        
    elif request.method == "POST":
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        rating = data.get('rating')
        description = data.get('description')

        result = db_block(create_program, logged_in_user, start_date, end_date, rating, description)

        return jsonify({'result': result})


# individual program routes (getting, updating, deleting)
@app.route('/programs/program/<int:user_id>/<int:program_id>', methods=["GET"])
def get_user_program(user_id, program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401

    result = db_block(select_user_program, logged_in_user, user_id, program_id)
    if result:
            return result

@app.route('/programs/<int:program_id>', methods=["PUT", "DELETE"])
def programs_update_and_delete(program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401
    
    if request.method == "PUT":
        return update_wrapper(request, ["start_date", "end_date", "rating", "description"], program_id, update_program, logged_in_user)


    elif request.method == "DELETE":
        result = db_block(delete_program, program_id, logged_in_user)
        if result:
            return result
        else:
            return 404
        

## program_exercise routes (adding, updating or deleting an exercise from a program)
@app.route('/programs/details/<int:program_id>/<int:exercise_id>', methods=["POST", "PUT", "DELETE"])
def prog_exercises(program_id, exercise_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return "need to log in first!", 401

    if request.method == "POST":
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

        result = db_block(update_exercise_program, program_id, exercise_id, logged_in_user, query)
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
        result = db_block(view_users_exercise_programs, logged_in_user, user_id)
        if result:
            return result
        else:
            return 404
    else:
        # returning a specific users program with exercises etc
        result = db_block(view_specific_exercise_program, logged_in_user, program_id, user_id)
        if result:
            return result
        else:
            return 404
