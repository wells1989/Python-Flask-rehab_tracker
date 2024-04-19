# Flask Sports Rehab Tracker Application

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Project Notes](#project-notes)

## Description
This application incorporates 3 tier architecture by utilizing a Postgres database, a Flask Application for the API and a JavaScript / HTML based UI with tailwind styling.

To improve security both client-side and server-side type / field checking was used in addition to data authentication with Flask sessions. Additionally, in the database layer a variety of robust practices were followed to prevent malicious access.

The front end incorporates a minimialist yet dynamic UI by combining JavaScript functionality with tailwind styling throughout. The site allows the user to perform CRUD operations / download their rehab programs seemlessly, and provides detailed error handling throughout.  

**Front-End Areas: HTML and jinja2 template syntax, tailwindCSS, JavaScript and DOM manipulation, event-driven-programming.**

**Back-End Areas: Flask API incorporation, secure CRUD operations, python data manipulation and retrieval, email sending functionality to improve user experience.**

## Installation

1. Clone the repository:

   ```bash
   gh repo clone wells1989/rehab_tracker

2. Install dependencies:

   ```bash
   pip install -r requirements.txt 

2. Database copying (in psql CLI)
- Install PostgresSQL and create a database
- Connect to your database using the path to the file **Rehab_backup.sql** in a psql terminal (replace the below details with the details from your database)

   ```psql
   psql -U <username> -h <host> -p <port> -d <database_name> -f /path/to/rehab_backup.sql

- Create a .env file (at the same level as app.py) with the required environmental variables, e.g.


   ```
   database=<your_database_name>
   user=<your_database_username>
   password=<your_database_password>
   host=<your_database_host>
   port=<your_database_port>
   ```

4. Run the application

    ```bash
    python run.py
    ```

## Usage
### UI

- **Initial Pages (Register / Login Forms):**

![Screenshot (700)](https://github.com/wells1989/Full-stack-blog/assets/122035759/d98ab2a3-282b-47ae-8134-19773adfbdae)

- **Homepage:**

![Screenshot (701)](https://github.com/wells1989/Full-stack-blog/assets/122035759/297e522f-b229-48f1-b3a0-e3ffd4caa870)


- **Creating new Programs:**

![Screenshot (703)](https://github.com/wells1989/Full-stack-blog/assets/122035759/fa33fef5-b0b3-418b-b5f5-8d75282e0986)


- **Profile Page:**

![Screenshot (699)](https://github.com/wells1989/Full-stack-blog/assets/122035759/cc31c40b-7242-4d0f-abfe-8de0aa716f4e)

- **Profile adjustment form:**

![Screenshot (696)](https://github.com/wells1989/Full-stack-blog/assets/122035759/ba87e522-7ac0-4c49-8c39-0ff5a57edf22)


- **Program_exercise manipulation / downloading:**

![Screenshot (697)](https://github.com/wells1989/Full-stack-blog/assets/122035759/ca4f2e34-ec75-40d5-9428-95cf98a967ac)


- **Extra functionality:**

![Screenshot (698)](https://github.com/wells1989/Full-stack-blog/assets/122035759/590421af-0d97-4aa0-b83d-ffdb814162aa)



### API Routes (See rehab flask app.postman_collection.json ...)

 Method | API Route                           | Description                         
-------------------------------------------------------------------------

| POST   | http://localhost:5000/register    | Register a new user                      
| POST   | http://localhost:5000/login       | Login                                                                       
| POST   | http://localhost:5000/logout      | Logout  
                                         
| GET    | http://localhost:5000/users/:id    | Get a user                                       
| PUT    | http://localhost:5000/users/:id    | Update user                                      
| DELETE | http://localhost:5000/users/:id    | Delete user

| GET    | http://localhost:5000/users/deleted|Delete user view   
                               
| GET    | http://localhost:5000/users/profiles/:user_id | View user profile                   
| PUT    | http://localhost:5000/users/profiles/:user_id | User profile update                    
| GET    | http://localhost:5000/users/:user_id/password_reset | Reset password
                  
| GET    | http://localhost:5000/programs/:user_id | Get users programs                         
| POST   | http://localhost:5000/programs/:user_id | Creating new program
| GET    | http://localhost:5000/programs/program/:user_id/:program_id | Viewing a program

| PUT    | http://localhost:5000/programs/:program_id | Updating a program

| DELETE | http://localhost:5000/programs/:program_id | Deleting a program
 
| GET    | http://localhost:5000/exercises | Get all exercises                        
| POST   | http://localhost:5000/exercises | Posting new exercise                      
| DELETE | http://localhost:5000/exercises/:id | Deleting exercise  

               
| POST   | http://localhost:5000/details | Adding exercise to program 

| DELETE | http://localhost:5000/programs/:exercise_id/:program_id | Deleting exercises from programs  
| PUT    | http://localhost:5000/programs/:exercise_id/:program_id | Updating exercises in a program   


## Project Notes:
- The focus of the project was comprehensive, secure database integration in a 3 tier layered application. As such a lot of the database functionality was hardcoded to be able to better access / manipulate the data results elsewhere. An alternative approach would be to use ORM and SQLAlchemy, although the functional approach worked well with Raw SQL.
- If going past a prototype stage the app's use of images would have to be accounted for by using a mixture of Flask-Uploads and binary data to pass the files to and from the database in an efficient manner.
