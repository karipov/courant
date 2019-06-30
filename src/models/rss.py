from mongoengine import Document
from mongoengine import StringField, IntField, ListField, DateTimeField
from datetime import datetime


class RSS(Document):
    time_added = DateTimeField(default=datetime.datetime.utcnow)

    link = StringField(required=True)
    title = StringField(required=True)
    subtitle = StringField(required=True)
    last_published = DateTimeField(required=True, default=datetime.utcnow)
    subscribed = ListField(IntField(), required=True)

    def clean(self):
        """
        Additional validation for RSS.
        """
        if len(self.title) > 255:
            self.title = ''.join(self.title.split()[:255])
        if len(self.subtitle) > 255:
            self.subtitle = ''.join(self.subtitle.split()[:255])

    meta = {
        'collection': 'rss',
        'indexes': ['$title']
    }
