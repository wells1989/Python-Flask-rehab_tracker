# possible refactoring to reduce code? 
# to do: implement admin_checking for certain operations (anything with exercises is okay, but any other table operations are limited to admin true or user_id matching - also remove ON DELETE cascade etc for programs-exercises, for exercises_id Foreign key)

import bcrypt
import binascii
import psycopg2
from utils.utis import database_connect, database_close, validate_email, validate_password

# helper functions
def admin_check(logged_in_user):
    return True if logged_in_user["is_admin"] == True else False


# returns either a list of dictionaries if "list" type, or a single dictionary if "ind" type
def results_to_dict(cursor, type):
    if type == "list":
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] # cursor.description contains info about columns in tuple form, so [0] = col name

        dictionaries = []
        for row in rows:
            item_dict = dict(zip(columns, row)) # makes a dictionary of columns, and rows, then adds to users
            dictionaries.append(item_dict)
        return dictionaries
    elif type == "ind":
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))



## common CRUD operations

# open select available to anyone for querying ...
def select_query(query, parameters=None, restricted=False, logged_in_user=None):
    try:
        conn, cursor = database_connect()

        if (restricted and admin_check(logged_in_user) or not restricted): # i.e. is restricted user needs to be an admin to proceed
            cursor.execute(query, parameters) # instead of query, (parameters) to allow data cleaning and prevent SQL injections

            dictionaries = results_to_dict(cursor, "list")
            
            database_close(conn, cursor)
            
            return dictionaries
        else:
            print("not authorized")
            return
           
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 
"""
e.g's
print(select_query("SELECT * FROM exercises"))
print(select_query("SELECT * FROM users", None, True, logged_in_user))

"""

