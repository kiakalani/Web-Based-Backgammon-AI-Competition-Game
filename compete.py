from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import current_user
from flask import current_app
from ai_management import AI
import base64
import os
from sqlalchemy import Integer, String, Column
import json
from sqlalchemy.exc import IntegrityError
from ai_management import AI
from login import User
import json


class Competition(current_app.config['DB']['base']):
    """
    A class containing the model for the users
    """
    __tablename__ = 'competition'
    id = Column(Integer, primary_key=True)
    winner_name = Column(String)
    loser_name = Column(String)
    winner_owner = Column(Integer)
    loser_owner = Column(Integer)
    gameplay = Column(String)

    def __init__(self, winner_name, loser_name, winner_owner, loser_owner, gameplay) -> None:
        self.winner_name = winner_name
        self.loser_name = loser_name
        self.winner_owner = winner_owner
        self.loser_owner = loser_owner
        self.gameplay = gameplay
        super().__init__()



def compete(owner1, ai1, owner2, ai2):
    first_ai = AI.query.filter(AI.owner == owner1, AI.name == ai1).first()
    second_ai = AI.query.filter(AI.owner == owner2, AI.name == ai2).first()
    db_session = current_app.config['DB']['session']
    if first_ai == None or second_ai == None:
        print(owner1)
        print(ai1)
        print(second_ai)
        return 'AI Not found', 404
    if Competition.query.filter(
        (Competition.winner_name == ai1 and Competition.loser_name == ai2 and Competition.winner_owner == owner1 and Competition.loser_owner == owner2) or
        (Competition.winner_name == ai2 and Competition.loser_name == ai1 and Competition.winner_owner == owner2 and Competition.loser_owner == owner1)
    ).first() != None:
        # Checking to make sure competition never took place before
        return 'Competition already took place', 400
    
    first_source = base64.decodebytes(bytes(first_ai.source, encoding='utf8')).decode()
    second_source = base64.decodebytes(bytes(second_ai.source, encoding='utf8')).decode()
    with open('game_logic/player1.py', 'w') as file:
        file.write(first_source)
        file.close()
    with open('game_logic/player2.py', 'w') as file:
        file.write(second_source)
        file.close()
    print('Building the docker image...')
    os.system('docker build -t competition ./game_logic')
    print('Success; now running to find the winner.')
    result_str = os.popen('docker run competition').read()
    game_result = base64.b64encode(
        bytes(result_str, encoding='utf-8')
    ).decode()
    res = json.loads(result_str)
    names = {'winner': res['winner'], 'loser': None}
    names['loser'] = res['colors']['white'] \
        if res['colors']['white'] != names['winner'] else res['colors']['black']
    owners = {
        'winner': first_ai.owner if first_ai.name == names['winner'] else second_ai.owner,
        'loser': None
    }
    owners['loser'] = first_ai.owner if first_ai.name == names['loser'] else second_ai.owner

    competition_inst = Competition(names['winner'], names['loser'], owners['winner'], owners['loser'], game_result)

    db_session = current_app.config['DB']['session']
    os.system("docker rmi --force competition")
    try:
        db_session.add(competition_inst)
        db_session.commit()
    except IntegrityError:
        return 'Competition already took place', 400
    
    return 'Success', 200
    

bp = Blueprint('compete', __name__, url_prefix='/compete')

@bp.route('/', methods=['GET', 'POST'])
def messages():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    user_id = current_user.id

    if request.method == 'POST':
        user_req = request.form
        for i in ['your_ai', 'oponent', 'oponent_ai']:
            if i not in user_req:
                return 'Bad request', 400
        oponent_id = User.query.filter(User.username == request.form['oponent']).first()
        if not oponent_id:
            return 'Bad request', 400
        oponent_id = oponent_id.id
        return compete(user_id, user_req['your_ai'], oponent_id, user_req['oponent_ai'])
    your_ais = AI.query.filter(AI.owner == user_id).all()
    your_ais = [i.name for i in your_ais]

    other_ais = AI.query.filter(AI.owner != user_id).all()
    other_ais = [(i.name, i.owner) for i in other_ais]
    return render_template('compete/index.html', user=current_user, your_ais=your_ais, other_ais=other_ais)

@bp.route('/ais', methods=['POST'])
def provide_ai_names():
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    data = json.loads(request.data.decode())
    if not data.get('name'):
        return 'Bad Request', 400
    if data['name'] == current_user.username:
        return jsonify([])
    uid = User.query.filter(User.username == data['name']).first()
    if uid == None:
        return jsonify([])
    uid = uid.id
    ais = AI.query.filter(AI.owner == uid).all()
    ais = [a.name for a in ais]
    return jsonify(ais)

@bp.route('/gameplay/<id>', methods=['GET'])
def watch_game(id):
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    if not id.isdigit():
        return 'Bad request', 400
    id = int(id)
    competition = Competition.query.filter(Competition.id == id).first()
    if not competition:
        return 'Bad request', 400
    resp = base64.decodebytes(bytes(competition.gameplay, encoding='utf-8')).decode()
    print(resp)
    return render_template('compete/gameplay.html', gameplay=competition.gameplay)