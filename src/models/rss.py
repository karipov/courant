from __future__ import annotations

from mongoengine import StringField

import utility
from .feed import Feed


class RSS(Feed):
    rss_link = StringField(unique=True, required=True)
    link = StringField(unique=True, required=True)

    subtitle = StringField(default=str)
    summary = StringField(default=str)

    last_entry_link = StringField(required=True, default=str)

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
        super().clean()

        self.language = utility.detect_language(
            [self.title, self.subtitle, self.summary]
        )

    @classmethod
    def get_rss(cls, rss_link: str) -> RSS:
        """
        Fetches a single RSS feed

        :param link: the link of the RSS feed to fetch an object for
        :return: the MongoEngine RSS object
        """
        return cls.objects(rss_link=rss_link)[0]
