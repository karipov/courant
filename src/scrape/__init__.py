"""
"""
from pathlib import Path
from threading import Thread
import time

from pyrogram import Client

from models import Channel


class Scraper:
    # import functions from other modules

    def __init__(self, config: dict, bot):
        """
        :param config: dict object containing config data.
        :param bot: python-telegram-bot object
        """
        self.client = Client(
            session_name=config['PYROGRAM']['update_session_file'],
            workdir=Path.cwd().joinpath(
                config['PYROGRAM']['sessions_path']
                ),
            api_id=config['PYROGRAM']['api_id'],
            api_hash=config['PYROGRAM']['api_hash']
        )
        self.bot = bot

        # must not forget to stop the client.
        self.client.start()

    def run(self):
        """
        Function to launch & run loop in a separate thread with updates.
        """
        def _loop_run():
            while True:
                self.update_channels()
                time.sleep(10)  # avoid floods

        Thread(target=_loop_run).start()

    def update_channels(self):
        """
        Main channel updater function that iterates over every channel,
        subscribed user and new post and sends the users the new info.
        """
        for resource in Channel.objects:
            posts = self.get_new_posts(resource)

            for user_id in resource.subscribed:
                for post in posts:
                    self.send_post(post.text.html, user_id)

    def send_post(self, post: str, user_id: int):
        self.bot.send_message(
            chat_id=user_id,
            text=post,
            parse_mode='HTML'
        )

    def get_new_posts(self, channel: Channel) -> list:
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
            if message.message_id == channel.last_entry_id:
                break

            posts.append(message)

        # the list needs to be reversed as posts go from new to old, and
        # users need to be served chronologically.
        posts.reverse()

        # update the last_message_id as new data has been fetched.
        channel.last_entry_id = last_message_id
        channel.save()

        return posts
