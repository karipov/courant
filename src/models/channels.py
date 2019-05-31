from mongoengine import Document
from mongoengine import IntField, ListField, DateTimeField
import datetime


class Channel(Document):
    time_added = DateTimeField(default=datetime.datetime.utcnow)
    channel_id = IntField(unique=True, required=True)
    subscribed = ListField(IntField(), required=True)

    meta = {
        'collection': 'channels'
    }
