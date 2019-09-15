from .shared import txt, config
from models import User
import utility

import logging

from telegram import TelegramError


def master_callback(update, context):
    """
    papa callback

    since python-telegram-bot doesn't have filters for callback data
    i have to implement this super janky solution.
    thanks PTB. very cool.
    """
    query = update.callback_query
    db_user = User.get_user(query.from_user.id)
    user_state = db_user.settings.fsm_state
    data_filter = query.data.split(config['TELEGRAM']['delim'])

    # select different trees depending on the data in the callback
    # Why? because it's useful to separate the actions at and post
    # the setup process for a user.
    if data_filter[0] == 'set':
        tree = txt['FSM']['TREE']
    elif data_filter[0] == 'fin':
        tree = txt['FSM']['DONE_TREE']
    else:
        logging.debug("OOPS, RETURN REACHED")
        logging.debug(f"{data_filter}")
        # TODO: delete whatever message had faulty callback data
        # will be helpful if any time we have an update to the
        # callback data naming scheme.
        return

    # TODO: now that there are two trees, improve the checking
    # TODO: maybe abandon the 'FSM' and split into 'SET' (for set-up
    # and anything from states 1-2) and 'FIN' (for anything after state 3)
    checked = utility.check_fsm(
        current=user_state,
        future=data_filter[1],
        tree=tree
        )

    if not checked:
        alert_restart(update, context, db_user)
        return

    # pseudo-switch/case statement
    fsm_options = {
        '1': cmd_entry_type,
        '2': manual_explore_entry,

        # if a button is clicked here, it's the "back" button
        '2.1': general_callback,
        '2.2': general_callback,

        '3': general_callback,
        '3.1': general_callback,
        '3.2': general_callback,
        '3.3': general_callback
    }

    logging.debug(f"current user state (db - exec.): {user_state}")
    logging.debug(f"future user state (json): {data_filter[1]}")

    fsm_options[user_state](update, context, db_user)


def alert_restart(update, context, user):
    """
    If a user decides to click a button they aren't supposed to, then this
    function will notify them.

    :param user: the MongoEngine User object.
    """
    query = update.callback_query

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


def general_callback(update, context, user):
    """
    This function can be used for general callback operations. It includes
    features such as extracting the future FSM state, and setting it for the
    user.
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


def cmd_entry_type(update, context, user):
    """ Handler: fsm:1 -> fsm:2 """
    # custom handler needed to ensure language set-up
    query = update.callback_query
    chosen_language_code = query.data.split(config['TELEGRAM']['delim'])[2]

    user.settings.language = chosen_language_code
    user.save()

    general_callback(update, context, user)


def manual_explore_entry(update, context, user):
    """ Handler fsm:2 -> fsm:2.1 | fsm:2.2"""
    general_callback(update, context, user)
