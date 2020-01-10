"""
Handles "service" functionality, such as "help" and "start"
commands - meaning most of the answers to these commands are static and
do not comprise the main functionality of the program.

Currently contains handlers for the following commands:
- /start <PAYLOAD>
- /cancel
- /help
"""

from . import txt, remove_message, create_new_user, FSM
from models import User
import utility

from telegram.error import BadRequest


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
    uid = update.message.from_user.id
    payload = get_payload(update.message.text)
    user = create_new_user(update)

    # "absorb" message - cleaner this way
    remove_message(update, context, user)

    main_text = ''
    lang = user.settings.language

    if user.settings.fsm_state in {'0', '1'}:
        main_text += txt['SERVICE']['start'][lang]
        markup = utility.gen_keyboard(txt['LANG_NAMES'], txt['LANG_PAYLOAD'])

        user.settings.fsm_state = FSM.LANGUAGE.value
        user.save()

    else:
        # send the main menu
        # better than sending message associated with the current state, as
        # there are messages with customized keyboards, etc..
        main_text += txt['FSM']['3']['text'][lang].format(
            **user.collect_main_data()
        )
        markup = utility.gen_keyboard(
            txt['FSM']['3']['markup'][lang],
            txt['FSM']['3']['payload']
        )

        # ensure that if user is in another state the payload isn't processed
        # just a precaution...
        payload = None

    if user.settings.last_msg_id:
        try:
            context.bot.delete_message(
                chat_id=uid,
                message_id=user.settings.last_msg_id
            )
        except BadRequest:
            try:
                context.bot.edit_message_text(
                    chat_id=uid,
                    message_id=user.settings.last_msg_id,
                    text=txt['CALLBACK']['deleted'][lang],
                    parse_mode='HTML'
                )
            except BadRequest:
                # the message can be already deleted by the user
                pass

    if payload:
        try:
            inviter = User.get_user(uid=payload)
        except LookupError:
            return

        inviter.add_to_invited(uid)
        main_text = (
            txt['SERVICE']['invited_by'][lang].format(
                user=utility.escape(context.bot.get_chat(payload).first_name),
                id=inviter.user_id
            )
            + '\n\n'
            + main_text
        )

    sent_message = context.bot.send_message(
        chat_id=uid,
        text=main_text,
        reply_markup=markup,
        parse_mode='HTML'
    )

    # bot sends a new message, so the old last_msg_id must be replaced.
    user.settings.last_msg_id = sent_message.message_id
    user.save()


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
def cmd_done(update, context):
    """
    Handler: command /done
    This command is, and can only be, called when the user is finished with
    the set-up process.
    """
    # in this handler, we are changing user FSM states
    # therefore, we first have to check them.

    user = User.get_user(update.message.from_user.id)
    end_fsm_states = ['2.1']

    if user.settings.fsm_state not in end_fsm_states:
        context.bot.delete_message(user.user_id, update.message.message_id)
        return

    if user.settings.fsm_state == '2.1':
        user.settings.fsm_state = FSM.DONE.value
        user.save()

    new_content = (
        f"{txt['FSM'][FSM.DONE.value]['text'][user.settings.language]}"
        .format(**user.collect_main_data())
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][FSM.DONE.value]['markup'][user.settings.language],
        txt['FSM'][FSM.DONE.value]['payload']
    )

    context.bot.send_message(
        chat_id=update.message.from_user.id,
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
