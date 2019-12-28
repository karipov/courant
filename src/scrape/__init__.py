"""
Scraper class that scrapes and distrubutes channel and rss information to users
"""
from pathlib import Path
from threading import Thread
import time
import json
import html

from pyrogram import Client

from models import RSS, User
import utility


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
        self.config = config
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

    def update_rss_feeds(self):
        """
        RSS Feed updater function that iterates over the rss feeds in the
        database and associated subscribed users to send them new articles.
        """
        for feed in RSS.objects:
            parsed = utility.parse_url(feed.rss_link)

            if not self.full_feed_check(parsed):
                for user_id in feed.subscribed:
                    user = User.get_user(user_id)
                    user_lang = user.settings.language

                    self.bot.send_message(
                        text=self.txt['UPD_RSS']['bad_feed'][user_lang].format(
                            feed.rss_link, html.escape(feed.title)
                        ),
                        chat_id=user_id,
                        parse_mode='HTML'
                    )

                feed.delete()
                return

            for user_id in feed.subscribed:
                pass  # FIXME: finish this up.

    def full_feed_check(self, rss_parsed) -> bool:
        """
        Checks the RSS feed for any oddities to have at least some uniformity

        :param rss_link: feedparsed rss xml content
        :return: True if good feed, False if bad feed
        """
        if not utility.check_source(rss_parsed):
            return False

        checked_feed = utility.check_parsed(
            rss_parsed.feed, self.config['SCRAPE']['RSS']['req_feed_keys']
        )

        if not checked_feed:
            return False

        checked_all_entries = all([
            utility.check_parsed(
                x, self.config['SCRAPE']['RSS']['req_entry_keys']
                ) for x in rss_parsed.entries
        ])

        if not checked_all_entries:
            return False

        # if all checks passed -> feed passes
        return True
