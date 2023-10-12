import os

from flask import Flask, request
from flask_socketio import SocketIO
from flask_login import current_user
from db import load_db, create_db
def create_app():
    app = Flask(__name__, template_folder='temp', static_folder='src')
    socketio = SocketIO(app)
    with app.app_context():
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            print('Please provide the "SECRET_KEY" environment variable')
            exit(-1)
        app.config['SECRET_KEY'] = secret_key
        app.config['SOCKETIO'] = socketio
        app.config['SOCKET_SIDS'] = {}
        
        create_db(app)
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
        @socketio.on('connect')
        def connection(auth):
            if current_user.is_anonymous:
                return
            app.config['SOCKET_SIDS'][current_user.username] = request.sid
            print('request sid is', request.sid)
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
