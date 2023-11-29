"""
Author: Kia Kalani
Student ID:101145220
A module for managing AI uploading and removal.
"""
import base64
import re

from flask import Blueprint, redirect, current_app, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_login import current_user
from sqlalchemy import Column, String, Integer, delete, or_, and_

import compete

bp = Blueprint('ai', __name__, url_prefix='/ai')

class AI(current_app.config['DB']['base']):
    """
    A class containing the model for the users
    """
    __tablename__ = 'ai'

    owner = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    source = Column(String)

    def __init__(self, name: str, owner: int, source: str) -> None:
        """
        Constructor
        """
        self.name = name
        self.owner = owner
        self.source = source
        super().__init__()


def file_is_valid(extension: str, text: str) -> bool:
    """
    This function indicates whether the uploaded file
    is valid.
    :param: extension: The file extension
    :param: text: The text components of the file
    :return: True if the file is valid; otherwise false.
    """
    # TODO: Run a competition and make sure the AI is functioning
    # as expected
    if extension != 'py':
        return False
    if text.count('import') != 1 or 'print' in text:
        return False
    # To check whether the AI makes valid moves or not
    code_valid =  compete.code_is_valid(text)
    print('Validity is', code_valid)
    return code_valid

def get_ai_name(code: str) -> str:
    """
    Getter for the name of the AI from the
    source code.
    :return: the name of the AI
    """
    pattern = re.compile(r'super\(\)\.__init__\((?P<ai_name>.+)\)')
    m = None
    for line in code.splitlines():
        line = line.strip()
        m = pattern.match(line)
        if m:
            return m.groupdict()['ai_name']
    return None
        
def write_ai_to_db(owner: int, name: str, code: str) -> bool:
    """
    This function writes the ai into the database.
    :param: The id of the owner user
    :param: name: The name of the AI
    :param: code: The source code of the AI
    :return: True if the writing process was
    successful; otherwise false
    """
    name = get_ai_name(code)
    # Means invalid name is provided
    if not name or len(name) <= 2:
        return False
    name = name[1:-1]
    if AI.query.filter(and_(AI.owner == owner, AI.name == name)).first():
        # This would mean that this AI already exists
        return False
    new_ai = AI(name, owner, base64.b64encode(bytes(code, encoding='utf-8')).decode())
    current_app.config['DB']['session'].add(new_ai)
    current_app.config['DB']['session'].commit()
    return True





@bp.route('/', methods=['GET'])
def search_page():
    """
    Displays the AIs currently available to compete against
    """
    return "", 200

@bp.route('/upload', methods=['POST'])
def upload_ai():
    """
    Invoked when the post request is made to the server
    for uploading a new AI.
    """
    # This means user has not authenticated. So the request is invalid
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    # If file is missing, provide a bad request response.
    if 'file' not in request.files:
        return 'Bad Request', 400
    file_extension = request.files['file'].filename.split('.')[-1].lower()
    contents = ''

    # If encoding is not utf-8, the file would be invalid
    try:
        contents = request.files['file'].stream.read().decode()
    except UnicodeDecodeError:
        return "Bad Request", 400
    
    print(request.form)
    print(file_extension)
    if file_is_valid(file_extension, contents):
        if write_ai_to_db(current_user.id, request.form['ai_name'], contents):
            return 'Success', 200
        return 'Bad Request', 400
    
    print(request.form)

    return 'Bad Request', 400

@bp.route('/remove', methods=['POST'])
def remove_ai():
    """
    Invoked when the user tries to remove one of their AIs.
    """
    
    if current_user.is_anonymous:
        return redirect('/auth/signin')
    if 'removed_ai' not in request.form:
        return 'Bad Request', 404
    removed = request.form['removed_ai']
    
    session = current_app.config['DB']['session']
    obj = AI.query.filter_by(name=removed).first()
    if obj is None:
        return 'Bad Request', 400

    # Removing the competition that the AI participated in
    Competition = compete.Competition
    items = session.query(Competition).filter(
        or_(
            and_((Competition.winner_name == removed), (Competition.winner_owner == current_user.id)),
            and_(Competition.loser_name == removed, Competition.loser_owner == current_user.id)
        )
    ).all()
    for i in items:
        session.delete(i)
    session.delete(obj)
    session.commit()
    return redirect('/account')

