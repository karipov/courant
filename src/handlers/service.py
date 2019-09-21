"""
Handles "service" functionality, such as "help" and "start"
commands - meaning most of the answers to these commands are static and
do not comprise the main functionality of the program.

Currently contains handlers for the following commands:
- /start <PAYLOAD>
- /cancel
- /help
"""

from .shared import txt, FSM
from models import User, Settings
import utility


markup = utility.gen_keyboard(txt['LANG_NAMES'], txt['LANG_PAYLOAD'])


def get_payload(text: str):
    """
    Convenience proxy function for utility.extract_payload

    :param text: text containing the payload
    :return: extracted payload
    """
    try:
        return int(utility.extract_payload(text)[0])
    except (TypeError, IndexError, ValueError):
        return None


def cmd_start(update, context):
    """ Handler: command /start <PAYLOAD> """
    uid = update.message.from_user.id
    # temporary language, until user selects via callback
    lang = utility.lang(
        update.message.from_user.language_code, txt['LANG_CODES']
        )
    payload = get_payload(update.message.text)

    # build account for a user if it doesn't exist
    if not User.check_exists(uid=uid):
        User(
            user_id=uid,
            settings=Settings(language=lang)
        ).save()

    current_user = User.get_user(uid=uid)

    # don't do anything if the user is in another FSM state
    if not current_user.settings.fsm_state == '0':
        context.bot.delete_message(uid, update.message.message_id)
        return

    current_user.settings.fsm_state = FSM.LANGUAGE.value
    current_user.save()

    # worry about payloads and invites below:
    if not payload:
        context.bot.send_message(
            uid, txt['SERVICE']['start'][lang],
            reply_markup=markup
            )
        return

    try:
        inviter = User.get_user(uid=payload)
    except LookupError:
        return

    inviter.add_to_invited(uid)
    context.bot.send_message(
        uid, txt['SERVICE']['invited_by'][lang].format(
            context.bot.get_chat(payload).first_name
        )
    )


def cmd_help(update, context):
    """ Handler: command /help """
    user = User.get_user(update.message.from_user.id)

    context.bot.send_message(
        user.user_id, txt['SERVICE']['help'][user.settings.language]
    )


def cmd_cancel(update, context):
    """ Handler: command /cancel """
    user = User.get_user(update.message.from_user.id)

    # reset user fsm_state:
    user.settings.fsm_state = FSM.START.value
    user.save()

    context.bot.send_message(
        user.user_id, txt['SERVICE']['cancel'][user.settings.language]
    )


# TODO: salvage usable code; delete the rest.
# def cmd_done(update, context):
#     """
#     Handler: command /done
#     This command is, and can only be, called when the user is finished with
#     the set-up process.
#     """
#     # in this handler, we are changing user FSM states
#     # therefore, we first have to check them.

#     user = User.get_user(update.message.from_user.id)
#     end_fsm_states = ['2.1']

#     if user.settings.fsm_state not in end_fsm_states:
#         context.bot.delete_message(user.user_id, update.message.message_id)
#         return

#     if user.settings.fsm_state == '2.1':
#         user.settings.fsm_state = FSM.DONE.value
#         user.save()

#         data = {
#             "link": f"tg://user?id={update.message.from_user.id}",
#             "name": html.escape(update.message.from_user.first_name),
#             "rss_num": len(user.subscribed.rss_list),
#             "channel_num": len(user.subscribed.channel_list),
#             "time": user.registered.strftime("%Y-%m-%d")
#         }

#         new_content = (
#             f"{txt['FSM'][FSM.DONE.value]['text'][user.settings.language]}"
#             .format(**data)
#         )

#         keyboard = utility.gen_keyboard(
#             txt['FSM'][FSM.DONE.value]['markup'][user.settings.language],
#             txt['FSM'][FSM.DONE.value]['payload']
#         )

#         context.bot.send_message(
#             chat_id=update.message.from_user.id,
#             text=new_content,
#             reply_markup=keyboard,
#             parse_mode='HTML'
#         )
