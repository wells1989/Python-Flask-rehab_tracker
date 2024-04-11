import bcrypt
import binascii
import psycopg2
from utils.utils import database_connect, database_close, validate_email, validate_password, admin_check, results_to_dict, db_block, update_wrapper

logged_in_user = None 

## common CRUD operations

# open select query ... ??
def select_query(conn, cursor, query, parameters=None, restricted=False, logged_in_user=None):

    if (restricted and admin_check(logged_in_user) or not restricted): # i.e. is restricted user needs to be an admin to proceed
        cursor.execute(query, parameters) # instead of query, (parameters) to allow data cleaning and prevent SQL injections

        dictionaries = results_to_dict(cursor, "list")
        
        return dictionaries
    else:
        print("not authorized")
        return
"""
e.g's
print(db_block(select_query, "SELECT * FROM programs"))
print(db_block(select_query, "SELECT * FROM programs WHERE id = 2"))
print(db_block(select_query, "SELECT * FROM users", True, logged_in_user))
"""

# select all users
def view_all_users(conn, cursor, logged_in_user):

    if admin_check(logged_in_user): # i.e. is restricted user needs to be an admin to proceed
        cursor.execute("SELECT * FROM users")

        if cursor.rowcount == 0:
            return "No users found", 404
        else:
            result = results_to_dict(cursor, "list")
            return result, 200
    else:
        return "not authorized", 404
# e.g. print(db_block(view_all_users, logged_in_user))


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
# e.g. print(db_block(view_user, 19, logged_in_user))


def update_user(conn, cursor, query, id, values, logged_in_user):
    if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user
        cursor.execute("UPDATE users " + query + " WHERE id = %s", values + [id])
        conn.commit()
        if cursor.rowcount > 0:
            return ("update successful"), 200
        else:
            return("No instance found"), 404

    else:
        return("not authorized"), 401
# OLD pre values: db_block(update_user, "SET name = 'V-man'", 30, logged_in_user)


def delete_user(conn, cursor, id, logged_in_user):
    if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "deletion successful", 200
        else:
            return "No instance found", 401

    else:
        return "not authorized", 404
# e.g. db_block(delete_user, 1, logged_in_user)
    

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
# e.g. print(db_block(view_profile, 17, logged_in_user))

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
# OLD PRE values e.g. db_block(update_profile, "SET bio = 'I am from Rotterdam'", 17, logged_in_user)


## Exercises
# selecting all exercises
def view_all_exercises(conn, cursor):
    cursor.execute("SELECT * FROM exercises ORDER BY name, id")

    if cursor.rowcount == 0:
        return "No instance found", 404
    else:
        result = results_to_dict(cursor, "list")
        return result, 200
# e.g. print(db_block(view_all_exercises))

def view_users_exercises(conn, cursor, logged_in_user):
    cursor.execute("SELECT * FROM exercises WHERE creator_id = %s ORDER BY name, id", (logged_in_user["id"],))

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

# e.g. print(db_block(view_exercise, 17))
    

def create_exercise(conn, cursor, logged_in_user, name, image=""):

    user_id = logged_in_user["id"]
    cursor.execute("INSERT INTO exercises (name, image, creator_id) VALUES (%s, %s, %s) RETURNING id, name, image, creator_id", (name, image, user_id)) # need the returning to access in .fetchone()
    conn.commit()
    
    created_exercise = cursor.fetchone() 

    if created_exercise:
        return created_exercise, 201
    else:
        return "Failed to create exercise", 500

# e.g. db_block(create_exercise, logged_in_user, "squats", "sample image2")
# / alt db_block(create_exercise, logged_in_user, "muay thai")


def update_exercise(conn, cursor, query, exercise_id, logged_in_user):

    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()

    if not exercise:
        return "No instance found", 404
    else:
        creator_id = exercise[3]

    if admin_check(logged_in_user) or logged_in_user["id"] == creator_id:
        cursor.execute("UPDATE exercises " + query + " WHERE id = %s", (exercise_id,)) # restricted exercises that user created
        conn.commit() 
        if cursor.rowcount > 0:
            return "Update successful", 200
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401
# e.g. db_block(update_exercise, "SET name = 'bench' WHERE name = 'dips'", 3, logged_in_user)


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
# e.g. db_block(delete_exercise, 6, logged_in_user)


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
# e.g. db_block(create_program, logged_in_user, "2000-10-20", "2000-12-20", 2, "summer_regime 2")


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
# e.g. print(db_block(view_all_user_programs, logged_in_user, 19))


# selecting a specific user's program
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
    #  print(db_block(view_program, logged_in_user, 28, 10))


