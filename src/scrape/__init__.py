"""
Scraper class that scrapes and distrubutes channel and rss information to users
"""
from pathlib import Path
from threading import Thread
import time
import json

from pyrogram import Client


class Scraper:
    def __init__(self, config: dict, bot):
        """
        :param config: dict object containing config data.
        :param bot: python-telegram-bot object
        """
        self.bot = bot
        self.config = config
        self.txt = json.load(
            open(Path.cwd().joinpath('src/interface/replies.json'))
        )

    # import functions from other modules
    from ._channel_scrape import update_channels, _get_new_posts, \
        _filter_post, _send_post
    from ._rss_scrape import update_rss_feeds, _full_feed_check, \
        _get_new_entries, _send_rss_message

    def run(self):
        """
        Launch & run loop in a separate thread with updates.
        """
        def _loop_run():
            # initializing client inside thread to avoid sqlite session errs
            self.client = Client(
                session_name=self.config['PYROGRAM']['update_session_file'],
                workdir=Path.cwd().joinpath(
                    self.config['PYROGRAM']['sessions_path']
                    ),
                api_id=self.config['PYROGRAM']['api_id'],
                api_hash=self.config['PYROGRAM']['api_hash']
            )
            self.client.start()

            while True:
                self.update_channels()
                self.update_rss_feeds()
                time.sleep(180)  # avoid floods

        Thread(target=_loop_run).start()
