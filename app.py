from flask import Flask, jsonify, request, url_for
from db import *
from flask import session, render_template, redirect
from utils.utils import process_request
from datetime import datetime
from api import home, users, exercises, programs

app = Flask(__name__)
app.register_blueprint(home.main_bp)
app.register_blueprint(users.users_bp)
app.register_blueprint(exercises.exercises_bp)
app.register_blueprint(programs.programs_bp)


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
        
            user_id = logged_in_user['id']
            program_id = form_data.get('program_id')

            notes = form_data.get('notes')
            sets = form_data.get('sets')
            reps = form_data.get('reps')
            date_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            rating = int(form_data.get('rating')) if form_data.get('rating') != '' else None
            result, status_code = db_block(add_exercise_to_program, program_id, exercise_id, notes, sets, reps, rating, date_modified, logged_in_user)

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
        
        # try:
            fields = ("notes", "sets", "reps", "rating")
            data = process_request(request, *fields)

            data['lastmod'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

            print(f'values: {data}')
            # DEV ONLY
            """
            print(f'values: {data}')
            notes, sets, reps, rating = data['notes'], data["sets"], data["reps"], int(data["rating"])
            print(f'exercise_id: {exercise_id}')
            print(f'program_id: {program_id}')

            print(f'notes: {notes}')
            print(f'notes: {sets}')
            print(f'notes: {reps}')
            print(f'rating: {rating}')
            """

            query = "SET "
            num_fields = len(data)
            for index, (key, value) in enumerate(data.items()):
                if value is not None:
                    query += f"{key} = '{value}'"
                    if index < num_fields - 1:
                        query += ", "

            result, status_code = db_block(update_exercise_in_program, program_id, exercise_id, logged_in_user, query)

            return result, status_code
        #except:
            #return redirect(f'/programs/program/{user_id}/{program_id}')
            

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


