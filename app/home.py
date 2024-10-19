#app/home.py
 
from flask import Blueprint, render_template

home = Blueprint('home', __name__)

# Home page
@home.route('/')
def homepage():
    return render_template('home.html')