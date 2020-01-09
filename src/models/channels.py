import datetime

from mongoengine import Document, EmbeddedDocument
from mongoengine import IntField, ListField, DateTimeField, BooleanField
from mongoengine import StringField, EmbeddedDocumentField

import utility


class MetaInfoChannel(EmbeddedDocument):
    time_added = DateTimeField(default=datetime.datetime.utcnow)
    fetched = BooleanField(required=True, default=True)


class Channel(Document):
    meta_info = EmbeddedDocumentField(MetaInfoChannel, default=MetaInfoChannel)
    channel_id = IntField(unique=True, required=True)
    username = StringField(required=True)

    # cannot be removed
    title = StringField(required=True, default=str)
    title_ngrams = ListField(StringField(), default=list)
    description = StringField(required=True, default=str)
    language = StringField(default=str)

    last_entry_id = IntField(required=True)

    subscribed = ListField(IntField(), default=list)

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
        self.title_ngrams = utility.gen_ngrams(self.title)

        self.language = utility.detect_language(
            [self.title, self.description]
        )

    @classmethod
    def get_channel(cls, id: int):
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
