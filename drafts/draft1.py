# end of 27/03 wed, pre admin checking and user id checking ....
import bcrypt
import binascii
import psycopg2
from utils.utils import database_connect, database_close, validate_email, validate_password

# helper functions 

## common CRUS operations

# for reading / selecting
def select_query(query, parameter=None):
    try:
        conn, cursor = database_connect()

        if parameter is not None:
            cursor.execute(query, (parameter,))
        else:
            cursor.execute(query)
        rows = cursor.fetchall() # fetched as tuples

        columns = [desc[0] for desc in cursor.description] # cursor.description contains info about columns in tuple form, so [0] = col name

        dictionaries = []
        for row in rows:
            item_dict = dict(zip(columns, row)) # makes a dictionary of columns, and rows, then adds to users
            dictionaries.append(item_dict)
        
        database_close(conn, cursor)
        
        return dictionaries
    
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 

# for deletion
def delete_query(query, parameter=None):
    try:
        conn, cursor = database_connect()

        if parameter is not None:
            cursor.execute(query, (parameter,))
        else:
            cursor.execute(query)
        
        conn.commit()
        print("Row successfully deleted")
        return
    
    except psycopg2.Error as e: 
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 

# for insertion
def insert_query(query, parameter=None):
    try:
        conn, cursor = database_connect()

        if parameter is not None:
            cursor.execute(query, (parameter,))
        else:
            cursor.execute(query)
        
        conn.commit()
        print("Row successfully inserted")
        return
    
    except psycopg2.Error as e: 
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 

# for updating
def update_query(query, parameter = None):
    try:
        conn, cursor = database_connect()

        if parameter is not None:
            cursor.execute(query, (parameter,))
        else:
            cursor.execute(query)
        
        conn.commit()
        print("Row successfully updated")
        return
    
    except psycopg2.Error as e: 
        print(f"An error occurred: {e}")
        conn.rollback()
        return None 

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback() 
        return None 

## Users / Profiles

# adding new users / registering
def register_user(name, email, user_password, profile_pic, bio):

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

    results = select_query("SELECT * FROM users WHERE email = %s", (email)) # select_query returns a list so need to access 1st dictionary i.e. selected user

    if results is None:
        print("user not found")
    else:
        user = results[0]
        stored_hashed_password = user["password"]

        # coming back as a hex string, so need to convert it into binary for bcrypt.checkpw ...
        hex_string = stored_hashed_password.replace("\\x", "")
        binary_hash = binascii.unhexlify(hex_string)
        print(f'binary hashed password {binary_hash}')

        # Hashing the user's provided password for comparison
        user_guess_encoded_password = user_password.encode('utf-8')
        print(f'user_guess_hashed_password: {user_guess_encoded_password}')

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

## testing 
# logging in / out example
logged_in_user = None

logged_in_user = log_in("frank@gmail.com", "frank1989$")

print(logged_in_user["email"])

logged_in_user = logout(logged_in_user)

print(logged_in_user)

# users = select_query("SELECT * FROM users;")
# print(users)

# select_users = select_query("SELECT * FROM users WHERE name='Paul'")
# print(select_users)


