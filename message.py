from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from flask import current_app
from sqlalchemy import Column, String, text, Integer
from datetime import datetime
from login import User

bp = Blueprint('message', __name__, url_prefix='/message')

class Message(current_app.config['DB']['base']):

    __tablename__ = 'message'
    sender = Column(String)
    receiver = Column(String)
    text = Column(String)
    date = Column(String)
    msg_id = Column(Integer, primary_key=True)


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
    # dropping the current user as an option
    all_msg = [a for a in all_msg if a[1] != current_user.username]
    
    return render_template('message/index.html', user=current_user, 
                           users=all_msg)
@bp.route('/<id>')
def message_by_id(id):
    if current_user.is_anonymous:
        return redirect('/')
    db_session = current_app.config['DB']['session']
    dest_user = db_session.execute(text(f'SELECT username FROM user WHERE id=:x'), {"x": id}).fetchall()
    if not dest_user:
        return 'Bad Request', 400
    dest_user = dest_user[0][0]
    if dest_user == current_user.username:
        return redirect('/message')
    # return dest_user
    messages = db_session.execute(text(f"SELECT * FROM message WHERE (sender='{current_user.username}' AND receiver='{dest_user}') or (sender='{dest_user}' and receiver='{current_user.username}');")).all()


    return render_template('message/message_page.html', messages=messages, receiver_name=dest_user, receiver_id=id)
