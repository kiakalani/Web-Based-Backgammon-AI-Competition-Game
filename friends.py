from flask import Blueprint, request, render_template, redirect,\
    current_app
from flask_login import current_user
from sqlalchemy import String, Integer, Column, and_, or_
import login

"""
General idea:
1. Friend request through a post method
2. Acceptance would remove the friend request and
add the ids as friends
3. Blocking an account would imply removing them
from both friend requests and friends
4. Unblocking just removes it from the blocked table
"""
bp = Blueprint('friends', __name__, url_prefix='/friends')

class Friend(current_app.config['DB']['base']):
    """
    A table to specify a user's friends
    """

    __tablename__ = 'friend'
    user1 = Column(Integer, primary_key=True)
    user2 = Column(Integer, primary_key=True)
    def __init__(self, user1: int, user2: int) -> None:
        self.user1 = user1
        self.user2 = user2

class FriendRequest(current_app.config['DB']['base']):
    """
    A table for friend requests
    """
    __tablename__ = 'friendrequest'
    from_user = Column(Integer, primary_key=True)
    to_user = Column(Integer, primary_key=True)
    def __init__(self, from_user: int, to_user: int) -> None:
        self.from_user = from_user
        self.to_user = to_user

def users_are_friends(user1: int, user2: int) -> bool:
    """
    A helper function for finding out whether two user ids
    are friends
    :param: user1: the first user
    :param: user2: the second user
    :return: true if two users are friends, otherwise false
    """
    return Friend.query.filter(
        or_(
            and_(Friend.user1 == user1, Friend.user2 == user2),
            and_(Friend.user2 == user1, Friend.user1 == user2)
        )
    ).first() != None

class Blocked(current_app.config['DB']['base']):
    """
    A table for storing the blocked users
    """
    __tablename__ = 'blocked'
    user = Column(Integer, primary_key=True)
    blocked_user = Column(Integer, primary_key=True)
    def __init__(self, user: int, blocked_user: int) -> None:
        self.user = user
        self.blocked_user = blocked_user

def user_is_blocked(user: int, blocked: int) -> bool:
    return Blocked.query.filter(
        and_(Blocked.user == user, Blocked.blocked_user == blocked)
    ).first() != None

def get_friends(user_id: int) -> [Friend]:
    """
    A getter method for the friends of the given user id.
    :param: user_id: an integer that indicates the id of
    the user.
    :return: An array of User objects that are friends with
        the given user
    """
    db_session = current_app.config['DB']['session']
    # Getting the ids
    friends = [(i.user1 if i.user1 != user_id else i.user2)\
        for i in db_session.query(Friend).filter(
            or_(Friend.user1 == user_id, Friend.user2 == user_id)
        ).all()
    ]
    # Getting the corresponding user object for each id
    return [
        db_session.query(login.User).filter(login.User.id == i).first()\
            for i in friends
    ]

@bp.route('/', methods=['GET'])
def messages():
    """
    Invoked when the user tries to see a list of
    their friends.
    """
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    
    return render_template('friends/index.html', user=current_user)
