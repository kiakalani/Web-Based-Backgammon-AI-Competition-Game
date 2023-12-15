"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for handling some of
the operations that are related to users. These functionalities
include following/unfollowing and blocking/unblocking as well
as providing the users page.
"""

from flask import current_app, Blueprint, request, render_template,\
    redirect
from flask_login import current_user
from sqlalchemy import and_, or_

import friends
import message
bp = Blueprint('users', __name__, url_prefix='/users')


def get_follow_txt(user1: int, user2: int) -> str:
    """
    This function provides what text should be shown on the
    follow button.
    :param: user1: the id of the first user.
    :param: user2: the id of the second user(the current user
    who has opened the page of user1).
    :return: The text that should be shown on the button
    """

    FriendRequest = friends.FriendRequest

    if friends.users_are_friends(user1, user2):
        return 'unfollow'

    elif FriendRequest.query.filter(
        and_(
            FriendRequest.from_user == user1,
            FriendRequest.to_user == user2
        )
    ).first():
        return 'accept'

    elif FriendRequest.query.filter(
        and_(
            FriendRequest.from_user == user2,
            FriendRequest.to_user == user1
        )
    ).first():
        return 'requested'

    return 'follow'


@bp.route('/<uid>', methods=['GET'])
def user_page(uid: str):
    """
    Provides the details about the user as well
    as the buttons for following or blocking
    the user.
    """

    if not uid.isdigit():
        return 'Bad Request', 400

    uid = int(uid)
    if uid == current_user.id:
        # If the user tries to access their own page,
        # they should be redirected to their account's
        # page
        return redirect('/account')

    Blocked = friends.Blocked

    user = friends.login.User.query.filter_by(
        id=int(uid)
    ).first()

    if not user or Blocked.query.filter(
        and_(
            Blocked.blocked_user == current_user.id,
            Blocked.user == user.id
        )
    ).first():
        return 'Bad Request', 400

    follow_txt = get_follow_txt(uid, current_user.id)
    block_txt = 'unblock' if \
        friends.user_is_blocked(current_user.id, uid) else 'block'

    return render_template(
        'users/user.html',
        user=user,
        follow_txt=follow_txt,
        block_txt=block_txt
    )




@bp.route('/<uid>/follow', methods=['GET'])
def follow(uid: str):
    """
    Invoked when the follow button is pressed.
    Depending on the scenario, this function would
    make a friend request, remove the friend request,
    accept the friend request, or unfriends a user.
    :param: uid: The id of the destination user.
    """

    db_inst = current_app.config['DB']['session']

    if not uid.isdigit():
        return 'Bad request', 400

    # Making sure the user is valid first
    usr_inst = friends.login.User.query.filter_by(id=int(uid)).first()

    if not usr_inst:
        return 'Bad Request', 400

    uid = int(uid)
    Blocked = friends.Blocked
    # Making sure the user has not blocked the current user
    if Blocked.query.filter(
        or_(
            and_(
                Blocked.user == uid,
                Blocked.blocked_user == current_user.id
            ),
            and_(
                Blocked.user == current_user.id,
                Blocked.blocked_user == uid
            )
        )
    ).first():
        return 'Bad Request', 400

    if uid == current_user.id:
        # A user should not be able to follow themselves
        return 'Bad request', 400


    if friends.users_are_friends(uid, current_user.id):
        # In this scenario, friendship should be removed
        Friend = friends.Friend
        f_inst = Friend.query.filter(
            and_(
                Friend.user1 == uid,
                Friend.user2 == current_user.id
            )
        ).first()
    
        if not f_inst:
            f_inst = Friend.query.filter(
                and_(
                    Friend.user1 == current_user.id,
                    Friend.user2 == uid
                )
            ).first()
    
        db_inst.delete(f_inst)
        db_inst.commit()
        return redirect(f'/users/{uid}')

    # Checking to see whether this is for accepting the follow request
    FriendRequest = friends.FriendRequest
    other_side_req = FriendRequest.query.filter(
        and_(
            FriendRequest.from_user == uid,
            FriendRequest.to_user == current_user.id
        )
    ).first()

    # This means the user is accepting the follow request
    if other_side_req:
        # Remove the other side req
        db_inst.delete(other_side_req)
        f = friends.Friend(uid, current_user.id)
        db_inst.add(f)
    else: # this means the user is making a follow request
        f = FriendRequest(current_user.id, uid)
        curf = FriendRequest.query.filter(
            and_(
                FriendRequest.from_user == current_user.id,
                FriendRequest.to_user == uid
            )
        ).first()

        if curf:
            db_inst.delete(curf)
        else:
            db_inst.add(f)
            room = current_app.config['SOCKET_SIDS'].get(usr_inst.username)
            if room:
                current_app.config['SOCKETIO'].emit(
                    'count_freqs',
                    {'count': friends.count_friend_requests(usr_inst.id, True)},
                    room=room
                )
    db_inst.commit()
    return redirect(f'/users/{uid}')




    


# Trigger this when block/unblock button is
# pressed
@bp.route('/<uid>/block', methods=['GET'])
def block(uid: str):
    """
    This method would be responsible for blocking or unblocking
    a given user.
    :param: uid: The id of the user to be blocked.
    """

    if not uid.isdigit() or \
        not friends.login.User.query.filter_by(id=int(uid)).first():
        return 'Bad Request', 400

    Blocked = friends.Blocked
    if Blocked.query.filter(
        and_(
            Blocked.user == uid,
            Blocked.blocked_user == current_user.id
        )
    ).first():
        return 'Bad Request', 400

    uid = int(uid)
    db_inst = current_app.config['DB']['session']

    if not friends.user_is_blocked(current_user.id, uid):
        # Block the user
        block_inst = Blocked(current_user.id, uid)
        db_inst.add(block_inst)

        # if friendship exists, remove it
        Friend = friends.Friend
        friend_inst = Friend.query.filter(
            and_(
                Friend.user1 == uid,
                Friend.user2 == current_user.id
            )
        ).first()

        if not friend_inst:
            friend_inst = Friend.query.filter(
                and_(
                    Friend.user2 == uid,
                    Friend.user1 == current_user.id
                )
            ).first()

        if friend_inst:
            db_inst.delete(friend_inst)

        # if follow request made, remove it
        FriendReq = friends.FriendRequest
        f_inst = FriendReq.query.filter(
            and_(
                FriendReq.from_user == current_user.id,
                FriendReq.to_user == uid
            )
        ).first()

        if f_inst:
            db_inst.delete(f_inst)

        f_inst = FriendReq.query.filter(
            and_(
                FriendReq.to_user == current_user.id,
                FriendReq.from_user == uid
            )
        ).first()

        if f_inst:
            db_inst.delete(f_inst)

        # Delete all the messages exchanged between these
        # two users
        message.flush_messages(uid, current_user.id)
    else:
        # Unblock the user
        blocked_inst = Blocked.query.filter(
            and_(
                Blocked.user == current_user.id,
                Blocked.blocked_user == uid
            )
        ).first()
        if blocked_inst:
            db_inst.delete(blocked_inst)
    db_inst.commit()

    return redirect(f'/users/{uid}')
