from flask import Blueprint, session, render_template, redirect, request, jsonify
import os
from db import *
from utils.utils import request_missing_fields

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

exercises_bp = Blueprint('exercises', __name__, url_prefix='/exercises', template_folder=template_dir)

@exercises_bp.route('/', methods=["GET", "POST"])
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

            missing_fields, status_code = request_missing_fields(request, fields)
            if status_code != 200:
                return render_template("error_template.html", message=missing_fields), status_code
        
            values = process_request(request, *fields)

            name, image = values['name'], values["image"]
        
            result, status_code = db_block(create_exercise, logged_in_user, name, image)

            if status_code != 201:
                return render_template("error_template.html", message=result), status_code
            else:
                return result, status_code
        except:
            return render_template("error_template.html", message="Error occurred"), 400

# individual exercise routes (selecting, updating or deleting)
@exercises_bp.route('/<int:id>', methods=["DELETE"])
def exercise(id):
    
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
 