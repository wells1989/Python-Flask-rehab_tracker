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

