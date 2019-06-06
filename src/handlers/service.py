from .shared import (
    txt
)
from models import User, Settings
import utility


markup = utility.gen_keyboard(label=txt['LANG_NAMES'], data=txt['LANGS'])
print(markup)


def cmd_start(update, context):
    uid = update.message.chat_id
    lang = update.message.from_user.language_code

    print(f'uid {uid} - lang {lang} has been detected')

    if lang not in txt['LANGS']:
        lang = 'en'

    # build account for a user if it doesn't exist
    if not User.check_exists(uid=uid):
        print(f'user {uid} doesn\'t exist... building account')
        User(
            user_id=uid,
            settings=Settings(language=lang)
        ).save()

    # extract and turn the payload into an integer
    try:
        print(f'message text: {update.message.text}')
        payload = int(utility.extract_payload(update.message.text)[0])
        print(f'payload is: {payload}')
    except (TypeError, IndexError):
        print('payload is empty')
        payload = None

    if not payload:
        context.bot.send_message(
            uid, txt['SERVICE']['start']['en'],
            reply_markup=markup
            )
        return

    # update whoever invited the new user
    # we also account for whether the inviter is
    # already in the database or not
    try:
        inviter = User.objects.get(user_id=payload)
        if uid in inviter.users_invited or uid == payload:
            print("user already invited or is the inviter themselves")
            # maybe provide an error message here?
            # "you've already invited this user"
            return

        print(f'inviter uid {inviter.user_id}')
        print(f'inviter already invited: {inviter.users_invited}')

        # append & save our changes on the inviter
        inviter.users_invited.append(uid)
        inviter.save()

        context.bot.send_message(
            uid, txt['SERVICE']['invited_by']['en'].format(payload)
        )

        print(f'inviter now has invited: {inviter.users_invited}')
    except Exception as e:
        # catches if the user doesn't exist
        print('panic', e)

    print()
