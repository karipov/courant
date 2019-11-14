from . import txt, config, remove_message
from models import User
import utility


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

    # if user click button of a message that is not the most current one
    # shouldn't happen, but who knows...
    if context.message.message_id != db_user.settings.last_msg_id:
        remove_message(update, context, db_user)

    # pseudo-switch/case statement
    fsm_options = {
        '1': cmd_entry_type,
        '2': manual_explore_entry,

        # watch out, to_menu can also mean going back.. so fix the .format()?
        '2.1': to_menu,
        '2.2': to_menu,

        '3': general_callback,

        '3.1': modify_rss_callback,
        '3.1.1': delete_rss_callback,

        '3.2': modify_channels_callback,
        '3.2.1': delete_channel_callback,

        '3.3': settings_callback,
        '3.3.1': general_callback
    }

    fsm_options[user_state](update, context, db_user)


def general_callback(update, context, user, format_data=None):
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

    if format_data:
        new_content = (
            f"{txt['FSM'][future_state]['text'][user.settings.language]}"
            .format(**format_data)
        )
    else:
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

    # if we would like to do anything with the response (save the message id)
    return update


def cmd_entry_type(update, context, user):
    """ Handler: 1 -> 2 """
    # custom handler needed to ensure language set-up
    query = update.callback_query
    chosen_language_code = query.data.split(config['TELEGRAM']['delim'])[2]

    user.settings.language = chosen_language_code
    user.save()

    general_callback(update, context, user)


def manual_explore_entry(update, context, user):
    """ Handler 2 -> 2.1 | 2.2"""
    update = general_callback(update, context, user)

    # clearing session
    user.subscribed.session_list = list()
    user.save()


def to_menu(update, context, user):
    """
    Ensures the menu is populated with user data.
    """
    menu_data = user.collect_main_data()
    general_callback(update, context, user, format_data=menu_data)

    return update


def modify_rss_callback(update, context, user):
    """ Handler 3.1 -> 3 | 3.1.1"""
    query = update.callback_query
    future_state = query.data.split(config['CB_DATA']['delim'])[1]

    if future_state == '3':
        to_menu(update, context, user)
        return

    # TODO: I beliebe telegram allows only a certain number of
    # items as buttons... Maybe having more should be a #premium feature
    inline = [[item.title, f'fin:3.1.1:{i}'] for i, item in enumerate(
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

    user.settings.fsm_state = future_state
    user.save()


def delete_rss_callback(update, context, user):
    """ Handler 3.1.1 -> Delete RSS | 3.1 """
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


def modify_channels_callback(update, context, user):
    """ Handler 3.2 -> 3 | 3.2.1 """
    # TODO: this is the same as modify_rss_callback
    # except the future_state const in 'inline' definition
    query = update.callback_query
    future_state = query.data.split(config['CB_DATA']['delim'])[1]

    if future_state == '3':
        to_menu(update, context, user)
        return

    inline = [[item.title, f'fin:3.2.1:{i}'] for i, item in enumerate(
        user.subscribed.channel_list
    )]
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

    user.settings.fsm_state = future_state
    user.save()


def delete_channel_callback(update, context, user):
    """ Handler 3.2.1 -> Delete Channel | 3.2 """
    query = update.callback_query
    future_state = query.data.split(config['CB_DATA']['delim'])[1]

    if future_state == "3.2":
        general_callback(update, context, user)
        return

    # TODO: error check here.
    resource_delete_id = int(query.data.split(config['CB_DATA']['delim'])[-1])
    channel_resource = user.subscribed.channel_list[resource_delete_id]

    # if the RSS feed has only one subscribed, then we disable fetching feed
    if len(channel_resource.subscribed) == 1:
        channel_resource.fetched = False
        channel_resource.subscribed = []
    else:
        channel_resource.subscribed.remove(user.user_id)

    channel_resource.save()

    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text=txt['CALLBACK']['deleted_channel'][user.settings.language].format(
            user.subscribed.channel_list[resource_delete_id].title
        ),
        alert=True
    )

    # deletes the Channel resource from User's document
    del user.subscribed.channel_list[resource_delete_id]
    user.save()

    modify_channels_callback(update, context, user)


def settings_callback(update, context, user):
    update = to_menu(update, context, user)

    # clearing session
    user.subscribed.session_list = list()
    user.save()
