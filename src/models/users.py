from mongoengine import Document
from mongoengine import IntField, DateTimeField, ListField, StringField
from mongoengine import BooleanField, EmbeddedDocument, EmbeddedDocumentField
import datetime


class Settings(EmbeddedDocument):
    language = StringField(required=True)
    fsm_state = IntField(default=0)


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

    @classmethod
    def check_exists(cls, uid: int) -> bool:
        """
        Checks if the User with a certain uid already exists in the database

        :param uid: which user id to check for
        :return: whether the user exists or not
        """
        user = cls.objects(user_id=uid)

        if not user:
            return False
        if len(user) > 1:
            raise TypeError
            return

        return True
