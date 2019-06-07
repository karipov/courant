from .shared import (
    txt
)
from models import User, Settings
import utility


markup = utility.gen_keyboard(label=txt['LANG_NAMES'], data=txt['LANGS'])


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
    """
    Handler: command /start <PAYLOAD>
    """
    uid = update.message.chat_id
    lang = utility.lang(update.message.from_user.language_code, txt['LANGS'])
    payload = get_payload(update.message.text)

    print(f'uid {uid} - lang {lang} has been detected')

    # build account for a user if it doesn't exist
    if not User.check_exists(uid=uid):
        print(f'user {uid} doesn\'t exist... building account')
        User(
            user_id=uid,
            settings=Settings(language=lang)
        ).save()

    if not payload:
        context.bot.send_message(
            uid, txt['SERVICE']['start'][lang],
            reply_markup=markup
            )
        return

    inviter = User.get_user(uid=payload)

    if not inviter:
        return

    inviter.add_to_invited(uid)
    context.bot.send_message(
        uid, txt['SERVICE']['invited_by'][lang].format(payload)
    )