def update_program(conn, cursor, query, program_id, values, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone()

    if not program:
        return "No instance found", 404
    else:
        user_id = program[1]

    if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
        cursor.execute("UPDATE programs " + query + " WHERE id = %s", values + [program_id]) # restricted exercises that user created
        conn.commit()
        if cursor.rowcount > 0:
            return "Update successful", 201
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401
    

# e.g. db_block(update_program, "SET description = 'brand new description'", 8, ...., logged_in_user)


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
# e.g. db_block(delete_program, 6, logged_in_user)


## program_exercises
def add_exercise_to_program(conn, cursor, program_id, exercise_id, notes, sets, reps, rating, logged_in_user):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone() 
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not program:
        return "program not found", 404
    if not exercise:
        return "exercise not found", 404

    if program[1] == logged_in_user["id"] or admin_check(logged_in_user):
        exercise_name = exercise[1]
        user_id = logged_in_user["id"]
        cursor.execute("INSERT into programs_exercises (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating", (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating))

        conn.commit()

        program_exercise_details = cursor.fetchone() 

        if program_exercise_details:
            return program_exercise_details, 201
        else:
            return "Failed to add_exercise", 500

    else:
        return "not authorised", 401
# e.g. db_block(add_exercise_to_program, 2, 6, "trying it for now", 3, 10, 1, logged_in_user)


def update_exercise_in_program(conn, cursor, program_id, exercise_id, logged_in_user, query):

    cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
    program = cursor.fetchone() 
    cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
    exercise = cursor.fetchone()
    
    if not program:
        return "program not found", 404
    if not exercise:
        return "exercise not found", 404

    if admin_check(logged_in_user) or logged_in_user["id"] == program[1]:
        cursor.execute("UPDATE programs_exercises " + query + " WHERE exercise_id = %s AND program_id = %s", (exercise_id, program_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "Update successful", 201
        else:
            return "No instance found", 404
    else:
        return "not authorised", 401
# e.g. db_block(update_exercise_in_program, 7, 4, logged_in_user, "SET notes = 'boo that it went awfully'")


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
# e.g. db_block(delete_exercise_from_program, 2, 2, logged_in_user)


# shows all the users exercise_programs
def view_users_past_exercises(conn, cursor, logged_in_user, user_id):

    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT * FROM programs_exercises WHERE user_id = %s", (user_id,))
        if cursor.rowcount == 0:
            return "No instance found", 401
        results = results_to_dict(cursor, "list")

        return results, 200
    else:
        return "not authorised", 401
# e.g. print(db_block(view_users_past_exercises, logged_in_user, 19))


def view_programs_exercises(conn, cursor, logged_in_user, user_id, program_id):

    if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
        cursor.execute("SELECT * FROM programs_exercises WHERE user_id = %s AND program_id = %s", (user_id, program_id))
        if cursor.rowcount == 0:
            return "No instance found", 404

        result = results_to_dict(cursor, "list")
        return result, 200
    else:
        return "not authorised", 401
# e.g. print(db_block(view_programs_exercises, logged_in_user, 2, 28))


## Registration / Login

def search_for_user(conn, cursor, email):
    cursor.execute("SELECT * FROM users")

    if cursor.rowcount == 0:
        return "No users found", 404
    else:
        results = results_to_dict(cursor, "list")
        for user in results:
            if user['email'] == email:
                return user
        return "User not found for email", 404
# print(db_block(search_for_user, "wellspaul554@gmail.com"))

# Register
def register_user(conn, cursor, name, email, user_password, profile_pic="", bio=""):
    
    user_check = db_block(search_for_user, email)

    if isinstance(user_check, dict):
        return "User already exists, please log in", 409

    if validate_email(email) and validate_password(user_password):
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (name, email, hashed_password))
        # above, returns id of the new user, can be accessed by cursor.fetchone()[0]

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

# e.g. print(db_block(register_user, "adam", "adam@gmail.com", "adam1989$"))

# log in
def log_in(conn, cursor, email, user_password):

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
# print(db_block(log_in, "wellspaul554@gmail.com", "wells1989%"))

# logout function
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

    


#logging in / out example
# logged_in_user = db_block(log_in, "wellspaul554@gmail.com", "wells1989%")
## # vasile password no longer working due to hashing issue logged_in_user = db_block(log_in, "vasile@gmail.com", "vasile1989$")

# logged_in_user = db_block(log_in, "frankie@gmail.com", "frank1989$")
# logged_in_user = db_block(log_in, "pantuda@gmail.com", ""password": "testing123%")


if __name__ == "__main__":
    logged_in_user, _ = db_block(log_in, "wellspaul554@gmail.com", "wells1989%")

    # logged_in_user, _ = db_block(log_in, "pantufa@gmail.com", "pantufa123%")

    print(logged_in_user)

    # DEV ONLY print(db_block(view_program, logged_in_user, 28, 10)) ## not working on postman, as getting need to log in first ...


