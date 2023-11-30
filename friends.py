from flask import Blueprint, request, render_template, redirect,\
    current_app
from flask_login import current_user
from sqlalchemy import String, Integer, Column, and_, or_
import login
import users

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
def get_blocked_users(user_id, query = None):
    users = []
    for b in Blocked.query.filter(Blocked.user == user_id).all():
        users.append(login.User.query.filter(login.User.id == b.blocked_user).first())
    if query:
        return [u for u in users if query.lower() in u.username.lower()]
    return users
def get_frequest_users(uid, query=None):
    users = []
    for r in FriendRequest.query.filter(FriendRequest.to_user == uid).all():
        users.append(login.User.query.filter(login.User.id == r.from_user).first())
    if query:
        return [u for u in users if query.lower() in u.username.lower()]
    return users
def choose_active_tab():
    resp = {
        'users': 'active' if request.args.get('uname') else '',
        'friends': 'active' if request.args.get('friendname') else '',
        'blocked': 'active' if request.args.get('blockedq') else '',
        'request': 'active' if request.args.get('requestq') else ''
    }
    for r in resp:
        if resp[r] == 'active':
            return resp
    resp['users'] = 'active'
    return resp
def choose_active_div():
    return {
        k: v if v != 'active' else 'show active' for k, v in choose_active_tab().items()
    }
@bp.route('/', methods=['GET'])
def messages():
    """
    Invoked when the user tries to see a list of
    their friends.
    """

    
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    query = request.args.get('uname')
    users = []
    if query:
        User = login.User
        blocked_by = Blocked.query.filter_by(blocked_user=current_user.id).all()
        users = User.query.filter(User.username.like(f'%{query}%')).all()
        users = [u for u in users if u.id not in blocked_by and u != current_user]
    friends = get_friends(current_user.id)
    fquery = request.args.get('friendname')
    if fquery:
        friends = [f for f in friends if fquery.lower() in f.username.lower()]
    blocked = get_blocked_users(current_user.id, request.args.get('blockedq'))
    requests = get_frequest_users(current_user.id, request.args.get('requestq'))
    return render_template('friends/index.html', user=current_user, users=users,
    friends=friends, blocked=blocked, requests=requests, active=choose_active_tab(),
    actived=choose_active_div())
