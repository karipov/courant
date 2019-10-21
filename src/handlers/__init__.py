"""
Used to expose shared variables, object instantiations and function definitions
"""

from pathlib import Path
from enum import Enum
import json

from telegram import TelegramError

from pyrogram import Client


txt = json.load(open(Path.cwd().joinpath('src/interface/replies.json')))
config = json.load(open(Path.cwd().joinpath('src/config.json')))

client = Client(
    session_name=config['TELEGRAM']['session_name'],
    api_id=config['TELEGRAM']['api_id'],
    api_hash=config['TELEGRAM']['api_hash']
)


class FSM(Enum):
    START = '0'

    LANGUAGE = '1'
    FINISH_MANUAL = '2.1b'

    DONE = '3'


def remove_message(update, context, user):
    """
    If a user decides to click a button they aren't supposed to, then this
    function will delete the message containing that button. Also, if a user
    sends a message outside of the FSM, the message is deleted.

    :param user: the MongoEngine User object.
    """
    query = update.callback_query

    # user messages (i.e. not clicking on buttons)
    if not query:
        try:
            context.bot.delete_message(
                chat_id=update.message.from_user.id,
                message_id=update.message.message_id
            )
        except TelegramError:
            # if we can't delete the message.. Oh well, nothing to do.
            pass
        return

    context.bot.answer_callback_query(query.id)

    try:
        context.bot.delete_message(
            chat_id=query.from_user.id,
            message_id=query.message.message_id
        )
    # if the message is older than 48h, you cannot delete it.
    # however, you can edit any message at any time
    except TelegramError:
        query.edit_message_text(
            text=txt['CALLBACK']['deleted'][user.settings.language],
            parse_mode='HTML'
        )
