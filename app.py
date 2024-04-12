from flask import Flask, jsonify, request, url_for
from db import *
from flask import session, render_template, redirect
from utils.utils import process_request
from datetime import datetime
from api import home, users, exercises, programs, details

app = Flask(__name__)
app.register_blueprint(home.main_bp)
app.register_blueprint(users.users_bp)
app.register_blueprint(exercises.exercises_bp)
app.register_blueprint(programs.programs_bp)
app.register_blueprint(details.details_bp)

