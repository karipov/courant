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
    data_filter = query.data.split(config['CB_DATA']['delim'])

    # select different trees depending on the data in the callback
    # Why? because it's useful to separate the actions at and post
    # the setup process for a user.
    if data_filter[0] == config['CB_DATA']['setup']:
        tree = txt['FSM']['TREE']
    elif data_filter[0] == config['CB_DATA']['post_setup']:
        tree = txt['FSM']['DONE_TREE']
    # elif data_filter[0] == config['CB_DATA']['operations']:
    #     # has nothing to do with FSM
    #     operations_callback(update, context, db_user)
    #     return
    else:
        alert_restart(update, context, db_user)
        return

    checked = utility.check_fsm(
        current=user_state,
        future=data_filter[1],
        tree=tree
        )

    logging.debug(f"current user state (db - exec.): {user_state}")
    logging.debug(f"future user state (json): {data_filter[1]}")

    if not checked:
        alert_restart(update, context, db_user)
        return

    # pseudo-switch/case statement
    fsm_options = {
        '1': cmd_entry_type,
        '2': manual_explore_entry,

        '2.1': general_callback,
        '2.2': general_callback,

        '3': general_callback,
        '3.1': modify_rss_callback,
        '3.1.1': delete_rss_callback,
        '3.2': general_callback,
        '3.3': general_callback
    }

    fsm_options[user_state](update, context, db_user)


def operations_callback(update, context, user):
    """
    papa operations

    this function should be focused on operating the main functionalities of
    the bot, such as

    1. Question: maybe just use the master_callback structure and get the
    extra information through the string in the third delimeter?

    i.e. fin:3.1.2:delete0

    delete0 is the information. or is it worth having a separate function
    such as this???
    """
    # TODO: fix this mofo!!
    raise NotImplementedError()


# TODO: rename, as this now actually deletes the message
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


def modify_rss_callback(update, context, user):
    """ Handler fsm:3.1 -> fsm:3 | fsm:3.1.1"""
    # TODO: finish the "generation" of a modification list
    # introduce another handler for fsm:3.1.1 that actually
    # handles the deletion
    query = update.callback_query
    future_state = query.data.split(config['CB_DATA']['delim'])[1]

    if future_state == "3":
        general_callback(update, context, user)
        return

    # TODO: I beliebe telegram allows only a certain number of
    # items as buttons... Maybe having more should be a #premium feature
    inline = [[item.title, f"fin:3.1.1:{i}"] for i, item in enumerate(
        user.subscribed.rss_list
    )]
    # adding the "Back" button. since only one button we use index 0
    inline.append([
        txt['FSM'][future_state]['markup'][user.settings.language][0],
        txt['FSM'][future_state]['payload'][0]
    ])
    label, data = zip(*inline)

    logging.debug(f"!!!!{data}!!!!")

    keyboard = utility.gen_keyboard(
        label=label,
        data=data,
        width=2
    )

    query.edit_message_text(
        text=txt['FSM'][future_state]['text'][user.settings.language],
        reply_markup=keyboard,
        parse_mode='HTML'
    )

    user.settings.fsm_state = "3.1.1"
    user.save()


def delete_rss_callback(update, context, user):
    """ Handler fsm:3.1.1 -> Delete RSS | 3.1 """
    query = update.callback_query
    future_state = query.data.split(config['CB_DATA']['delim'])[1]

    if future_state == "3.1":
        general_callback(update, context, user)
        return

    # TODO: error check here.
    resource_delete_id = int(query.data.split(config['CB_DATA']['delim'])[-1])

    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text=txt['CALLBACK']['deleted_rss'][user.settings.language].format(
            user.subscribed.rss_list[resource_delete_id].title
        ),
        alert=True
    )

    # deletes the RSS resource
    del user.subscribed.rss_list[resource_delete_id]
    logging.debug("\n\n!!!!! deleted RSS resource\n")
    user.save()

    # TODO: update the message with new buttons
    # if the user has 0 feeds, they will be only shown the back button, so
    # no chance of an infinite loop...?
    modify_rss_callback(update, context, user)
