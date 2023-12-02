from flask import current_app, Blueprint, request, render_template,\
    redirect
from flask_login import current_user
import friends
import message
bp = Blueprint('users', __name__, url_prefix='/users')
from sqlalchemy import and_, or_

# Include all the users who did not block the user
# Make query working
@bp.route('/', methods=['GET'])
def index():
    # Getting the objects
    query = request.args.get('query')
    users = []
    if query:
        Blocked = friends.Blocked
        User = friends.login.User
        blocked_by = Blocked.query.filter_by(blocked_user=current_user.id).all()
        users = User.query.filter(User.username.like(f'%{query}%')).all()
        users = [u for u in users if u.id not in blocked_by and u != current_user]
    return render_template('/users/index.html', users=users)

def get_follow_txt(user1: int, user2: int) -> str:

    # current_user is user2
    FriendRequest = friends.FriendRequest
    if friends.users_are_friends(user1, user2):
        return 'unfollow'
    elif FriendRequest.query.filter(
        and_(FriendRequest.from_user == user1, FriendRequest.to_user == user2)
    ).first():
        return 'accept'
    elif FriendRequest.query.filter(
        and_(FriendRequest.from_user == user2, FriendRequest.to_user == user1)
    ).first():
        return 'requested'
    return 'follow'


# Show the specific user and allow to block
# or follow the user
@bp.route('/<uid>', methods=['GET'])
def user_page(uid):
    if not uid.isdigit():
        return 'Bad Request', 400
    uid = int(uid)
    if uid == current_user.id:
        return 'Bad Request', 400
    Blocked = friends.Blocked
    user = friends.login.User.query.filter_by(id=int(uid)).first()
    if not user or Blocked.query.filter(
        and_(Blocked.blocked_user == current_user.id, Blocked.user == user.id)
    ).first():
        return 'Bad Request', 400
    follow_txt = get_follow_txt(uid, current_user.id)
    block_txt = 'unblock' if friends.user_is_blocked(current_user.id, uid) else 'block'

    return render_template('users/user.html', user=user, follow_txt=follow_txt, block_txt=block_txt)




# Trigger this when follow/unfollow button is
# pressed. If the second person is pressing this,
# it would mean that the person has accepted
# the follow request
@bp.route('/<uid>/follow', methods=['GET'])
def follow(uid):
    db_inst = current_app.config['DB']['session']

    # Making sure the user is valid first
    usr_inst = friends.login.User.query.filter_by(id=int(uid)).first()
    if not uid.isdigit() or \
        not usr_inst:
        return 'Bad Request', 400
    uid = int(uid)
    Blocked = friends.Blocked
    # Making sure the user has not blocked the current user
    if Blocked.query.filter(
        or_(
            and_(Blocked.user == uid, Blocked.blocked_user == current_user.id),
            and_(Blocked.user == current_user.id, Blocked.blocked_user == uid)
        )
    ).first():
        return 'Bad Request', 400
    if uid == current_user.id:
        return 'Bad request', 400
    if friends.users_are_friends(uid, current_user.id):
        Friend = friends.Friend
        f_inst = Friend.query.filter(and_(Friend.user1 == uid, Friend.user2 == current_user.id)).first()
        if not f_inst:
            f_inst = Friend.query.filter(and_(Friend.user1 == current_user.id, Friend.user2 == uid)).first()
        db_inst.delete(f_inst)
        db_inst.commit()
        return redirect(f'/users/{uid}')
    # Checking to see whether this is for accepting the follow request
    FriendRequest = friends.FriendRequest
    other_side_req = FriendRequest.query.filter(
        and_(FriendRequest.from_user == uid, FriendRequest.to_user == current_user.id)
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
            and_(FriendRequest.from_user == current_user.id, FriendRequest.to_user == uid)
        ).first()
        if curf:
            db_inst.delete(curf)
        else:
            db_inst.add(f)
            print('here', friends.count_friend_requests(usr_inst.id, True))
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
def block(uid):
    if not uid.isdigit() or \
        not friends.login.User.query.filter_by(id=int(uid)).first():
        return 'Bad Request', 400
    Blocked = friends.Blocked
    if Blocked.query.filter(
        and_(Blocked.user == uid, Blocked.blocked_user == current_user.id)
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
            and_(Friend.user1 == uid, Friend.user2 == current_user.id)
        ).first()
        if not friend_inst:
            friend_inst = Friend.query.filter(
                and_(Friend.user2 == uid, Friend.user1 == current_user.id)
            ).first()
        if friend_inst:
            db_inst.delete(friend_inst)

        # if follow request made, remove it
        FriendReq = friends.FriendRequest
        f_inst = FriendReq.query.filter(
            and_(FriendReq.from_user == current_user.id, FriendReq.to_user == uid)
        ).first()
        if f_inst:
            db_inst.delete(f_inst)
        f_inst = FriendReq.query.filter(
            and_(FriendReq.to_user == current_user.id, FriendReq.from_user == uid)
        ).first()
        if f_inst:
            db_inst.delete(f_inst)
        message.flush_messages(uid, current_user.id)
    else:
        # Unblock the user
        blocked_inst = Blocked.query.filter(
            and_(Blocked.user == current_user.id, Blocked.blocked_user == uid)
        ).first()
        if blocked_inst:
            db_inst.delete(blocked_inst)
    db_inst.commit()
    return redirect(f'/users/{uid}')
