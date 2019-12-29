"""
Methods for the Scrape class that enable collection and distribution of
information from channels to users
"""
import html

from pyrogram.errors import BadRequest
from pyrogram import Message

from models import Channel, User


def update_channels(self):
    """
    Main channel updater function that iterates over every channel,
    subscribed user and new post and sends the users the new info.
    """
    for resource in Channel.objects:

        try:
            posts = self._get_new_posts(resource)
        except BadRequest:  # if username doesn't exist; invalid.
            for user_id in resource.subscribed:
                user = User.get_user(user_id)
                user_lang = user.settings.language

                self.bot.send_message(
                    text=self.txt['UPD_CHANS']['deleted'][user_lang].format(
                        resource.username
                    ),
                    chat_id=user_id,
                    parse_mode='HTML'
                )

            resource.delete()
            return

        for user_id in resource.subscribed:
            for post in posts:
                data = self._filter_post(post)
                self._send_post(data, user_id)


def _filter_post(self, post: Message) -> dict:
    """
    Filters the pyrogram Message class to be sent by PTB

    :param post: pyrogram Message
    :return dict: dictionary with all info about type:
    """
    info = {
        'metadata': {}
    }

    if post.media:
        info['method'] = self.bot.send_message

        info['metadata']['text'] = (
            f"<b>{html.escape(post.chat.title)}</b> "
            f"<a href=\"t.me/"
            f"{post.chat.username}/{post.message_id}\">[»]</a>"
        )
        info['metadata']['disable_web_page_preview'] = False
        info['metadata']['parse_mode'] = 'HTML'

        return info

    if post.text:
        # when the channel title is added, total message length can be
        # more than 4096 chars, so it's shortened.
        cut_and_html = \
            post.text.html[:4096-len(post.chat.title)-10] + ' ...'

        info['method'] = self.bot.send_message

        info['metadata']['text'] = (
            f"<b>{html.escape(post.chat.title)}</b> "
            f"<a href=\"t.me/"
            f"{post.chat.username}/{post.message_id}\">[»]</a>\n"
            f"{cut_and_html}"
        )
        info['metadata']['parse_mode'] = 'HTML'
        info['metadata']['disable_web_page_preview'] = True

        return info


def _send_post(self, info: dict, user_id: int):
    info['metadata']['chat_id'] = user_id
    # execute function with provided metadata
    info['method'](**info['metadata'])


def _get_new_posts(self, channel: Channel) -> list:
    """
    Grabs all the new posts from a channel

    :param channel: document from the Channel collection
    :return: a list of messages (posts)
    """
    # ensure the channel is resolved
    # TODO: this might need to be improved due to flood limits.
    _ = self.client.get_chat(channel.username)

    last_message_id = self.client.get_history(
        chat_id=channel.channel_id,
        limit=1
    )[0].message_id

    if last_message_id == channel.last_entry_id:
        return []

    posts = []

    # prevents from users flooding the bot, so we just grab at most last
    # 15 messages from the channel.
    for message in self.client.iter_history(channel.channel_id, limit=15):
        if message.message_id <= channel.last_entry_id:
            break

        posts.append(message)

    # the list needs to be reversed as posts go from new to old, and
    # users need to be served chronologically.
    posts.reverse()

    # update the last_message_id as new data has been fetched.
    channel.last_entry_id = last_message_id
    channel.save()

    return posts
