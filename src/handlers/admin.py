"""
Module for containing admin-related command handlers. This module makes heavy
use of checking for admin priveleges, so a check function is included.
"""

from .shared import (
    txt, config
)


def check_admin(uid: int):
    """
    Checks if the person is an admin

    :param uid: user_id to check for.
    """
    if str(uid) == config['admin']:
        return True
    else:
        return False


def cmd_admin(update, context):
    uid = update.message.chat_id
    if not check_admin(uid):
        return

    context.bot.send_message(
        uid, txt['ADMIN']['stats']['en']
    )
