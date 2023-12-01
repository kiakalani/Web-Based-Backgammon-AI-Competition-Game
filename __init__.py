"""
Author: Kia Kalani
Student ID: 101145220
This module puts the code together
and is responsible for executing
the application
"""

import os

from flask import Flask, request
from flask_socketio import SocketIO
from flask_login import current_user
from db import load_db, create_db


def create_app():
    """
    A function for creating and setting up the
    flask application
    """

    # Setting up the flask app
    app = Flask(
        __name__,
        template_folder='temp',
        static_folder='src'
    )
    socketio = SocketIO(app)
    with app.app_context():
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            print(
                'Please provide the "SECRET_KEY" environment variable'
            )
            exit(-1)
        # Setting up the configurations
        app.config['SECRET_KEY'] = secret_key
        app.config['SOCKETIO'] = socketio
        app.config['SOCKET_SIDS'] = {}
        app.config['MAX_CONTENT_LENGTH'] = 128 * 1024
        
        # Setting up the database
        create_db(app)

        # Registering the blueprints from
        # other modules
        import home
        app.register_blueprint(home.bp)
        import login
        login.init_login_manager()
        app.register_blueprint(login.bp)
        import account
        app.register_blueprint(account.bp)
        import message
        app.register_blueprint(message.bp)
        import friends
        app.register_blueprint(friends.bp)
        import compete
        app.register_blueprint(compete.bp)
        import ai_management
        app.register_blueprint(ai_management.bp)
        import users
        app.register_blueprint(users.bp)

        # Setting up the socket for messaging
        @socketio.on('connect')
        def connection(auth):
            if current_user.is_anonymous:
                return
            app.config['SOCKET_SIDS'][current_user.username] = request.sid
            socketio.emit(
                'unreads',
                {
                    'all_unreads': message.get_count_all_unseen(current_user.id)
                },
                room=app.config['SOCKET_SIDS'][current_user.username]
            )

        @socketio.on('disconnect')
        def disconnect():
            if current_user.is_anonymous:
                return
            user_sids = app.config['SOCKET_SIDS']
            if current_user.username in user_sids:
                del user_sids[current_user.username]
    
        
        

    load_db(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.config['SOCKETIO'].run(app)
