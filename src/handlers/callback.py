from .shared import txt, config
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
    data_filter = query.data.split(config['TELEGRAM']['delim'])

    if data_filter[0] != 'fsm':
        return

    # TODO: delete message if state is wrong
    # TODO: user callback state is not used at all to check the fsm state.
    # must remember to use this, and maybe do away with fsm states shown in
    # the replies.json 'callback' field. makes it awkward.
    # pseudo-switch/case statement
    fsm_options = {
        '0': alert_restart,
        '1': cmd_entry_type,
        '2': manual_explore_entry,

        '2.1': cmd_manual_entry,
        '2.2': cmd_explore_entry
    }

    fsm_options[data_filter[1]](update, context, db_user)


def alert_restart(update, context, user):
    query = update.callback_query

    context.bot.answer_callback_query(
        callback_query_id=query.id,
        text=txt['CALLBACK']['restart'][user.settings.language],
        show_alert=True
    )


def cmd_entry_type(update, context, user):
    """ Handler: fsm:1 -> fsm:2 """
    query = update.callback_query
    chosen_language_code = query.data.split(config['TELEGRAM']['delim'])[2]
    state = query.data.split(config['TELEGRAM']['delim'])[3]

    user.settings.language = chosen_language_code
    user.settings.fsm_state = state
    user.save()

    new_content = (
        f"{txt['FSM'][state]['text'][chosen_language_code]}"
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][state]['markup'][chosen_language_code],
        txt['FSM'][state]['payload']
    )

    # edit the message to display the selected language
    query.edit_message_text(
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


def manual_explore_entry(update, context, user):
    """ Handler fsm:2 -> fsm:2.1 | fsm:2.2"""
    query = update.callback_query
    state = query.data.split(config['TELEGRAM']['delim'])[3]

    user.settings.fsm_options = state
    user.save()

    new_content = (
        f"{txt['FSM'][state]['text'][user.settings.language]}"
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][state]['markup'][user.settings.language],
        txt['FSM'][state]['payload']
    )

    query.edit_message_text(
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


def cmd_manual_entry(update, context, user):
    """ Handler: fsm:2.1 -> fsm: 2.1.1 """
    pass


def cmd_explore_entry(update, context, user):
    """ Handler: fsm:2.2 -> fsm: 2.2.1 """
    pass
