from flask import Blueprint, session, render_template, redirect, request, jsonify, url_for
import os
from db import *
from datetime import datetime
from utils.utils import request_missing_fields

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

details_bp = Blueprint('details', __name__, url_prefix='/details', template_folder=template_dir)


# adding exercises to a program
@details_bp.route('/', methods=["POST"])
def details():

    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")

    if request.method == "POST":
        
        try:
            required_fields = ["exercise_id", "program_id"]

            missing_fields, status_code = request_missing_fields(request, required_fields)
            if status_code != 200:
                return render_template("error_template.html", message=missing_fields), status_code

            form_data = request.form.to_dict()
            exercise_id = form_data.get('exercise_id')
        
            user_id = logged_in_user['id']
            program_id = form_data.get('program_id')

            notes = form_data.get('notes')
            sets = int(form_data.get('sets')) if form_data.get('sets') != '' else None
            reps = int(form_data.get('reps')) if form_data.get('reps') != '' else None
            
            date_modified = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            rating = int(form_data.get('rating')) if form_data.get('rating') != '' else None
            result, status_code = db_block(add_exercise_to_program, program_id, exercise_id, notes, sets, reps, rating, date_modified, logged_in_user)

            # DEV ONLY
            user_agent = request.headers.get('User-Agent', '')
            if 'Postman' in user_agent:
                return jsonify({'result': result})

            if status_code == 201:
                return"successfully added exercise", 201
            else:
                return render_template("error_template.html", message="an error occurred"), status_code
        except:
            return render_template("error_template.html", message="an error occurred"), 400


# removing / updating exercises in a program
@details_bp.route('/<int:exercise_id>/<int:program_id>', methods=["PUT", "DELETE"])
def update_or_remove_program_exercise(exercise_id, program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    else:
        user_id = logged_in_user['id']
    
    if request.method == "PUT":
        
        try:
            fields = ("notes", "sets", "reps", "rating")

            missing_fields, status_code = request_missing_fields(request, fields)
            if status_code != 200:
                return render_template("error_template.html", message=missing_fields), status_code

            data = process_request(request, *fields)

            data['lastmod'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

            for key in ["sets", "reps", "rating"]: 
                if data[key] == '' or not str(data[key]).isnumeric():
                    data[key] = None

            query = "SET "
            num_fields = len(data)
            values= []
            for index, (key, value) in enumerate(data.items()):
                    query += f"{key} = %s"
                    values.append(value)
                    if index < num_fields - 1:
                        query += ", "
                    
            result, status_code = db_block(update_exercise_in_program, program_id, exercise_id, logged_in_user, query, values)

            return result, status_code

        except:
            return render_template("error_template.html", message="an error occurred"), 400

            

    if request.method == "DELETE":
        try:
            result, status_code = db_block(delete_exercise_from_program, program_id, exercise_id, logged_in_user)

            return result, status_code
        except:
            return render_template("error_template.html", message="an error occurred"), 400
