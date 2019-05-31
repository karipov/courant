"""
This module is used to expose shared variables and object instantiations
"""

from pathlib import Path
import json

txt = json.load(open(Path.cwd().joinpath('src/interface/replies.json')))
config = json.load(open(Path.cwd().joinpath('src/config.json')))
