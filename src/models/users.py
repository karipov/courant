from __future__ import annotations

from mongoengine import Document
from mongoengine import IntField, DateTimeField, ListField, StringField
from mongoengine import BooleanField, EmbeddedDocument, EmbeddedDocumentField
from mongoengine import ReferenceField
from datetime import datetime

# TODO: add further constriants, e.g. max_length


class Settings(EmbeddedDocument):
    """
    Sub-document containgin User settings data.
    """
    language = StringField(required=True)
    fsm_state = StringField(default='0', regex="(\\d\\.)*\\d")
    last_msg_id = IntField()


class Subscribed(EmbeddedDocument):
    """
    Sub-document containing data that describes which services
    a User is subscribed to.
    """
    # every field here must have a default
    rss_list = ListField(ReferenceField('RSS'), default=list)
    channel_list = ListField(ReferenceField('Channel'), default=list)

    # this field is used when the user is adding channels/rss feeds.
    # Therefore, only titles of the feeds are added, as these are later
    # requested for a user to see what they have added.
    # Then, the field is cleared.
    session_list = ListField(StringField(), default=list)


class User(Document):
    """
    User class that contains all necessary information about individual users
    of the service.
    """
    user_id = IntField(unique=True, required=True)
    registered = DateTimeField(default=datetime.now)
    premium = BooleanField(required=True, default=False)
    users_invited = ListField(IntField())
    settings = EmbeddedDocumentField(Settings, required=True)
    subscribed = EmbeddedDocumentField(Subscribed, default=Subscribed)

    meta = {
        'collection': 'users'
    }

    # def clean(self):
    #     """
    #     Overrides the clean method that is activated as the document is saved
    #     This method currently creates an empty 'Subscribed' EmbeddedDocument
    #     as the User object is being created.
    #     """
    #     if not self.subscribed:
    #         self.subscribed = Subscribed()

    def add_to_invited(self, payload: int):
        """
        Adds a foreign user_id to as the invitor of self (User)

        :param received: user_id of the user to whom we are adding
        :param payload: the user_id we are adding
        """
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

        if len(user) == 0:
            raise LookupError(f"User {uid} not found.")

        if len(user) > 1:
            raise LookupError(f"More than 1 user with id: {uid} was found.")

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
        """
        Retrieves the total amount of users

        :return: total amount of users
        """
        return cls.objects.count()

    def collect_main_data(self, time_format: str = '%Y-%m-%d') -> dict:
        """
        Returns general about user information for the main menu

        :param time_format: the format for which the datetieme object is
        converted to; for more info see official docs
        https://docs.python.org/3/library/datetime.html#datetime.date.strftime
        """
        return {
            'rss_num': len(self.subscribed.rss_list),
            'channel_num': len(self.subscribed.channel_list),
            'time': self.registered.strftime(time_format)
        }
