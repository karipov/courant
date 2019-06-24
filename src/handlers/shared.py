"""
Used to expose shared variables and object instantiations
"""

from pathlib import Path
from enum import Enum
import json

txt = json.load(open(Path.cwd().joinpath('src/interface/replies.json')))
config = json.load(open(Path.cwd().joinpath('src/config.json')))


# TODO: remove this class as it is now useless.
class FSM(Enum):
    START = '0'
    LANGUAGE = '1'
    ENTRY_TYPE = '2'

    MANUAL_ENTRY = '2.1'
    EXPLORE_ENTRY = '2.2'
