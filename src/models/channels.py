from mongoengine import Document
from mongoengine import IntField, ListField, DateTimeField, BooleanField
from mongoengine import StringField
import datetime


class Channel(Document):
    time_added = DateTimeField(default=datetime.datetime.utcnow)
    fetched = BooleanField(required=True, default=True)
    channel_id = IntField(unique=True, required=True)
    username = StringField(required=True)
    # TODO: need a username field.

    # cannot be removed
    title = StringField(required=True, default=str)
    description = StringField(required=True, default=str)

    last_entry_id = IntField(required=True)

    subscribed = ListField(IntField(), default=list)

    meta = {
        'collection': 'channels'
    }

    @classmethod
    def get_channel(cls, id: int):
        """
        Retrieve a single channel given its id.

        :param id: the channel_id to retrieve for
        :return: Channel database object
        """
        assert type(id) == int
        return cls.objects(channel_id=id)[0]
