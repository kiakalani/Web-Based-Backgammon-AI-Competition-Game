from flask import Blueprint, request, render_template, redirect
from flask_login import current_user


bp = Blueprint('friends', __name__, url_prefix='/friends')

@bp.route('/', methods=['GET'])
def messages():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    
    return render_template('friends/index.html', user=current_user)
