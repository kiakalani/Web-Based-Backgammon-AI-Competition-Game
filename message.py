from flask import Blueprint, request, render_template, redirect
from flask_login import current_user
from flask import current_app
from sqlalchemy import Column, String, text, Integer, and_, or_, Boolean, not_, update
from datetime import datetime
from login import User
import friends
bp = Blueprint('message', __name__, url_prefix='/message')

class Message(current_app.config['DB']['base']):

    __tablename__ = 'message'
    sender = Column(Integer)
    receiver = Column(Integer)
    text = Column(String)
    date = Column(String)
    seen = Column(Boolean)
    msg_id = Column(Integer, primary_key=True)


    def __init__(self, sender, receiver, text, date):
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
    db_inst.execute(update(Message).where(and_(Message.sender == sender, Message.receiver == receiver)).values(seen=True))

    db_inst.commit()

def count_unseen_messages(sender, receiver) -> int:
    """
    A function to count how many unseen messages exist from
    the specific user identified with their id.
    :param: sender: The person who sent messages that are unseen
    :param: receiver: The person who is receiving the message
    """
    items = Message.query.filter(
        and_(and_(Message.sender == sender, Message.receiver == receiver), not_(Message.seen))
    ).all()
    return len(items)

@current_app.config['SOCKETIO'].on('message')
def send_msg(data):
    """
    A function for updating messaging live and storing it into the database
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
            'receive', {'sender': sender, 'message': message, 'date': send_date, 'unread': count_unseen_messages(sender, rec_usr.id) + 1},
            room=current_app.config['SOCKET_SIDS'][receiver]
        )
    # get the user corresponding to receiver
    # Storing the message in the database
    db_instance = current_app.config['DB']['session']
    print(message)
    msg_obj = Message(sender, rec_usr.id, message, send_date)
    db_instance.add(msg_obj)
    db_instance.commit()

@current_app.config['SOCKETIO'].on('seen')
def set_the_seen(data):
    sender = data['sender']
    set_seen(sender, current_user.id)


@bp.route('/', methods=['GET'])
def messages():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    friend_collection = friends.get_friends(current_user.id)
    count_unseen = {i.id: count_unseen_messages(i.id, current_user.id) for i in friend_collection}
    print(count_unseen)
    return render_template('message/index.html', user=current_user, 
                           users=friend_collection, unseen = count_unseen)
@bp.route('/<uid>')
def message_by_id(uid):
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
    messages = Message.query.filter(or_(
        and_(Message.sender == current_user.id, Message.receiver == uid),
        and_(Message.sender == uid, Message.receiver == current_user.id)
    ))
    return render_template('message/message_page.html', messages=messages, receiver_name=dest_user.username, receiver_id=dest_user.id, user=current_user)
