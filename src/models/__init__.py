from json import load
from pathlib import Path

from mongoengine import connect

from .channels import Channel
from .rss import RSS
from .users import User, Settings

__all__ = ['Channel', 'RSS', 'User', 'Settings']

# loading the configuration file
args = load(open(Path.cwd().joinpath('src/config.json')))
# connecting to a mongo database
db = connect(args['MONGO']['name'])

# clears database before start of every test.
if args['MONGO']['dev_mode']:
    db.drop_database(args['MONGO']['name'])
