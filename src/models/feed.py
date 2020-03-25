from datetime import datetime

from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField
from mongoengine import ListField, DateTimeField, BooleanField
from mongoengine import StringField, LazyReferenceField
from mongoengine import PULL

import utility
from .users import User


class MetaInfo(EmbeddedDocument):
    time_added = DateTimeField(required=True, default=datetime.utcnow)
    fetched = BooleanField(required=True, default=True)


class Feed(Document):
    meta_info = EmbeddedDocumentField(
        MetaInfo, required=True, default=MetaInfo
    )
    subscribed = ListField(
        LazyReferenceField(User, reverse_delete_rule=PULL),
        default=list
    )
    title = StringField(required=True)
    title_ngrams = ListField(StringField(), default=list)
    language = StringField(required=True, default=str)

    meta = {
        'allow_inheritance': True,
        'abstract': True
    }

    def clean(self):
        """
        Override before .save()
        """
        self.title_ngrams = utility.gen_ngrams(self.title, min_size=4)

    def check_subscription(self, user_id: int) -> bool:
        """
        Checks whether a given user_id is in the subscribers list

        :param user_id: telegram id to check
        :return: whether user is subscribed
        """
        return user_id in [x.user_id for x in self.subscribed]
