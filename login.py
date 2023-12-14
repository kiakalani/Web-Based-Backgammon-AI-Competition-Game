# Author: Kia Kalani
# This module handles the authorization to access
# the web application. In addition, it contains
# the model for the users inside the database.

from flask import current_app, Blueprint,\
    redirect, render_template, request
from flask_login import LoginManager, \
    UserMixin, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash,\
    check_password_hash
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError



class User(UserMixin, current_app.config['DB']['base']):
    """
    A class containing the model for the users
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

    def __init__(self, username, name, email, password) -> None:
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        super().__init__()

def init_login_manager():
    """
    A function to instantiate the login manager
    """

    # instantiating the login manager
    login_manager = LoginManager()

    login_manager.init_app(current_app)

    # Function that returns the corresponding user
    # from its id
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def register():
    """
    An endpoint for users to register to the website.
    :return: The server's response about the status of
    the registration
    """
    if current_user and current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = request.form
        # Receiving the parameters
        username = form.get('username')
        name = form.get('name')
        email = form.get('email')
        password = form.get('password')
        # Error checking the parameters
        if not username or not name or not email or not password:
            return '400 Bad request', 400
        
        # Creating the user instance
        user = User(username, name, email, generate_password_hash(password))
        db = current_app.config['DB']

        db['session'].add(user)

        # Ensuring that the user does not already exist
        try:
            db['session'].commit()
        except IntegrityError as e:
            reason = str(e.orig).split('.')[-1]
            return render_template('auth/register_message.html', alert_type='danger', 
                message=f'Failed to register user. Reason: This {reason} is already in use'), 400

        return render_template('auth/register_message.html', alert_type='success',
            message=f'Successfully registered user {username}. Please try to Sign In')

    return render_template('auth/register.html')


@bp.route('/signin', methods=['GET', 'POST'])
def login():
    """
    An endpoint for logging in.
    :return: The server's response
    """
    # Means they should not access this page. So we redirect them to home
    if current_user and current_user.is_authenticated:
        return redirect('/')
    # Logging in the user if the credentials are valid
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')
        if not username or not password:
            return 'Bad request', 400
        user = User.query.filter(User.username == username).first()
        if not user:
            return render_template('auth/register_message.html', alert_type='danger', message=f'User {username} Does not exist.')
        password_correct = check_password_hash(user.password, password)
        if password_correct:
            login_user(user)
            return redirect('/')
    return render_template('auth/login.html')

@bp.route('/signout', methods=['GET'])
def logout():
    """
    An endpoint for logging out the user
    """
    # Anonymous users are not logged in. So there would be no access.
    if current_user.is_anonymous:
        return redirect('/')
    logout_user()
    return redirect('/')
    