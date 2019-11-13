"""
Run to send a quick message to any one specific person.
"""

from pathlib import Path
from json import load

import telegram


args = load(open(Path.cwd().joinpath('src/config.json')))
bot = telegram.Bot(token=args['TELEGRAM']['token'])

bot.send_message(106596774, 'yo')
