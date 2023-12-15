"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for handling the
operations that correspond to friendship management.
"""

from flask import Blueprint, request, render_template, redirect,\
    current_app
from flask_login import current_user
from sqlalchemy import String, Integer, Column, and_, or_

import login
import users

bp = Blueprint('friends', __name__, url_prefix='/friends')

class Friend(current_app.config['DB']['base']):
    """
    A table to specify a user's friends
    """

    __tablename__ = 'friend'
    user1 = Column(Integer, primary_key=True)
    user2 = Column(Integer, primary_key=True)

    def __init__(self, user1: int, user2: int) -> None:
        """
        Constructor
        """
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
        """
        Constructor
        """
        self.from_user = from_user
        self.to_user = to_user

class Blocked(current_app.config['DB']['base']):
    """
    A table for storing the blocked users
    """
    __tablename__ = 'blocked'
    user = Column(Integer, primary_key=True)
    blocked_user = Column(Integer, primary_key=True)

    def __init__(self, user: int, blocked_user: int) -> None:
        """
        Constructor
        """
        self.user = user
        self.blocked_user = blocked_user

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
            and_(
                Friend.user1 == user1,
                Friend.user2 == user2
            ),
            and_(
                Friend.user2 == user1,
                Friend.user1 == user2
            )
        )
    ).first() != None


def user_is_blocked(user: int, blocked: int) -> bool:
    """
    This method would indicate whether the user is blocked
    by a given user.
    :param: user: the user who we suspect that they blocked 
        the given user.
    :param: blocked: The user who we want to check if they
        are blocked by a given user.
    :return: True if user has blocked the destined user;
    otherwise, false.
    """

    return Blocked.query.filter(
        and_(
            Blocked.user == user,
            Blocked.blocked_user == blocked
        )
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

def get_blocked_users(user_id: int, query = None) -> [login.User]:
    """
    This method provides all the users who are blocked
    by the given user id according to the query. If the
    query parameter is none, then this method would return
    all of the users who are blocked by the given user.
    :param:user_id: The user we want to get all of the blocked
        users by them.
    :param: query: A query parameter. This parameter would filter
    the result based on whether the username contains what was
    mentioned in the query.
    :return: An array of blocked users by the given user id.
    """

    users = []
    # Getting all the blocked users
    for b in Blocked.query.filter(
        Blocked.user == user_id
    ).all():
        users.append(
            login.User.query.filter(
                login.User.id == b.blocked_user
            ).first()
        )
    if query:
        # Filtering the users by query
        return [
            u for u in users if query.lower() in u.username.lower()
        ]
    return users

def get_frequest_users(uid: int, query=None) -> [login.User]:
    """
    This method provides all of the users who have made a friend
    request to a given user. The query is responsible for filtering
    the name of those users by their username.
    :param: uid: The user id we want to check for the friend requests
    made to them.
    :param: query: a string for filtering the name of those who
    have made a friend request to a given user.
    :return: An array of users who have made friend request to the
    given user.
    """

    users = []
    for r in FriendRequest.query.filter(
        FriendRequest.to_user == uid
    ).all():
        # Adding all the users who made friend request to the user
        users.append(
            login.User.query.filter(
                login.User.id == r.from_user
            ).first()
        )

    if query:
        # Filtering users by the query
        return [
            u for u in users if query.lower() in u.username.lower()
        ]

    return users

def choose_active_tab() -> dict:
    """
    This method is responsible for providing the class parameters
    of client's HTML code. It essentially would make certain tab
    active by default.
    :return: a dictionary containing the necessary configurations.
    """

    # All of the tabs for user's friend management page
    resp = {
        'users': 'active' if request.args.get('uname') else '',
        'friends': 'active' if request.args.get('friendname') else '',
        'blocked': 'active' if request.args.get('blockedq') else '',
        'request': 'active' if request.args.get('requestq') else ''
    }

    # Making sure there is an active tab
    for r in resp:
        if resp[r] == 'active':
            return resp

    resp['users'] = 'active'

    return resp

def choose_active_div() -> dict:
    """
    This method is similar to <code>choose_active_tab</code> with the exception
    of it corresponding to the div that is for the chosen tab.
    :return: a dictionary containing the necessary configurations.
    """

    return {
        k: v if v != 'active' else 'show active' for k, v in choose_active_tab().items()
    }

def count_friend_requests(uid: int, inc=False):
    """
    This method is used for providing the number that would
    be shown once the user receives a new friend request.
    If number is more than 99, then +99 would be shown.
    :param: uid: The user's id
    :param: inc: Indicates whether we should increment
    the value before returning this function. This would be
    needed especially since when this gets triggered, the
    message is not added to the database yet.
    :return: a string indicating how many messages a user
    has received.
    """

    count = len(
        FriendRequest.query.filter(
            FriendRequest.to_user == uid
        ).all()
    )

    if inc:
        count += 1

    return str(count) if count <= 99 else '+99'

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
        # These users should not be visible to the
        # current user
        blocked_by = Blocked.query.filter_by(
            blocked_user=current_user.id
        ).all()

        # Getting all of the users that match the query
        # and are not the user
        users = User.query.filter(
            User.username.like(f'%{query}%')
        ).all()
        users = [
            u for u in users if u.id not in blocked_by and u != current_user
        ]

    # handling the friends with the query
    friends = get_friends(current_user.id)
    fquery = request.args.get('friendname')
    if fquery:
        friends = [
            f for f in friends if fquery.lower() in f.username.lower()
        ]

    # getting the blocked users by current user
    blocked = get_blocked_users(
        current_user.id,
        request.args.get('blockedq')
    )

    # getting the users who made friend request to the
    # current user
    requests = get_frequest_users(
        current_user.id,
        request.args.get('requestq')
    )

    return render_template(
        'friends/index.html',
        user=current_user,
        users=users,
        friends=friends,
        blocked=blocked,
        requests=requests,
        active=choose_active_tab(),
        actived=choose_active_div()
    )
