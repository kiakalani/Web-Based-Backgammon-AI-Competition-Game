from flask import current_app, Blueprint, request, render_template,\
    redirect
from flask_login import current_user
import friends
bp = Blueprint('users', __name__, url_prefix='/users')

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
        FriendRequest.from_user == user1 and FriendRequest.to_user == user2
    ).first():
        return 'accept'
    elif FriendRequest.query.filter(
        FriendRequest.from_user == user2 and FriendRequest.to_user == user1
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
    Blocked = friends.Blocked
    user = friends.login.User.query.filter_by(id=int(uid)).first()
    if not user or Blocked.query.filter(
        Blocked.blocked_user == current_user.id and Blocked.user == user.id
    ).first():
        return 'Bad Request', 400
    follow_txt = get_follow_txt(uid, current_user.id)
    print(friends.users_are_friends(uid, current_user.id))
    print(uid, 'and', current_user.id)
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
    if not uid.isdigit() or \
        not friends.login.User.query.filter_by(id=int(uid)).first():
        return 'Bad Request', 400
    uid = int(uid)
    Blocked = friends.Blocked
    # Making sure the user has not blocked the current user
    if Blocked.query.filter(
        Blocked.user == uid and Blocked.blocked_user == current_user.id
    ).first():
        return 'Bad Request', 400
    if friends.users_are_friends(uid, current_user.id):
        Friend = friends.Friend
        print('here1')
        print(friends.users_are_friends(uid, current_user))
        f_inst = Friend.query.filter(Friend.user1 == uid and Friend.user2 == current_user.id).first()
        print(f_inst)
        if not f_inst:
            f_inst = Friend.query.filter(Friend.user1 == current_user.id and Friend.user2 == uid).first()
        print('here2')
        print(f_inst)
        db_inst.delete(f_inst)
        db_inst.commit()
        print('here3')
        return redirect(f'/users/{uid}')
    # Checking to see whether this is for accepting the follow request
    FriendRequest = friends.FriendRequest
    other_side_req = FriendRequest.query.filter(
        FriendRequest.from_user == uid and FriendRequest.to_user == current_user.id
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
            FriendRequest.from_user == current_user.id and FriendRequest.to_user == uid
        ).first()
        if curf:
            db_inst.delete(curf)
        else:
            db_inst.add(f)
    db_inst.commit()
    return redirect(f'/users/{uid}')




    


# Trigger this when block/unblock button is
# pressed
@bp.route('/<uid>/block', methods=['GET'])
def block(uid):
    pass
