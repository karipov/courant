"""
Handles "general" functionality that pertains to the workings of the program
post-setup.

Currently contains handlers for:
- text-messages within the set-up FSM states

Currently contains filters for:
- text messages with certain FSM states
"""

from models import User


def master(update, context):
    """
    This handler is implemented to generally deal with FSM states in incoming
    messages.
    """
    db_user = User.get_user(update.message.from_user.id)
    user_state = db_user.settings.fsm_state

    # TODO: fill the fsm_options
    fsm_options = {
        '2.1.1': rss_compile,
        '2.1.2': channel_compile,

        '2.2.1': explore_compile
    }

    fsm_options[user_state](update, context, db_user)


def general_compile(update, context, user):
    """
    Handles general messages for compilation.

    This could be useful in case the need arises to add more services,
    which will all basically use the same backend or same pieces of code.
    """
    pass


def rss_compile(update, context, user):
    """ Handler: fsm:2.1.1 -> fsm:3 """
    pass


def channel_compile(update, context, user):
    """ Handler: fsm:2.1.2 -> fsm:3 """
    pass


def explore_compile(update, context, user):
    """ Handler: fsm:2.2.1 -> fsm:3 """
    pass
