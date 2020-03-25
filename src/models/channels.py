from __future__ import annotations

from mongoengine import IntField, StringField

import utility
from .feed import Feed


class Channel(Feed):
    channel_id = IntField(unique=True, required=True)
    username = StringField(required=True)

    # cannot be removed
    description = StringField(required=True, default=str)

    last_entry_id = IntField(required=True)

    meta = {
        'indexes': [{
            'fields': ['$title', '$description', '$title_ngrams'],
            'default_language': 'none',
            'weights': {'title': 10, 'description': 3, 'title_ngrams': 3}
        }],
        'collection': 'channels'
    }

    def clean(self):
        """
        Override
        """
        super().clean()

        self.language = utility.detect_language(
            [self.title, self.description]
        )

    @classmethod
    def get_channel(cls, id: int) -> Channel:
        """
        Retrieve a single channel given its id.

        :param id: the channel_id to retrieve for
        :return: Channel database object
        """
        assert type(id) == int
        return cls.objects(channel_id=id)[0]

    @property
    def link(self):
        return f'https://t.me/{self.username}'
