"""
Methods for the Scrape class that enable the collection and distribution of
information from rss feeds to users
"""
import html

from models import RSS, User
import utility


def update_rss_feeds(self):
    """
    RSS Feed updater function that iterates over the rss feeds in the
    database and associated subscribed users to send them new articles.
    """
    for feed in RSS.objects:
        parsed = utility.parse_url(feed.rss_link)

        # even though a feed check is done when the it is added to the
        # database, xml files can change any time
        if not self._full_feed_check(parsed):
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

        new_entries = self._get_new_entries(
            db_feed=feed,
            rss_parsed=parsed
        )

        for user_id in feed.subscribed:
            for entry in new_entries:
                self.bot.send_message(
                    text=self.txt['UPD_RSS']['formatted'].format(
                        html.escape(entry.title), entry.link
                    ),
                    chat_id=user_id,
                    parse_mode='HTML'
                )


def _full_feed_check(self, rss_parsed) -> bool:
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


def _get_new_entries(self, db_feed: RSS, rss_parsed) -> list:
    """
    Grabs new entries from an RSS feed

    :param db_feed: MongoEngine RSS feed object
    :param rss_parsed: parsed & checked RSS feed
    :return: list of new entries
    """
    if len(rss_parsed.entries) == 0:
        return []

    last_entry_link = rss_parsed.entries[0].link

    if last_entry_link == db_feed.last_entry_link:
        return []

    entries = []

    for entry in rss_parsed.entries:
        if entry.link == db_feed.last_entry_link:
            break

        entries.append(entry)

    db_feed.last_entry_link = last_entry_link
    db_feed.save()

    return entries
