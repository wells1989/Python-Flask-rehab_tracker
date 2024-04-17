from flask import Blueprint, session, render_template, redirect, request, jsonify, url_for
import os
from db import *

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

programs_bp = Blueprint('programs', __name__, url_prefix='/programs', template_folder=template_dir)


# User program routes
@programs_bp.route('/<int:user_id>', methods=["GET", "POST"])
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


# individual program routes
@programs_bp.route('/program/<int:user_id>/<int:program_id>', methods=["GET"])
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


@programs_bp.route('/<int:program_id>', methods=["PUT", "DELETE"])
def programs_update_and_delete(program_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    user_id = logged_in_user['id']
    if request.method == "PUT":

        try:
            raw_data = request.get_json()
            if not all(field in raw_data for field in ["start_date", "end_date", "rating", "description"]):
                return redirect(f'/programs/{program_id}')
            
            print(raw_data)

            fields = ("start_date", "end_date", "rating", "description")
            data = process_request(request, *fields)

            for key in ["start_date", "end_date", "rating"]:
                if data[key] == '':
                    data[key] = None
            
            query = "SET "
            values=[]
            num_fields = len(data)
            for index, (key, value) in enumerate(data.items()):

                query += f"{key} = %s"
                values.append(value)
                if index < num_fields - 1:
                    query += ", "

            result, status_code = db_block(update_program, query, program_id, values, logged_in_user )

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

