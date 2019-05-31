from mongoengine import Document
from mongoengine import IntField, DateTimeField, ListField, StringField
from mongoengine import BooleanField, EmbeddedDocument, EmbeddedDocumentField
import datetime


class Settings(EmbeddedDocument):
    language = StringField(required=True)
    fsm_state = IntField(required=True, default=0)


class User(Document):
    user_id = IntField(unique=True, required=True)
    registered = DateTimeField(default=datetime.datetime.now)
    premium = BooleanField(required=True, default=False)
    users_invited = ListField(IntField())
    settings = EmbeddedDocumentField(Settings, required=True)

    meta = {
        'indexes': ['user_id'],
        'collection': 'users'
    }
