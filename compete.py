from flask import Blueprint, request, render_template, redirect
from flask_login import current_user


bp = Blueprint('compete', __name__, url_prefix='/compete')

@bp.route('/', methods=['GET'])
def messages():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    
    return render_template('compete/index.html', user=current_user)
