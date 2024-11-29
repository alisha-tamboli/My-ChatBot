from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf import FlaskForm
from bson.objectid import ObjectId
from bson import ObjectId 
import os

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Update with a strong key
app.config['MONGO_URI'] = 'mongodb://localhost:27017/chatbot_db'  # Replace with your MongoDB URI

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Flask-Login User class
class User(UserMixin):
    def __init__(self, user_id):
        self.id = str(user_id)

# Login manager loader function
@login_manager.user_loader
def load_user(user_id):
    try:
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(user_id)  # Return the User object
    except Exception as e:
        return None  # Return None if user_id is invalid
    

# WTForms for registration and login
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user = mongo.db.users.find_one({"username": username.data})
        if existing_user:
            raise ValidationError('This username is already taken.')
        

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"username": form.username.data})
        if existing_user:
            flash('This username is already taken.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data)
        user = {
            "username": form.username.data,
            "password": hashed_password
        }
        mongo.db.users.insert_one(user)
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    # if current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            user = mongo.db.users.find_one({"username": form.username.data})
            if user and check_password_hash(user['password'], form.password.data):
                login_user(User(str(user['_id'])))  # Convert ObjectId to string
                flash('Login successful!', 'success')
                return redirect(url_for('chat'))
            else:
                flash('Login failed. Check your username or password.', 'danger')

        return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_input = request.json.get('message', '')
        if not user_input:
            return jsonify({"response": "Please provide a message."})
        response = chatbot_response(user_input)
        return jsonify({"response": response})
    return render_template('chat.html')


# Chatbot logic
def chatbot_response(user_input):
    responses = {
        "hi": "Hello! How can I assist you?",
        "how are you?": "I'm just a bot, but I'm doing great!",
        "what's your name?": "I'm your friendly chatbot!",
        "bye": "Goodbye! Have a great day!",
        "tell me something about yourself?": "I am here to help you with anything you need."
    }
    return responses.get(user_input.lower(), "I'm not sure how to respond to that.")



if __name__ == '__main__':
    app.run(debug=True, port=5000)
