from __future__ import annotations

from mongoengine import Document
from mongoengine import StringField, IntField, ListField, DateTimeField
from mongoengine import BooleanField
from datetime import datetime


class RSS(Document):
    time_added = DateTimeField(default=datetime.utcnow)
    fetched = BooleanField(default=True)

    rss_link = StringField(unique=True, required=True)
    link = StringField(unique=True, required=True)
    title = StringField(required=True)

    subtitle = StringField(default=str)
    summary = StringField(default=str)
    last_entry_link = StringField(required=True, default=str)

    subscribed = ListField(IntField(), default=list)

    meta = {
        'collection': 'rss',
        'indexes': ['$title']
    }

    @classmethod
    def get_rss(cls, rss_link: str) -> RSS:
        """
        Fetches a single RSS feed

        :param link: the link of the RSS feed to fetch an object for
        :return: the MongoEngine RSS object
        """
        rss = cls.objects(rss_link=rss_link)

        if len(rss) == 0:
            raise LookupError(f"RSS feed with link {rss_link} not found.")
        if len(rss) > 1:
            raise LookupError(
                f"More than one feed with link {rss_link} found."
            )

        return rss[0]

    def check_subscription(self, uid: int) -> bool:
        """
        Checks whether an RSS feed has a given user in its subscription

        :param uid: telegram-given user_id
        :return: whether or not the the user is subscribed
        """
        return uid in self.subscribed