# selecting specific user
def select_user(id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user to view
            cursor.execute("SELECT * FROM users WHERE id = %s", (id,))

            if cursor.rowcount == 0:
                print("No instance found")
                return database_close(conn, cursor)

            result = results_to_dict(cursor, "ind")
            database_close(conn, cursor)
            return result
        else:
            print("not authorized")

        return database_close(conn, cursor)
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. select_user(17, logged_in_user)
    

def update_user(query, id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user
            cursor.execute("UPDATE users " + query + " WHERE id = %s", (id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("update successful")
            else:
                print("No instance found")

        else:
            print("not authorized")

        return database_close(conn, cursor)
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. update_user("SET name = 'D-man'", 17, logged_in_user)


def delete_user(id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == id: # needs to be admin or same user
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("deletion successful")
            else:
                print("No instance found")

        else:
            print("not authorized")

        return database_close(conn, cursor)
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. delete_user(16, logged_in_user)
    

# userProfiles
def select_profile(id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or id == logged_in_user["id"]:
            cursor.execute("SELECT * FROM userprofiles WHERE user_id = %s", (id,))
            if cursor.rowcount == 0:
                print("No instance found")
                return database_close(conn, cursor)
            result = results_to_dict(cursor, "ind")

            database_close(conn, cursor)
            return result
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. print(select_profile(17, logged_in_user))

def update_profile(query, user_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
            cursor.execute("UPDATE userprofiles " + query + " WHERE user_id = %s", (user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("Update successful")
            else:
                print("No instance found")

        else:
            print("not authorized")

        return database_close(conn, cursor)
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. update_profile("SET bio = 'I am from the netherlands!!!'", 17, logged_in_user)


## Exercises
# view all print(select_query("SELECT * FROM exercises"))
# print(select_query("SELECT * FROM users", None, True, logged_in_user))

def create_exercise(logged_in_user, name, image):
    try:
        conn, cursor = database_connect()
        user_id = logged_in_user["id"]
        cursor.execute("INSERT INTO exercises (name, image, creator_id) VALUES (%s, %s, %s)", (name, image, user_id))
        conn.commit()
        print("insertion successful")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. create_exercise(logged_in_user, "squats", "sample image2")


def update_exercise(query, creator_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == creator_id:
            cursor.execute("UPDATE exercises " + query + " AND creator_id = %s", (creator_id,)) # restricted exercises that user created
            conn.commit()
            if cursor.rowcount > 0:
                print("Update successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. update_exercise("SET name = 'bench' WHERE name = 'squats'", 28, logged_in_user)


def delete_exercise(query, creator_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == creator_id:
            cursor.execute("DELETE FROM exercises " + query + " AND creator_id = %s", (creator_id,)) # restricted exercises that user created
            conn.commit()
            if cursor.rowcount > 0:
                print("deletion successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. delete_exercise("WHERE name = 'squats'", 28, logged_in_user)


## programs
def create_program(logged_in_user, start_date, end_date, rating, description):
    try:
        conn, cursor = database_connect()
        user_id = logged_in_user["id"]

        cursor.execute("INSERT INTO programs (user_id, start_date, end_date, rating, description) VALUES(%s, %s, %s, %s, %s)", (user_id, start_date, end_date, rating, description))
        conn.commit()
        print("new program created")
        return database_close(conn, cursor)
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. create_program(logged_in_user, "2000-10-20", "2000-12-20", 3, "summer_regime")


def select_programs(logged_in_user, user_id):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
            cursor.execute("SELECT * FROM programs WHERE user_id = %s", (user_id,))
            if cursor.rowcount == 0:
                print("No instance found")
                return database_close(conn, cursor)
            results = results_to_dict(cursor, "list")

            database_close(conn, cursor)
            return results
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. print(select_programs(logged_in_user, 28))



def update_program(query, user_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
            cursor.execute("UPDATE programs " + query + " AND user_id = %s", (user_id,)) # restricted exercises that user created
            conn.commit()
            if cursor.rowcount > 0:
                print("Update successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. update_program("SET rating = 1 WHERE id = 5", 19, logged_in_user)


def delete_program(program_id, user_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
            cursor.execute("DELETE FROM programs WHERE id = %s AND user_id = %s", (program_id, user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("deletion successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. delete_program(3, 28, logged_in_user)


## program_exercises
def add_exercise_to_program(program_id, exercise_id, notes, sets, reps, rating, logged_in_user):
    try:
        conn, cursor = database_connect()

        cursor.execute("SELECT * FROM programs WHERE id = %s", (program_id,))
        program = cursor.fetchone() 
        cursor.execute("SELECT * FROM exercises WHERE id = %s", (exercise_id,))
        exercise = cursor.fetchone()
        
        if not program:
            print("program not found")
            return database_close(conn, cursor)
        if not exercise:
            print("exercise not found")
            return database_close(conn, cursor)

        if program[1] == logged_in_user["id"] or admin_check(logged_in_user):
            exercise_name = exercise[1]
            user_id = logged_in_user["id"]
            cursor.execute("INSERT into programs_exercises (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating))

            conn.commit()
            print("exercise added to program")
        else:
            print("not authorised")

        return database_close(conn, cursor)
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# add_exercise_to_program(2, 2, "trying it for now", 3, 10, 1, logged_in_user)


def update_exercise_program(program_id, user_id, exercise_id, logged_in_user, query):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
            cursor.execute("UPDATE programs_exercises " + query + " WHERE exercise_id = %s AND program_id = %s AND user_id = %s", (exercise_id, program_id, user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("Update successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. update_exercise_program(2, 28, 2, logged_in_user, "SET notes = 'went well so far'")


def delete_exercise_from_program(exercise_id, program_id, user_id, logged_in_user):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or logged_in_user["id"] == user_id:
            cursor.execute("DELETE FROM programs_exercises WHERE exercise_id = %s AND program_id = %s AND user_id = %s", (exercise_id, program_id, user_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print("deletion successful")
            else:
                print("No instance found")
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. delete_exercise_from_program(7, 2, 28, logged_in_user)


# shows all the users exercise_programs
def view_users_exercise_programs(logged_in_user, user_id):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
            cursor.execute("SELECT * FROM programs_exercises WHERE user_id = %s", (user_id,))
            if cursor.rowcount == 0:
                print("No instance found")
                return database_close(conn, cursor)
            results = results_to_dict(cursor, "list")

            database_close(conn, cursor)
            return results
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. print(view_users_exercise_programs(logged_in_user, 19))


def view_specific_exercise_program(logged_in_user, program_id, user_id):
    try:
        conn, cursor = database_connect()

        if admin_check(logged_in_user) or user_id == logged_in_user["id"]:
            cursor.execute("SELECT * FROM programs_exercises WHERE user_id = %s AND program_id = %s", (user_id, program_id))
            if cursor.rowcount == 0:
                print("No instance found")
                return database_close(conn, cursor)
            result = results_to_dict(cursor, "ind")

            database_close(conn, cursor)
            return result
        else:
            print("not authorised")

        return database_close(conn, cursor)

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None
# e.g. print(view_specific_exercise_program(logged_in_user, 2, 28))

## Users / Profiles

# adding new users / registering
def register_user(name, email, user_password, profile_pic="", bio=""):

    try:
        conn, cursor = database_connect()
    
        if validate_email(email) and validate_password(user_password):
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (name, email, hashed_password))
            # above, returns id of the new user, can be accessed by cursor.fetchone()[0]
                
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO userProfiles (user_id, profile_pic, bio) VALUES (%s, %s, %s)", (user_id, profile_pic, bio))

            conn.commit()

        elif not validate_email(email):
            print("Invalid email address")
        elif not validate_password(user_password):
            print("password must be 8 characters long, and include alphabetical, numerical and 1 special character")

        print(f'user {name} successfully created')
        return database_close(conn, cursor)

    except psycopg2.Error as e: # postgres common errors
        print(f"An error occurred: {e}")
        conn.rollback() # reverts database i.e. eliminating any changes the query made prior to the error
        return None 

    except Exception as e: # general errors
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 
    

# log in
def log_in(email, user_password):
    conn, cursor = database_connect()

    results = select_query("SELECT * FROM users WHERE email = %s", (email,)) # select_query returns a list so need to access 1st dictionary i.e. selected user

    if results is None:
        print("user not found")
    else:
        user = results[0]
        stored_hashed_password = user["password"]

        # coming back as a hex string, so need to convert it into binary for bcrypt.checkpw ...
        hex_string = stored_hashed_password.replace("\\x", "")
        binary_hash = binascii.unhexlify(hex_string)

        # Hashing the user's provided password for comparison
        user_guess_encoded_password = user_password.encode('utf-8')

        if bcrypt.checkpw(user_guess_encoded_password, binary_hash):
            logged_in_user = user
            return logged_in_user
        else:
            print("passwords don't match")

        return database_close(conn, cursor)

# logout function
def logout(logged_in_user):
    if not logged_in_user:
        return
    
    logged_in_user = None
    return logged_in_user


# logging in / out example

logged_in_user = None
# logged_in_user = log_in("wellspaul554@gmail.com", "wells1989%")
logged_in_user = log_in("frank@gmail.com", "frank1989$")


# print(select_query("SELECT * FROM programs WHERE id = 2", "ind"))
