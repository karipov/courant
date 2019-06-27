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
    state = db_user.settings.fsm_state

    # TODO: fill the fsm_options
    fsm_options = {
        '': ''
    }

    fsm_options[state](update, context, db_user)
