from __future__ import annotations
from datetime import datetime

from mongoengine import Document, EmbeddedDocument
from mongoengine import StringField, IntField, ListField, DateTimeField
from mongoengine import BooleanField, EmbeddedDocumentField

import utility


class MetaInfoRSS(EmbeddedDocument):
    time_added = DateTimeField(default=datetime.utcnow)
    fetched = BooleanField(required=True, default=True)


class RSS(Document):
    meta_info = EmbeddedDocumentField(MetaInfoRSS, default=MetaInfoRSS)
    rss_link = StringField(unique=True, required=True)
    link = StringField(unique=True, required=True)

    # cannot be removed
    title = StringField(required=True)
    title_ngrams = ListField(StringField(), default=list)
    language = StringField(required=True, default=str)
    subtitle = StringField(default=str)
    summary = StringField(default=str)

    last_entry_link = StringField(required=True, default=str)

    subscribed = ListField(IntField(), required=True, default=list)

    meta = {
        'indexes': [{
            'fields': ['$title', '$subtitle', '$summary', '$title_ngrams'],
            'default_language': 'none',
            'weights': {
                'title': 10,
                'title_ngrams': 3,
                'subtitle': 3,
                'summary': 3
            }
        }],
        'collection': 'rss'
    }

    def clean(self):
        """
        Override
        """
        # RSS titles tend to be longer, so min_size higher
        self.title_ngrams = utility.gen_ngrams(self.title, min_size=4)
        self.language = utility.detect_language(
            [self.title, self.subtitle, self.summary]
        )

        if self.meta_info.fetched and not self.check_subscribed():
            raise Exception(f"No subscribers but {self.title} fetched.")

    def check_subscription(self, uid: int) -> bool:
        """
        Checks whether an RSS feed has a given user in its subscription

        :param uid: telegram-given user_id
        :return: whether or not the the user is subscribed
        """
        return uid in self.subscribed

    def check_subscribed(self) -> bool:
        """
        Checks whether RSS has any subscribers

        :return: True for yes, False for no.
        """
        try:
            if len(self.subscribed) == 0:
                return False
        except TypeError:  # field might not exist
            return False

        return True

    @classmethod
    def get_rss(cls, rss_link: str) -> RSS:
        """
        Fetches a single RSS feed

        :param link: the link of the RSS feed to fetch an object for
        :return: the MongoEngine RSS object
        """
        rss = cls.objects(rss_link=rss_link)

        # not needed as rss should be a unique field.
        # if len(rss) == 0:
        #     raise LookupError(f"RSS feed with link {rss_link} not found.")
        # if len(rss) > 1:
        #     raise LookupError(
        #         f"More than one feed with link {rss_link} found."
        #     )

        return rss[0]
