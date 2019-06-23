from .shared import (
    txt, FSM
)
from models import User
import utility


def cmd_language_select(update, context):
    """ Handler: callback """
    query = update.callback_query
    user = User.get_user(query.from_user.id)
    chosen_language_code = query.data

    user.settings.language = chosen_language_code
    user.settings.fsm_state = FSM.MANUAL_ENTRY.value
    user.save()

    new_content = (
        f"{txt['CALLBACK']['lang_select'][chosen_language_code]}\n"
        f"\n\n"
        f"{txt['FSM'][FSM.MANUAL_ENTRY.value]['text'][chosen_language_code]}"
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][FSM.MANUAL_ENTRY.value]['markup'][chosen_language_code],
        txt['FSM'][FSM.MANUAL_ENTRY.value]['payload']
    )

    # edit the message to display the selected language
    query.edit_message_text(
        text=new_content,
        markup=keyboard
    )
