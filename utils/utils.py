import os
import re
import psycopg2
from dotenv import load_dotenv
import bcrypt
import binascii

load_dotenv()

# helper functions

def env_variables_generation():
    database = os.getenv('database')
    db_user = os.getenv('user')
    db_password = os.getenv('password')
    db_host = os.getenv('host')
    db_port = os.getenv('port')

    return database, db_user, db_password, db_host, db_port

def database_connect():
    database, db_user, db_password, db_host, db_port = env_variables_generation()
    conn = psycopg2.connect(database=database, user=db_user, password=db_password, host=db_host, port=db_port)
    cursor = conn.cursor()

    return conn, cursor

def database_close(conn, cursor):
    cursor.close()
    conn.close()

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    """ ^[a-zA-Z0-9._%+-] = 1 or more from a-z A-Z 0-9 and spec characters ._%+-
        @ matches @ symbol
        [a-zA-Z0-9.-]+ = matches 1 or more characters (e.g. domain part of email)
        \. = escaped . character
        [a-zA-Z]{2,} = matches 2 or more letters of a-z or A-Z
        $ = end of the string
    """
    return re.match(email_regex, email)

def validate_password(password):

    password_regex = '^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[^a-zA-Z0-9]).{8,}$'
    """
    ^ = start of the string
    (?=.*[0-9]) = at least 1 number from 0-9
    (?=.*[a-zA-Z]) = at least 1 letter
    (?=.*[^a-zA-Z0-9]) = at least 1 character NOT a-z or A-Z or 1-9 (^ makes it negative)
    .{8,} = matches any chatacrer at least 8 or more times, i.e. min length 8
    $ = end of string
    """
    return re.match(password_regex, password)

## helper functions
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


## wrapper functions
# wrapper for db_functions to handle database connection etc
def db_block(function, *args, **kwargs):
    result = None
    try:
        conn, cursor = database_connect()
        result = function(conn, cursor, *args, **kwargs)
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals() and conn: # searching local variables for conn (to prevent error if conn = None)
            conn.rollback()
            return e, 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            return e, 400
    finally:
        database_close(conn, cursor)
    
    if result is not None:
        return result
 

# wrapper for the update API requests
def update_wrapper(request, allowed_fields, id_to_update, update_function, logged_in_user):
    data = request.get_json()

    fields = {}
    for field in allowed_fields:
        if field in data:
            fields[field] = data[field]
    
    query = "SET "
    num_fields = len(fields)
    for index, (key, value) in enumerate(fields.items()):
        if value is not None:
            query += f"{key} = %s"
            if index < num_fields - 1:
                query += ", "

    values = [value for value in fields.values() if value is not None]

    result = db_block(update_function, query, id_to_update, values, logged_in_user)

    return result


def process_request(request, *field_names):
    if request.form:
        data = request.form
    else:
        data = request.get_json()

    values = {}
    for field_name in field_names:
        values[field_name] = data.get(field_name)

    return values
    