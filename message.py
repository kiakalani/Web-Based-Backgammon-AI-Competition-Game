"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for handling all of
the functionalities related to messaging and live
updating the messages through socket.
"""

from datetime import datetime

from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from flask import current_app
from sqlalchemy import Column, String, text,\
    Integer, and_, or_, Boolean, not_, update


from login import User
import friends


bp = Blueprint('message', __name__, url_prefix='/message')

class Message(current_app.config['DB']['base']):
    """
    The database model for messages
    """
    __tablename__ = 'message'
    sender = Column(Integer)
    receiver = Column(Integer)
    text = Column(String)
    date = Column(String)
    seen = Column(Boolean)
    msg_id = Column(Integer, primary_key=True)


    def __init__(self, sender, receiver, text, date):
        """
        Constructor for setting the necessary values
        """
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.date = date
        self.seen = False

def set_seen(sender: int, receiver: int) -> None:
    """
    Sets the seen flag to true upon invoking
    :param: sender: the sender's id
    :param: receiver: the receiver's id
    """

    db_inst = current_app.config['DB']['session']
    db_inst.execute(
        update(Message).where(
            and_(
                Message.sender == sender,
                Message.receiver == receiver
            )
        ).values(seen=True)
    )

    db_inst.commit()

def count_unseen_messages(sender, receiver) -> int:
    """
    A function to count how many unseen messages exist from
    the specific user identified with their id.
    :param: sender: The person who sent messages that are unseen
    :param: receiver: The person who is receiving the message
    """

    items = Message.query.filter(
        and_(
            and_(
                Message.sender == sender,
                Message.receiver == receiver
            ),
            not_(Message.seen)
        )
    ).all()
    return len(items)

def get_count_all_unseen(receiver: int, inc=False) -> str:
    """
    A method to provide the count of all unseen messages for
    a given user.
    """

    unseens = len(Message.query.filter(
        and_(
            Message.receiver == receiver,
            not_(Message.seen)
        )
    ).all())
    if inc:
        unseens += 1
    if unseens > 99:
        return '+99'
    return str(unseens)

@current_app.config['SOCKETIO'].on('message')
def send_msg(data):
    """
    A function for updating messaging live and storing it into the database
    :param: data: the dictionary containing the information
    client has sent over to the server.
    """

    # Necessary components about the message
    receiver = data.get('receiver')
    message = data.get('message')
    sender = current_user.id
    send_date = str(datetime.now())
    rec_usr = User.query.filter(User.username == receiver).first()

    # Live updating the message to the receiver
    if current_app.config['SOCKET_SIDS'].get(receiver):
        current_app.config['SOCKETIO'].emit(
            'receive',
            {
                'sender': sender,
                'message': message,
                'date': send_date,
                'unread': count_unseen_messages(sender, rec_usr.id) + 1,
            },
            room=current_app.config['SOCKET_SIDS'][receiver]
        )
        current_app.config['SOCKETIO'].emit(
            'unreads',
            {
                'all_unreads': get_count_all_unseen(rec_usr.id, True)
            },
            room=current_app.config['SOCKET_SIDS'][receiver]
        )
    # get the user corresponding to receiver
    # Storing the message in the database
    db_instance = current_app.config['DB']['session']
    msg_obj = Message(sender, rec_usr.id, message, send_date)
    db_instance.add(msg_obj)
    db_instance.commit()

@current_app.config['SOCKETIO'].on('seen')
def set_the_seen(data):
    """
    Invoked when users open the unread messages.
    :param: data: the data sent over by the client.
    """
    sender = data['sender']
    set_seen(sender, current_user.id)
    # we have to update this on seen as well
    current_app.config['SOCKETIO'].emit(
        'unreads',
        {
            'all_unreads': get_count_all_unseen(current_user.id)
        },
        room=current_app.config['SOCKET_SIDS'][current_user.username]
    )


@bp.route('/', methods=['GET'])
def messages():
    """
    The index page for the given user to see who messaged
    them.
    """
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    friend_collection = friends.get_friends(current_user.id)
    count_unseen = {
        i.id: count_unseen_messages(i.id, current_user.id)\
            for i in friend_collection
    }
    return render_template('message/index.html', user=current_user, 
                           users=friend_collection, unseen = count_unseen)

@bp.route('/<uid>')
def message_by_id(uid):
    """
    Opens the messaging room for given two users.
    :param: uid: the id of the destination user.
    """

    if current_user.is_anonymous:
        return redirect('/')

    if not uid.isdigit():
        return 'Bad Request', 400

    uid = int(uid)
    dest_user = User.query.filter(User.id == uid).first()

    if not dest_user:
        return 'Bad Request', 400

    if uid == current_user.id:
        return redirect('/message')

    messages = Message.query.filter(
        or_(
            and_(Message.sender == current_user.id, Message.receiver == uid),
            and_(Message.sender == uid, Message.receiver == current_user.id)
        )
    )

    return render_template(
        'message/message_page.html',
        messages=messages,
        receiver_name=dest_user.username,
        receiver_id=dest_user.id,
        user=current_user
    )
