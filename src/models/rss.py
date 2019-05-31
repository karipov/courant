from mongoengine import Document
from mongoengine import StringField, IntField, ListField, DateTimeField
import datetime


class RSS(Document):
    time_added = DateTimeField(default=datetime.datetime.utcnow)
    link = StringField(required=True)
    subscribed = ListField(IntField(), required=True)

    meta = {
        'collection': 'rss'
    }
