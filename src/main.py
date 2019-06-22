from pathlib import Path
from json import load
import logging

from handlers import (
    admin, service, callback
)

from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler
)


# set some config files and define them as objects
args = load(open(Path.cwd().joinpath('src/config.json')))
updater = Updater(token=args['TELEGRAM']['token'], use_context=True)
dispatcher = updater.dispatcher


# ADDING HANDLERS HERE
# add command handlers
dispatcher.add_handler(CommandHandler('admin', admin.cmd_admin))
dispatcher.add_handler(CommandHandler('start', service.cmd_start))
dispatcher.add_handler(CommandHandler('help', service.cmd_help))

# add callback handlers
dispatcher.add_handler(CallbackQueryHandler(callback.cmd_language_select))

# start polling
logging.basicConfig(level=logging.INFO)
updater.start_polling()
