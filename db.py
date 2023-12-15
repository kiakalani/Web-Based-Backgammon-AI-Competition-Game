"""
Author: Kia Kalani
Student ID: 101145220
This module is responsible for implementing the database
instance that would be used throughout the project
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

def create_db(app):
    """
    <code>create_db</code> creates the initial database
    instance into the app configuration.
    :param: app: The flask application instance
    :return: None
    """

    # Passing address as an environment variable
    db_path = os.environ.get('SQLDB')
    if not db_path:
        print('Error finding database. Please set SQLDB environment variable')
        exit(-1)

    # Creating db instance
    engine = create_engine(f'sqlite:///{db_path}')
    db_session = scoped_session(sessionmaker(autoflush=False, bind=engine))
    base = declarative_base()
    base.query = db_session.query_property()

    app.config['DB'] = {
        'engine': engine,
        'session': db_session,
        'base': base
    }
    # On app exit remove db instance
    @app.teardown_appcontext
    def remove_session(exception=None):
        db_session.remove()

def load_db(app):
    """
    <code>load_db</code> is invoked when the models are
    needed to be created within the database.
    :param: app: The flask application instance
    :return: None
    """

    from login import User
    from ai_management import AI
    from message import Message
    from compete import Competition
    from friends import Friend

    db_info = app.config['DB']
    db_info['base'].metadata.create_all(bind=db_info['engine'])
