"""
Handles "general" functionality that pertains to the workings of the program
post-setup.

Currently contains handlers for:
- text-messages within the set-up FSM states

Currently contains filters for:
- text messages with certain FSM states
"""


def unprompted_message_handler(update, context):
    """ Handler for unprompted messages """
    context.bot.delete_message(
        update.message.chat_id,
        update.message.message_id
        )
