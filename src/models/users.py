from __future__ import annotations

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

    def add_to_invited(self, payload: int):
        """
        :param received: user_id of the user to whom we are adding
        :param payload: the user_id we are adding
        """
        # TODO: add a user_id to invited list
        if payload in self.users_invited or self.user_id == payload:
            return

        self.users_invited.append(payload)
        self.save()

    @classmethod
    def get_user(cls, uid: int) -> User:
        """
        Fetches a single user for a given user_id

        :param uid: the user_id to fetch by
        :return: User object
        """
        user = cls.objects(user_id=uid)

        if len(user) == 0 or len(user) > 1:
            return None

        # return the single element form the list
        return user[0]

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
