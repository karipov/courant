from pathlib import Path
from json import load
import logging

from handlers import admin, service, callback, general
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )

# set some config files and define them as objects
args = load(open(Path.cwd().joinpath('src/config.json')))
updater = Updater(token=args['TELEGRAM']['token'], use_context=True)
dispatcher = updater.dispatcher
logger = logging.getLogger(__name__)


def error(update, context):
    """ Log Errors caused by Updates """
    logger.warning(
        'Update "%s" caused error "%s"', update, error
        )


# ADDING HANDLERS HERE
# add command handlers
dispatcher.add_handler(CommandHandler('admin', admin.cmd_admin))
dispatcher.add_handler(CommandHandler('start', service.cmd_start))
dispatcher.add_handler(CommandHandler('cancel', service.cmd_cancel))
dispatcher.add_handler(CommandHandler('help', service.cmd_help))

# adding message habdlers
dispatcher.add_handler(MessageHandler(Filters.text, general.master))

# add callback handlers
dispatcher.add_handler(CallbackQueryHandler(callback.master_callback))

# add error handler
# dispatcher.add_error_handler(error)

# start polling
updater.start_polling()
updater.idle()
