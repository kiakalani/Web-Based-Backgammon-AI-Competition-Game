"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for running the competition between
the given two AIs and store the outcome of the competition.
"""
from flask import Blueprint, request, render_template, redirect, jsonify
from flask_login import current_user
from flask import current_app
import base64
import os
from sqlalchemy import Integer, String, Column, and_, or_
import json
from sqlalchemy.exc import IntegrityError
import ai_management
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
        """
        Constructor
        :param: winner_name: The name of the AI who won the competition
        :param: loser_name: The name of the AI who lost the competition
        :param: winner_owner: The id of the owner of the AI who won the competition
        :param: loser_owner: The id of the owner of the AI who lost the competition
        :param: gameplay: Base64 encoded Jsonified string that contains all of the moves
        made and relevant information that needs to be displayed
        :return: None
        """
        self.winner_name = winner_name
        self.loser_name = loser_name
        self.winner_owner = winner_owner
        self.loser_owner = loser_owner
        self.gameplay = gameplay
        super().__init__()



def compete(owner1: int, ai1: str, owner2: int, ai2: str) -> (str, int):
    """
    A function to run the competition between the given two AIs.
    :param: owner1: the owner id of the first AI
    :param: ai1: the name of the AI that belongs to owner1
    :param: owner2: the owner id of the second AI
    :param: ai2: the name of the AI that belongs to owner2
    """
    AI = ai_management.AI
    # fetching the corresponding AIs from the database
    first_ai = AI.query.filter(AI.owner == owner1, AI.name == ai1).first()
    second_ai = AI.query.filter(AI.owner == owner2, AI.name == ai2).first()
    db_session = current_app.config['DB']['session']
    # Making sure the AIs are valid
    if first_ai == None or second_ai == None:
        print(owner1)
        print(ai1)
        print(second_ai)
        return 'AI Not found', 404

    # If this instance exists, then it would mean that the competition already took place
    if Competition.query.filter(
        or_(
            and_(
                and_(Competition.winner_owner == owner1, Competition.loser_owner == owner2),
                and_(Competition.winner_name == ai1, Competition.loser_name == ai2)
            ),
            and_(
                and_(Competition.winner_name == ai2, Competition.loser_name == ai1),
                and_(Competition.winner_owner == owner2, Competition.loser_owner == owner1)
            )
        )
    ).first() != None:
        # Checking to make sure competition never took place before
        return 'Competition already took place', 400
    
    # Putting the source code for both competitors into files for creating a container
    first_source = base64.decodebytes(bytes(first_ai.source, encoding='utf8')).decode()
    second_source = base64.decodebytes(bytes(second_ai.source, encoding='utf8')).decode()
    with open('game_logic/player1.py', 'w') as file:
        file.write(first_source)
        file.close()
    with open('game_logic/player2.py', 'w') as file:
        file.write(second_source)
        file.close()
    # Creating a container for running the competition between the two AIs
    print('Building the docker image...')
    os.system('docker build -t competition ./game_logic')
    print('Success; now running to find the winner.')
    result_str = os.popen('docker run competition').read()
    game_result = base64.b64encode(
        bytes(result_str, encoding='utf-8')
    ).decode()
    try:
        res = json.loads(result_str)
    except json.JSONDecodeError:
        return 'Error with competition. this is due to a faulty implementation for AI', 400

    # Getting the winner and loser names
    names = {'winner': res['winner'], 'loser': None}
    names['loser'] = res['colors']['white'] \
        if res['colors']['white'] != names['winner'] else res['colors']['black']

    # Getting the owners
    owners = {
        'winner': first_ai.owner if first_ai.name == names['winner'] else second_ai.owner,
        'loser': None
    }
    owners['loser'] = first_ai.owner if first_ai.name == names['loser'] else second_ai.owner


    # Creating the competition instance for writing to the database
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
    """
    Provoked when user wants to compete against another user's
    AI.
    """
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    user_id = current_user.id

    if request.method == 'POST':
        # This means user tried to run a competition
        user_req = request.form
        for i in ['your_ai', 'oponent', 'oponent_ai']:
            if i not in user_req:
                return 'Bad request', 400
        oponent_id = User.query.filter(User.username == request.form['oponent']).first()
        if not oponent_id:
            return 'Bad request', 400
        oponent_id = oponent_id.id
        # Running the competition and returning the result
        return compete(user_id, user_req['your_ai'], oponent_id, user_req['oponent_ai'])
    AI = ai_management.AI

    # Getting all of the user and other users AIs for displaying the competition
    # options to the user
    your_ais = AI.query.filter(AI.owner == user_id).all()
    your_ais = [i.name for i in your_ais]

    other_ais = AI.query.filter(AI.owner != user_id).all()
    other_ais = [(i.name, i.owner) for i in other_ais]
    return render_template('compete/index.html', user=current_user, your_ais=your_ais, other_ais=other_ais)

@bp.route('/ais', methods=['POST'])
def provide_ai_names():
    """
    A method for receiving all of the AIs for the given
    username
    """
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
    AI = ai_management.AI
    ais = AI.query.filter(AI.owner == uid).all()
    ais = [a.name for a in ais]
    return jsonify(ais)

@bp.route('/gameplay/<id>', methods=['GET'])
def watch_game(id):
    """
    A method that provides the necessary data
    for replaying the moves that AIs made for
    the given competition by ID.
    :param: id: the id of the competition that
    took place.
    """
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    if not id.isdigit():
        return 'Bad request', 400
    id = int(id)
    competition = Competition.query.filter(Competition.id == id).first()
    if not competition:
        return 'Bad request', 400
    return render_template('compete/gameplay.html', gameplay=competition.gameplay)