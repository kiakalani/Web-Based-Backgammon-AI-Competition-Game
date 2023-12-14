"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for providing the my account
page to the logged in user.
"""

from flask import Blueprint, render_template, redirect, request, current_app
from flask_login import current_user

from ai_management import AI

bp = Blueprint('account', __name__, url_prefix='/account')

def get_ais(uid: int) -> [AI]:
    """
    A function to provide all of the implemented AIs by the
    given user id.
    :param: uid: an integer that specifies the id of the
    given user.
    :return: a collection of AIs that were implemented
    by the user.
    """
    return current_app.config['DB']['session'].query(AI).filter(AI.owner == uid)

@bp.route('/', methods=['GET'])
def account():
    """
    Handling the /account endpoint.
    """
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    return render_template('account/index.html', user=current_user, ais=get_ais(current_user.id))

