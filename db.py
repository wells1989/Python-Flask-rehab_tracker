import bcrypt
import binascii
import psycopg2
from utils.utils import database_connect, database_close, validate_email, validate_password, admin_check, results_to_dict, db_block, update_wrapper, process_request, search_for_user

logged_in_user = None 


# selecting specific user
def view_user(conn, cursor, id, logged_in_user):

    if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user to view
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))

        if cursor.rowcount == 0:
            return("No instance found"), 404
        else:
            result = results_to_dict(cursor, "ind")
            return result, 200
    else:
        return("not authorized"), 401


def update_user(conn, cursor, query, id, values, logged_in_user):
    if admin_check(logged_in_user) or logged_in_user["id"] == id:
        cursor.execute("UPDATE users " + query + " WHERE id = %s", values + [id])
        conn.commit()
        if cursor.rowcount > 0:
            return ("update successful"), 200
        else:
            return("No instance found"), 404

    else:
        return("not authorized"), 401


def delete_user(conn, cursor, id, logged_in_user):
    if admin_check(logged_in_user) or logged_in_user["id"] == id: 
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "deletion successful", 200
        else:
            return "No instance found", 401

    else:
        return "not authorized", 404


## userProfiles
def view_profile(conn, cursor, user_id, logged_in_user):

    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT * FROM userprofiles WHERE user_id = %s", (user_id,))
        if cursor.rowcount == 0:
            return "No instance found", 404
        result = results_to_dict(cursor, "ind")

        return result, 200
    else:
        return "not authorised", 401

def update_profile(conn, cursor, query, user_id, values, logged_in_user):
    if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
        cursor.execute("UPDATE userprofiles " + query + " WHERE user_id = %s", values + [user_id])
        conn.commit()
        if cursor.rowcount > 0:
            return "Update successful", 200
        else:
            return "No instance found", 404

    else:
        return "not authorized", 401


## Exercises
def view_all_exercises(conn, cursor):
    cursor.execute("SELECT * FROM exercises ORDER BY name, id")

    if cursor.rowcount == 0:
        return "No instance found", 404
    else:
        result = results_to_dict(cursor, "list")
        return result, 200

def view_users_exercises(conn, cursor, logged_in_user):
    cursor.execute("SELECT * FROM exercises WHERE creator_id = %s ORDER BY id DESC", (logged_in_user["id"],))

    if cursor.rowcount == 0:
        return "No instance found", 404
    else:
        result = results_to_dict(cursor, "list")
        return result, 200

    
def view_exercise(conn, cursor, id):

    cursor.execute("SELECT * FROM exercises WHERE id = %s", (id,))
    if cursor.rowcount == 0:
        return "No instance found", 404
    result = results_to_dict(cursor, "ind")

    return result, 200

def create_exercise(conn, cursor, logged_in_user, name, image=""):

    user_id = logged_in_user["id"]
    cursor.execute("INSERT INTO exercises (name, image, creator_id) VALUES (%s, %s, %s) RETURNING id, name, image, creator_id", (name, image, user_id)) # need the returning to access in .fetchone()
    conn.commit()
    
    created_exercise = cursor.fetchone() 

    if created_exercise:
        return 'exercise created', 201
    else:
        return "Failed to create exercise", 500


def update_exercise(conn, cursor, query, exercise_id, logged_in_user):

    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()

    if not exercise:
        return "No instance found", 404
    else:
        creator_id = exercise[3]

    if admin_check(logged_in_user) or logged_in_user["id"] == creator_id:
        cursor.execute("UPDATE exercises " + query + " WHERE id = %s", (exercise_id,)) # restricted to exercises that user created
        conn.commit() 
        if cursor.rowcount > 0:
            return "Update successful", 200
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401


