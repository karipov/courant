"""
Used to expose shared variables, object instantiations and function definitions
"""

from pathlib import Path
from enum import Enum
import json
import logging

from telegram import TelegramError
from pyrogram import Client

import utility


txt = json.load(open(Path.cwd().joinpath('src/interface/replies.json')))
config = json.load(open(Path.cwd().joinpath('src/config.json')))

client = Client(
    session_name=config['TELEGRAM']['session_name'],
    api_id=config['TELEGRAM']['api_id'],
    api_hash=config['TELEGRAM']['api_hash']
)
logging.getLogger('pyrogram').setLevel(logging.WARNING)


class FSM(Enum):
    START = '0'

    LANGUAGE = '1'
    FINISH_MANUAL = '2.1b'

    DONE = '3'


def to_menu(update, context, user):
    """
    Ensures the menu is populated with user data.
    """
    query = update.callback_query  # shorter var name
    future_state = query.data.split(config['TELEGRAM']['delim'])[1]

    # telegram requires the server to "answer" a callback query
    context.bot.answer_callback_query(query.id)

    # the "future" FSM state now becomes the "current" FSM state
    user.settings.fsm_state = future_state
    user.save()

    new_content = (
        f"{txt['FSM'][future_state]['text'][user.settings.language]}"
        .format(**user.collect_main_data())
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][future_state]['markup'][user.settings.language],
        txt['FSM'][future_state]['payload']
    )

    # edit the message to display the selected language
    query.edit_message_text(
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


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
