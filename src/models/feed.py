from datetime import datetime

from mongoengine import Document, EmbeddedDocument
from mongoengine import ListField, DateTimeField, BooleanField
from mongoengine import StringField, LazyReferenceField
from mongoengine import CASCADE

import utility


class MetaInfo(EmbeddedDocument):
    time_added = DateTimeField(default=datetime.utcnow)
    fetched = BooleanField(required=True, default=True)


class Feed(Document):
    meta_info = EmbeddedDocument(MetaInfo, required=True, default=MetaInfo)
    subscribed = ListField(
        LazyReferenceField('User', reverse_delete_rule=CASCADE), default=list
    )
    title = StringField(required=True)
    title_ngrams = ListField(StringField, default=list)

    meta = {'allow_inheritance': True}

    def clean(self):
        """
        Override before .save()
        """
        self.title_ngrams = utility.gen_ngrams(self.title)

    def check_subscription(self, user_id: int) -> bool:
        """
        Checks whether a given user_id is in the subscribers list

        :param user_id: telegram id to check
        :return: whether user is subscribed
        """
        return user_id in [x.pk for x in self.subscribed]
