from .shared import (
    txt
)

from models import User


def cmd_language_select(update, context):
    """ Handler: callback """
    query = update.callback_query
    user = User.get_user(query.from_user.id)
    chosen_language_code = query.data

    user.settings.language = chosen_language_code
    user.save()

    # edit the message to display the selected language
    query.edit_message_text(
        text=txt['CALLBACK']['lang_select'][chosen_language_code]
    )
