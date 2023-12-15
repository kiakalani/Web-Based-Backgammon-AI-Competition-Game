"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for rendering the
home page of the application
"""

from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    """
    Provides the main menu of the application
    """

    return render_template('home/index.html', user=current_user)
