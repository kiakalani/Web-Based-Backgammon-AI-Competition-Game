from flask import current_app
from ai_management import AI
import base64
import os
from sqlalchemy import Integer, String, Column
import json
from sqlalchemy.exc import IntegrityError

class Competition(current_app.config['DB']['base']):
    """
    A class containing the model for the users
    """
    __tablename__ = 'competition'
    winner_name = Column(String, primary_key=True)
    loser_name = Column(String, primary_key=True)
    winner_owner = Column(Integer, primary_key=True)
    loser_owner = Column(Integer, primary_key=True)
    gameplay = Column(String)

    def __init__(self, winner_name, loser_name, winner_owner, loser_owner, gameplay) -> None:
        self.winner_name = winner_name
        self.loser_name = loser_name
        self.winner_owner = winner_owner
        self.loser_owner = loser_owner
        self.gameplay = gameplay
        super().__init__()


def ai_logic_is_valid(code: str) -> bool:
    pass


def compete(owner1, ai1, owner2, ai2):
    first_ai = AI.query.filter(AI.owner == owner1, AI.name == ai1).first()
    second_ai = AI.query.filter(AI.owner == owner2, AI.name == ai2).first()
    db_session = current_app.config['DB']['session']
    if first_ai == None or second_ai == None:
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
    
    # result_obj = Competition()

