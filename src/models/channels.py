import datetime

from mongoengine import Document
from mongoengine import IntField, ListField, DateTimeField, BooleanField
from mongoengine import StringField
import pycld2

LANGUAGES = [
    'en', 'da', 'nl', 'fi', 'fr', 'de', 'hu', 'it',
    'ro', 'ru', 'es', 'sv', 'tr', 'nb', 'pt'
]


class Channel(Document):
    time_added = DateTimeField(default=datetime.datetime.utcnow)
    fetched = BooleanField(required=True, default=True)
    channel_id = IntField(unique=True, required=True)
    username = StringField(required=True)

    # cannot be removed
    title = StringField(required=True, default=str)
    description = StringField(required=True, default=str)
    language = StringField(default=str)

    last_entry_id = IntField(required=True)

    subscribed = ListField(IntField(), default=list)

    meta = {
        'indexes': [{
            'fields': ['$title', '$description'],
            'default_language': 'none',
            'weights': {'title': 10, 'description': 3}
        }],
        'collection': 'channels'
    }

    def clean(self):
        """
        Override
        """
        total_strings = self.title + ' ' + self.description

        _, _, details = pycld2.detect(
            total_strings, isPlainText=True, bestEffort=True
        )

        lang_codes = [x[1] for x in details]
        selected = [x for x in lang_codes if x in LANGUAGES]

        try:
            self.language = selected[0]
        except IndexError:
            self.language = 'none'

    @classmethod
    def get_channel(cls, id: int):
        """
        Retrieve a single channel given its id.

        :param id: the channel_id to retrieve for
        :return: Channel database object
        """
        assert type(id) == int
        return cls.objects(channel_id=id)[0]
