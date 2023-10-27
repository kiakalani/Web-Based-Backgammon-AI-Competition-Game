from flask import Blueprint, render_template
from flask_login import current_user
from game_logic.compete import compete

bp = Blueprint('home', __name__, url_prefix='/')


@bp.route('/')
def index():
    compete(1, 'Player 1', 2, 'Player 2')
    return render_template('home/index.html', user=current_user)
