from mongoengine import Document
from mongoengine import StringField, IntField, ListField, DateTimeField
from datetime import datetime


class RSS(Document):
    time_added = DateTimeField(default=datetime.utcnow)

    link = StringField(unique=True, required=True)
    title = StringField(required=True)

    subtitle = StringField(default=str)
    summary = StringField(default=str)
    last_entry_link = StringField(required=True, default=str)

    subscribed = ListField(IntField(), required=True, default=list)

    meta = {
        'collection': 'rss',
        'indexes': ['$title']
    }