def delete_exercise(conn, cursor, id, logged_in_user):
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (id,))
    exercise = cursor.fetchone()

    if not exercise:
        return "No instance found", 404
    else:
        creator_id = exercise[3]

    if admin_check(logged_in_user) or logged_in_user["id"] == creator_id:
        cursor.execute("DELETE FROM exercises WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "deletion successful", 200
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401


## programs
def create_program(conn, cursor, logged_in_user, start_date, end_date, rating, description):
    user_id = logged_in_user["id"]

    cursor.execute("INSERT INTO programs (user_id, start_date, end_date, rating, description) VALUES (%s, %s, %s, %s, %s) RETURNING user_id, start_date, end_date, rating, description", (user_id, start_date, end_date, rating, description))
    conn.commit()
    created_program = cursor.fetchone() 

    if created_program:
        return created_program, 200
    else:
        return "Failed to create program", 500

# selecting all programs for specific user
def view_all_user_programs(conn, cursor, logged_in_user, user_id):
    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT * FROM programs WHERE user_id = %s ORDER BY start_date DESC", (user_id,))
        if cursor.rowcount == 0:
            return "No instance found", 404
        else:
            results = results_to_dict(cursor, "list")

            return results, 200
    else:
        return "not authorised", 401


# selecting a specific program
def view_program(conn, cursor, logged_in_user, user_id, program_id):
    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT * FROM programs WHERE user_id = %s AND id = %s LIMIT 1", (user_id, program_id,))
        if cursor.rowcount == 0:
            return "No instance found", 404
        else:
            result = results_to_dict(cursor, "ind")

            return result, 200
    else:
        return "not authorised", 401


def update_program(conn, cursor, query, program_id, values, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone()

    if not program:
        return "No instance found", 404
    else:
        user_id = program[1]

    if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
        full_query = f'UPDATE programs {query} WHERE id = %s'
        print(full_query)
        cursor.execute(full_query, (*values, program_id))
        conn.commit()
        if cursor.rowcount > 0:
            return "Update successful", 201
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401

def delete_program(conn, cursor, program_id, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone()

    if not program:
        return "No instance found", 404
    else:
        user_id = program[1]

    if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
        cursor.execute("DELETE FROM programs WHERE id = %s AND user_id = %s", (program_id, user_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "deletion successful", 201
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401


## program_exercises
def view_programs_exercises(conn, cursor, logged_in_user, user_id, program_id):

    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT e.id AS exercise_id, e.image, e.name, pe.notes, pe.sets, pe.reps, pe.rating FROM programs_exercises pe JOIN exercises e ON pe.exercise_id = e.id WHERE user_id = %s AND program_id = %s ORDER BY lastmod DESC", (user_id, program_id))

        if cursor.rowcount == 0:
            return "No instance found", 404

        result = results_to_dict(cursor, "list")
        return result, 200
    else:
        return "not authorised", 401

def add_exercise_to_program(conn, cursor, program_id, exercise_id, notes, sets, reps, rating, date_modified, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone() 
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not program:
        return "program not found", 404
    if not exercise:
        return "exercise not found", 404
    
    cursor.execute("SELECT * FROM programs_exercises WHERE program_id = %s AND exercise_id = %s", (program_id, exercise_id))
    duplicate = cursor.fetchone()
    if duplicate:
        return "exercise already in program", 400

    if program[1] == logged_in_user["id"] or admin_check(logged_in_user):
        exercise_name = exercise[1]
        user_id = logged_in_user["id"]
        cursor.execute("INSERT into programs_exercises (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating, lastmod) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating, lastmod", (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating, date_modified))

        conn.commit()

        program_exercise_details = cursor.fetchone() 

        if program_exercise_details:
            return program_exercise_details, 201
        else:
            return "Failed to add_exercise", 500

    else:
        return "not authorised", 401

def update_exercise_in_program(conn, cursor, program_id, exercise_id, logged_in_user, query, values):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone() 
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not program:
        return "program not found", 404
    if not exercise:
        return "exercise not found", 404

    if admin_check(logged_in_user) or logged_in_user["id"] == program[1]:
        cursor.execute("UPDATE programs_exercises " + query + " WHERE exercise_id = %s AND program_id = %s", (*values, exercise_id, program_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "Update successful", 201
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401

def delete_exercise_from_program(conn, cursor, program_id, exercise_id, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone() 
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not program:
        return "program not found", 404
    if not exercise:
        return "exercise not found", 404

    if admin_check(logged_in_user) or logged_in_user["id"] == program[1]:
        cursor.execute("DELETE FROM programs_exercises WHERE exercise_id = %s AND program_id = %s", (exercise_id, program_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "deletion successful", 200
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401


## Register / log in routes
def register_user(conn, cursor, name, email, user_password, profile_pic="", bio=""):
    
    user_check = db_block(search_for_user, email)

    if isinstance(user_check, dict):
        return "User already exists, please log in", 409
    
    if len(name) < 3:
        return "Name needs to be at least 3 characters long", 400

    if validate_email(email) and validate_password(user_password):
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (name, email, hashed_password))

        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO userProfiles (user_id, profile_pic, bio) VALUES (%s, %s, %s)", (user_id, profile_pic, bio)) 
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    
        if cursor.rowcount == 0:
            return "internal error", 500
        else:
            user = results_to_dict(cursor, "ind")

            logged_in_user = user
            return logged_in_user, 200

    elif not validate_email(email):
        return f"Invalid email address", 400
    elif not validate_password(user_password):
        return "password must be 8 characters long, and include alphabetical, numerical and 1 special character", 400

def log_in(conn, cursor, email, user_password):

    if not email or not user_password:
        return "missing input fields", 400

    user = db_block(search_for_user, email)

    if not isinstance(user, dict):
        return "Error finding user", 404

    stored_hashed_password = user["password"]

    # coming back as a hex string, so need to convert it into binary for bcrypt.checkpw ...
    hex_string = stored_hashed_password.replace("\\x", "")
    binary_hash = binascii.unhexlify(hex_string)

    # Hashing the user's provided password for comparison
    user_guess_encoded_password = user_password.encode('utf-8')

    if bcrypt.checkpw(user_guess_encoded_password, binary_hash):
        logged_in_user = user
        return logged_in_user, 200
    else:
        return "passwords don't match", 400

def logout(logged_in_user):
    if not logged_in_user:
        return
    
    logged_in_user = None
    return logged_in_user


def change_password(conn, cursor, old_password, new_password, logged_in_user, id):
    if admin_check(logged_in_user) or id == logged_in_user["id"]:

        users_password_hash = logged_in_user["password"]

        hex_string = users_password_hash.replace("\\x", "")
        binary_hash = binascii.unhexlify(hex_string)

        # Hashing the user's provided password for comparison
        user_guess_encoded_password = old_password.encode('utf-8')

        if bcrypt.checkpw(user_guess_encoded_password, binary_hash):

            cursor.execute("SELECT * FROM users WHERE id = %s", (logged_in_user["id"],))
        
            if cursor.rowcount == 0:
                return "internal error", 500
            else:
                user = results_to_dict(cursor, "ind")
                
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed_password, user['id']))
                # above, returns id of the new user, can be accessed by cursor.fetchone()[0]
                conn.commit()
                return user, 200
            
        else:
            return "passwords don't match", 400
       
    else:
        return "not authorised", 401