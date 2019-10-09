"""
Cleans the mongo database by dropping all of its collections
"""

from json import load
from pathlib import Path
from mongoengine import connect

args = load(open(Path.cwd().joinpath('src/config.json')))
db = connect(args['MONGO']['name'])
db.drop_database(args['MONGO']['name'])
