from pathlib import Path
from json import load
import logging

from handlers import admin, service

from telegram.ext import Updater, CommandHandler


# set some config files and define them as objects
args = load(open(Path.cwd().joinpath('src/config.json')))
updater = Updater(token=args['TOKEN'], use_context=True)
dispatcher = updater.dispatcher

# add stuff to the dispathcer
dispatcher.add_handler(CommandHandler('start', service.cmd_start))
dispatcher.add_handler(CommandHandler('admin', admin.cmd_admin))

# start polling
logging.basicConfig(level=logging.INFO)
updater.start_polling()
