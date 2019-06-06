"""
NOT IN USE

Currently a useless module
"""


from .shared import txt
from models import User


def check_state(uid: int) -> User:
    """
    Checks the FSM state for a given user

    :param uid: User identification
    :return: current FSM state
    """
    return User.objects(user_id=uid)


def state_0(update, context):
    uid = update.message.chat_id

    context.bot.send_message(uid, txt['FSM']['0']['en'])

    User.objects(
        user_id=uid
        ).update(set_settings__S__fsm_state=1)

    # we return the new state
    return 1
