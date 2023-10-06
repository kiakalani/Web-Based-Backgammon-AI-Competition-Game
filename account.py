from flask import Blueprint, render_template, redirect, request, current_app
from flask_login import current_user
from ai_management import AI

bp = Blueprint('account', __name__, url_prefix='/account')

def get_ais(uid):
    return current_app.config['DB']['session'].query(AI).filter(AI.owner == uid)

@bp.route('/', methods=['GET'])
def account():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    return render_template('account/index.html', user=current_user, ais=get_ais(current_user.id))

