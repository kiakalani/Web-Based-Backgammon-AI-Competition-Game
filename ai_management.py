"""
Author: Kia Kalani
Student ID:101145220
A module for managing AI uploading and removal.
"""
import base64

from flask import Blueprint, redirect, current_app, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_login import current_user
from sqlalchemy import Column, String, Integer, delete
import re


bp = Blueprint('ai', __name__, url_prefix='/ai')

class AI(current_app.config['DB']['base']):
    """
    A class containing the model for the users
    """
    __tablename__ = 'ai'

    owner = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True)
    source = Column(String)

    def __init__(self, name, owner, source) -> None:
        self.name = name
        self.owner = owner
        self.source = source
        super().__init__()



def file_is_valid(extension: str, text: str):
    # TODO: Create a tester and run the code in python with the game to make sure the file is valid.
    if extension != 'py':
        return False
    if text.count('import') != 1 or 'print' in text:
        return False
    return True

def get_ai_name(code: str) -> str:
    pattern = re.compile(r'super\(\)\.__init__\((?P<ai_name>.+)\)')
    m = None
    for line in code.splitlines():
        line = line.strip()
        m = pattern.match(line)
        if m:
            return m.groupdict()['ai_name']
    return None
        
def write_ai_to_db(owner, name, code):
    name = get_ai_name(code)
    if not name or len(name) <= 2:
        return False
    name = name[1:-1]
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
    
    if 'ai_name' not in request.form:
        return 'Bad Request', 400
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
    session.delete(obj)
    session.commit()
    return "DONE!"

