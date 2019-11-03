"""
Module for containing admin-related command handlers. This module makes heavy
use of checking for admin priveleges, so a check function is included.
"""

from . import txt, config
from models import User


def check_admin(uid: int):
    """
    Checks if the person is an admin

    :param uid: user_id to check for.
    """
    if uid in config['TELEGRAM']['admin']:
        return True
    else:
        return False


def cmd_admin(update, context):
    """
    Provides administrators with statistics.
    """
    uid = update.message.chat_id

    if not check_admin(uid):
        return

    total_users = User.retrieve_total()

    context.bot.send_message(
        uid, txt['ADMIN']['stats']['en'].format(total_users)
    )
    # TODO: include a button that destroys the message.
