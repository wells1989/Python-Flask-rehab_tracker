from flask import Blueprint, session, render_template, redirect, request, jsonify
import os
from db import *

current_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')

users_bp = Blueprint('users', __name__, url_prefix='/users', template_folder=template_dir)


## individual User routes
@users_bp.route("/<int:id>", methods=["GET", "PUT", "DELETE"])
def user(id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user or id != logged_in_user["id"]:
        return render_template("not_authorised.html")

    if request.method == "GET":
        try:
            result, status_code = db_block(view_user, id, logged_in_user)
            if status_code == 200:
                profile = db_block(view_profile, id, logged_in_user)[0]
                return render_template("profile_page.html", user=logged_in_user, profile=profile, logged_in_user=logged_in_user)
            else: 
                return redirect("error_template", message=result)
        except:
            return redirect("/")
        
    elif request.method == "PUT":
        try:
            
            if (len(request.json.get('name') < 3)) or (not validate_email(request.json.get('email'))):
                return "please insert valid fields", 400

            result, status_code = update_wrapper(request, ["name", "email"], id, update_user, logged_in_user)

            if status_code > 400:
                return redirect("error_template", message="failed to update user")

            updated_user, status_code = db_block(view_user, id, logged_in_user)

            session['logged_in_user'] = updated_user 
            # dev only for postman testing
            user_agent = request.headers.get('User-Agent', '')
            if 'Postman' in user_agent:
                return "User updated successfully", 200
                # slight BUG in that postman updates aren't reflected until user logs out and in again
            else:
                return updated_user, 200
        except:
            return redirect(f'/users/profiles/{id}')

    elif request.method == "DELETE":
        
        try:
            result, status_code = db_block(delete_user, id, logged_in_user)
            if status_code != 200:
                return result, status_code
            elif result:
                session["logged_in_user"] = None

                # dev only, postman testing
                user_agent = request.headers.get('User-Agent', '')
                if 'Postman' in user_agent:
                    return "User deleted successfully", 200
                return result, status_code
            else:
                return 404
        except:
            return redirect(f'/users/profiles/{id}')

@users_bp.route("/deleted", methods=["GET"])
def delete_route():
    return render_template("user_deleted.html")


## User profile routes
@users_bp.route("/profiles/<int:user_id>", methods=["GET", "PUT"]) # user_id, NOT profile id
def profile(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    if request.method == "GET": 
        try:
            result, status_code = db_block(view_profile, user_id, logged_in_user)
            if result:
                if status_code == 401:
                    return render_template("not_authorised.html")
                
                elif status_code != 200:
                    return render_template("error_template.html", message=result)
                
                # dev only, for postman queries
                if request.accept_mimetypes.accept_json:
                    return jsonify({"user": logged_in_user, "profile": result}), 200
                else:
                    return render_template("profile_page.html", user=user, profile=result)
            else:
                return 404
        except:
            return redirect("/")

    elif request.method == "PUT":
            try:
                update_wrapper(request, ["profile_pic", "bio"], user_id, update_profile, logged_in_user)

                return redirect(f'/users/profiles/{id}')
            except:
                return redirect(f'/users/profiles/{id}')


# password reset
@users_bp.route('/<int:user_id>/password_reset', methods=["GET", "POST"])
def password_reset(user_id):
    logged_in_user = session.get('logged_in_user')
    if not logged_in_user:
        return render_template("not_authorised.html")
    
    if request.method == "GET":
        return render_template ("password_reset.html", user=logged_in_user)

    if request.method == "POST":
        try:
            data = request.get_json()
            old_password = data.get('old_password')
            new_password = data.get('confirm_password')

            result, status_code = db_block(change_password, old_password, new_password, logged_in_user, user_id)

            if status_code == 200:
                return result, status_code
            else:
                return "Incorrect password. Please try again.", 400
        except:
            return redirect(f'/users/profiles/{id}')

