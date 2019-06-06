from pathlib import Path
from json import load
import logging

from handlers import admin, service

from telegram.ext import Updater, CommandHandler


# set some config files and define them as objects
args = load(open(Path.cwd().joinpath('src/config.json')))
updater = Updater(token=args['TELEGRAM']['token'], use_context=True)
dispatcher = updater.dispatcher


# add stuff to the dispatcher
dispatcher.add_handler(CommandHandler('admin', admin.cmd_admin))
dispatcher.add_handler(CommandHandler('start', service.cmd_start))

# start polling
logging.basicConfig(level=logging.INFO)
updater.start_polling()
