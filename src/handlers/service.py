from .shared import (
    txt
)


def cmd_start(update, context):
    context.bot.send_message(
        update.message.chat_id, txt['SERVICE']['start']['en']
    )
