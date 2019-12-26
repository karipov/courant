"""
Scraper class that scrapes and distrubutes channel and rss information to users
"""
from pathlib import Path
from threading import Thread
import time
import json

from pyrogram import Client


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
        self.txt = json.load(
            open(Path.cwd().joinpath('src/interface/replies.json'))
        )

        # must not forget to stop the client.
        self.client.start()

    from ._channel_scrape import update_channels

    def run(self):
        """
        Function to launch & run loop in a separate thread with updates.
        """
        def _loop_run():
            while True:
                self.update_channels()
                time.sleep(10)  # avoid floods

        Thread(target=_loop_run).start()
