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
    data_filter = query.data.split(config['TELEGRAM']['delim'])

    if data_filter[0] != 'fsm':
        # haven't dealt with anything that isn't FSM yet, so just
        # quit if we see a problem.
        return

    user_state = db_user.settings.fsm_state

    checked = utility.check_fsm(
        current=user_state,
        future=data_filter[1],
        tree=txt['FSM']['TREE']
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
    query = update.callback_query
    state = query.data.split(config['TELEGRAM']['delim'])[1]

    context.bot.answer_callback_query(query.id)

    user.settings.fsm_state = state
    user.save()

    new_content = (
        f"{txt['FSM'][state]['text'][user.settings.language]}"
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][state]['markup'][user.settings.language],
        txt['FSM'][state]['payload']
    )

    # edit the message to display the selected language
    query.edit_message_text(
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


def cmd_entry_type(update, context, user):
    """ Handler: fsm:1 -> fsm:2 """
    query = update.callback_query
    chosen_language_code = query.data.split(config['TELEGRAM']['delim'])[2]

    user.settings.language = chosen_language_code
    user.save()

    general_callback(update, context, user)


def manual_explore_entry(update, context, user):
    """ Handler fsm:2 -> fsm:2.1 | fsm:2.2"""
    general_callback(update, context, user)
