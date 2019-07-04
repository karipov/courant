from __future__ import annotations

from mongoengine import Document
from mongoengine import IntField, DateTimeField, ListField, StringField
from mongoengine import BooleanField, EmbeddedDocument, EmbeddedDocumentField
from mongoengine import ReferenceField
from datetime import datetime


class Settings(EmbeddedDocument):
    language = StringField(required=True)
    fsm_state = StringField(default='0', regex="(\\d\\.)*\\d")


class Subscribed(EmbeddedDocument):
    # every field here must have a default
    rss_list = ListField(ReferenceField('RSS'), default=list)


class User(Document):
    user_id = IntField(unique=True, required=True)
    registered = DateTimeField(default=datetime.now)
    premium = BooleanField(required=True, default=False)
    users_invited = ListField(IntField)
    settings = EmbeddedDocumentField(Settings, required=True)
    subscribed = EmbeddedDocumentField(Subscribed)

    meta = {
        'indexes': ['user_id'],
        'collection': 'users'
    }

    def clean(self):
        if not self.subscribed:
            self.subscribed = Subscribed()

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

    # SHORTHANDS
    @classmethod
    def get_user(cls, uid: int) -> User:
        """
        Fetches a single user for a given user_id

        :param uid: the user_id to fetch by
        :return: User object
        """
        user = cls.objects(user_id=uid)

        # TODO: should raise two different errors
        if len(user) == 0 or len(user) > 1:
            raise LookupError(f"User {uid} not found.")

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

    @classmethod
    def retrieve_total(cls) -> int:
        """ Retrieves the total amount of users """
        return cls.objects.count()
