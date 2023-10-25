from flask import current_app
from ai_management import AI
import base64
import os
from sqlalchemy import Integer, String, Column


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

    def __init__(self, name, owner, source) -> None:
        self.name = name
        self.owner = owner
        self.source = source
        super().__init__()



def compete(owner1, ai1, owner2, ai2):
    first_ai = AI.query.filter(AI.owner == owner1, AI.name == ai1).first()
    second_ai = AI.query.filter(AI.owner == owner2, AI.name == ai2).first()
    if first_ai == None or second_ai == None:
        print('Invalid')
        return None
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
    print(result_str)
    os.system("docker rmi --force competition")

