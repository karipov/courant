from .shared import txt, FSM
from models import User
import utility


def master_callback(update, context):
    """
    papa callback

    since python-telegram-bot doesn't have filters for callback data
    i have to implement this super janky solution
    """
    pass


def cmd_language_select(update, context):
    """ Handler: callback """
    query = update.callback_query
    user = User.get_user(query.from_user.id)
    chosen_language_code = query.data

    user.settings.language = chosen_language_code
    user.settings.fsm_state = FSM.ENTRY_TYPE.value
    user.save()

    new_content = (
        f"<i>{txt['CALLBACK']['lang_select'][chosen_language_code]}</i>"
        f"\n\n"
        f"{txt['FSM'][FSM.ENTRY_TYPE.value]['text'][chosen_language_code]}"
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][FSM.ENTRY_TYPE.value]['markup'][chosen_language_code],
        txt['FSM'][FSM.ENTRY_TYPE.value]['payload']
    )

    # edit the message to display the selected language
    query.edit_message_text(
        text=new_content,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
