from pathlib import Path
from json import load
import logging
import traceback
import os
import sys

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters
from telegram.utils.helpers import mention_html
from telegram.error import TelegramError

from handlers import admin, service, callback, general
from scrape import Scraper

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# set some config files and define them as objects
args = load(open(Path.cwd().joinpath('src/config.json')))

# use different bots in production vs in testing
if os.getenv('TELEGRAM_PRODUCTION', False):
    token = args['TELEGRAM']['token_prod']
else:
    token = args['TELEGRAM']['token']

updater = Updater(token=token, use_context=True)

dispatcher = updater.dispatcher
logger = logging.getLogger(__name__)


def error(update, context):
    """
    Log & manage errors caused by updates
    """

    if update.effective_message:
        text = "Hey. I'm sorry to inform you that an error happened " \
               "while I tried to handle your update. " \
               "My developer(s) will be notified."
        try:
            update.effective_message.reply_text(text)
        except TelegramError:
            # message could fail if callback or inline use
            # or if bot is simply blocked, so pass if error.
            pass

    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    # lets try to get as much information from the telegram update as possible
    payload = ""

    if update.effective_user:
        mention_user = mention_html(
            update.effective_user.id, update.effective_user.first_name
        )
        payload += f"with the user {mention_user}"

    # situations when you don't get a chat:
    if update.effective_chat:
        payload += f"within the chat <i>{update.effective_chat.title}</i>"
        if update.effective_chat.username:
            payload += f"(@{update.effective_chat.username})"

    if update.poll:
        payload += f"with the poll id {update.poll.id}."

    text = f"Hey.\nThe error <code>{context.error}</code> ocurred {payload}. "\
           f"Here's the full traceback:\n\n<code>{trace}</code>"

    for dev_id in args['TELEGRAM']['admin']:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)

    # raise the error again, so the logger module catches it.
    raise


# ADDING HANDLERS HERE
# add command handlers
dispatcher.add_handler(CommandHandler('admin', admin.cmd_admin))
dispatcher.add_handler(CommandHandler('start', service.cmd_start))
dispatcher.add_handler(CommandHandler('cancel', service.cmd_cancel))
dispatcher.add_handler(CommandHandler('done', service.cmd_done))
dispatcher.add_handler(CommandHandler('help', service.cmd_help))

# adding message habdlers
dispatcher.add_handler(MessageHandler(Filters.text, general.master))

# add callback handlers
dispatcher.add_handler(CallbackQueryHandler(callback.master_callback))

# add error handler
dispatcher.add_error_handler(error)

scrape = Scraper(config=args, bot=updater.bot)
scrape.run()

# start polling
updater.start_polling()
updater.idle()
