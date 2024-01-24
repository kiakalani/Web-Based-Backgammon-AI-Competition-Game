# Web-Based Backgammon AI Competition Game

### Kia Kalani

## Required packages/tools for running this project:
1. Python
2. sqlite3
3. Docker

## Instructions for running the code:

1. `python -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Set the `SQLDB` variable as the path of the file for your SQLITE database in your environment variable. Ex: `export SQLDB=bg.db`
5. Set the secret key environment variable for the application. This should not be technically provided directly as a text; however, for running the project, this element is required. This would look like the following: `export SECRET_KEY=A_Security_Key`
6. `python ./__init__.py`


Note: For running the project properly, you would need to have docker installed on your system and running. In addition, the user that runs the flask application needs to have the privilege to create and run docker containers; otherwise, when user tries to run a competition, or upload their code, bad request message would be provided to them.
