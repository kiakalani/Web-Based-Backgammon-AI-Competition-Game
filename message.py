from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from flask import current_app
from sqlalchemy import Column, String, text
from datetime import datetime
from login import User

bp = Blueprint('message', __name__, url_prefix='/message')

class Message(current_app.config['DB']['base']):

    __tablename__ = 'message'
    sender = Column(String, primary_key=True)
    receiver = Column(String, primary_key=True)
    text = Column(String)
    date = Column(String)

    def __init__(self, sender, receiver, text, date):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.date = date

@current_app.config['SOCKETIO'].on('message')
def send_msg(data):
    """
    A function for updating messaging live and storing it into the database
    """
    # Necessary components about the message
    receiver = data.get('receiver')
    message = data.get('message')
    sender = current_user.username
    send_date = str(datetime.now())

    # Live updating the message to the receiver
    if current_app.config['SOCKET_SIDS'].get(receiver):
        current_app.config['SOCKETIO'].emit(
            'receive', {'sender': sender, 'message': message, 'date': send_date},
            room=current_app.config['SOCKET_SIDS'][receiver]
        )
    
    # Storing the message in the database
    db_instance = current_app.config['DB']['session']
    msg_obj = Message(sender, receiver, message, send_date)
    db_instance.add(msg_obj)
    db_instance.commit()


@bp.route('/', methods=['GET'])
def messages():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    all_msg = current_app.config['DB']['session'].execute(text('SELECT id, username FROM user;')).all()
    print(all_msg)
    
    return render_template('message/index.html', user=current_user, 
                           users=all_msg)
@bp.route('/<id>')
def message_by_id(id):
    # Todo: Implement it so the user would be able to message through here.
    pass