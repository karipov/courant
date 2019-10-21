from . import txt, config, remove_message
from models import User
import utility

import logging


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
        remove_message(update, context, db_user)
        return

    checked = utility.check_fsm(
        current=user_state,
        future=data_filter[1],
        tree=tree
        )

    logging.debug(f"current user state (db - exec.): {user_state}")
    logging.debug(f"future user state (json): {data_filter[1]}")

    if not checked:
        remove_message(update, context, db_user)
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

        '3.3': general_callback,
        '3.3.1': general_callback
    }

    fsm_options[user_state](update, context, db_user)


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
    rss_resource = user.subscribed.rss_list[resource_delete_id]

    # if the RSS feed has only one subscribed, then we disable fetching feed
    if len(rss_resource.subscribed) == 1:
        rss_resource.fetched = False
        rss_resource.subscribed = []
    else:
        rss_resource.subscribed.remove(user.user_id)

    rss_resource.save()

    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text=txt['CALLBACK']['deleted_rss'][user.settings.language].format(
            user.subscribed.rss_list[resource_delete_id].title
        ),
        alert=True
    )

    # deletes the RSS resource from User's document
    del user.subscribed.rss_list[resource_delete_id]
    user.save()

    modify_rss_callback(update, context, user)
