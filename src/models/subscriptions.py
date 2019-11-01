from mongoengine import Document, EmbeddedDocument
from mongoengine import IntField, StringField, ListField
from mongoengine import EmbeddedDocumentField


# TODO: currently not implemnented...

CONTENT_TYPES = (
    ('text', 'Text'),
    ('audio', 'Audio'),
    ('document', 'Documents'),
    ('sticker', 'Stickers'),
    ('photo', 'Photos'),
    ('video', 'Videos'),
    ('video_note', 'Video Notes'),
    ('voice', 'Voice Notes'),
    ('location', 'Location')
)

POPULARITY_PERCENTAGE = list(range(0, 101, 10))


class ChannelFilters(EmbeddedDocument):
    popularity = IntField(default=0, choices=POPULARITY_PERCENTAGE)

    yes_hashtags = ListField(StringField)
    no_hashtags = ListField(StringField)

    yes_content_type = ListField(StringField, choices=CONTENT_TYPES)
    no_content_type = ListField(StringField, choices=CONTENT_TYPES)

    yes_words = ListField(StringField)
    no_words = ListField(StringField)


class Subscriptions(Document):
    user_id = IntField(unique=True, required=True)
    subscriptions = ListField(IntField)
    channel_filters = EmbeddedDocumentField(ChannelFilters)
