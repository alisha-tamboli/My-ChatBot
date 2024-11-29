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
    def __init__(self, user_id,username=None):
        self.id = str(user_id)
        self.username = username 

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_id=str(user_data["_id"]), username=user_data.get("username"))
    return None


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


# Register route
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
    form = LoginForm()
    if form.validate_on_submit():
        # Find the user in the database
        user = mongo.db.users.find_one({"username": form.username.data})
        
        if user and check_password_hash(user['password'], form.password.data):
            # Login the user
            login_user(User(str(user['_id'])))  # Convert ObjectId to string
            
            # Check if the user is an admin
            if user.get('role') == 'admin':
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                flash('User login successful!', 'success')
                return redirect(url_for('chat'))  # Redirect to user chat page
        else:
            flash('Login failed. Check your username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/admin/add_intent', methods=['GET', 'POST'])
@login_required

def add_intent():
    if current_user.username != "admin":  # Ensure only admin can access
        flash("Access Denied.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        intent_name = request.form.get('intent_name')
        training_phrases = request.form.get('training_phrases', '').split(',')
        responses = request.form.get('responses', '').split(',')

        # Validate input
        if not intent_name or not training_phrases or not responses:
            flash("All fields are required.", "danger")
            return redirect(url_for('add_intent'))

        # Insert into MongoDB
        intent = {
            "intent_name": intent_name.strip(),
            "training_phrases": [phrase.strip() for phrase in training_phrases],
            "responses": [response.strip() for response in responses]
        }
        mongo.db.intents.insert_one(intent)
        flash("Intent added successfully!", "success")
        return redirect(url_for('add_intent'))

    return render_template('add_intent.html')



@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_input = request.json.get('message', '').strip().lower()

        if not user_input:
            return jsonify({"response": "Please provide a message."})

        # Query MongoDB for matching intent
        intent = mongo.db.intents.find_one({
            "training_phrases": {"$in": [user_input]}
        })

        # Return a random response from the matched intent
        if intent:
            from random import choice
            response = choice(intent['responses'])
        else:
            response = "I'm not sure how to respond to that."

        return jsonify({"response": response})

    return render_template('chat.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False, port=5000)
