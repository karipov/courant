import unittest
import os, sys  # noqa: E401
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../src/'
)))

from models import User, Settings, Channel, RSS, db, args  # noqa: E402


class TestMongoDB(unittest.TestCase):

    def setUp(self):
        db.drop_database(args['MONGO']['name'])

    def test_reverse_cascade_pull(self):
        u1 = User(
            user_id=77,
            settings=Settings(
                language='en'
            )
        ).save()

        u2 = User(
            user_id=200,
            users_invited=[u1],
            settings=Settings(
                language='en'
            )
        ).save()

        c1 = Channel(
            channel_id=5005,
            username='@yeetmyteet',
            description='hola mis amigos',
            last_entry_id=12,
            title='Hisp',
            subscribed=[u1, u2]
        ).save()

        r1 = RSS(
            rss_link='http://example.com/rss',
            link='http://example.com/',
            subtitle='This is an example RSS feed',
            last_entry_link='http://example.com/rss/dQw4w9WgXcQ',
            title='Example News',
            subscribed=[u1, u2]
        ).save()

        u1.delete()

        # fetching the latest data to update the cascade rules
        u2.reload()
        c1.reload()
        r1.reload()

        c1_deref_subscribed = [x.pk for x in c1.subscribed]
        r1_deref_subscribed = [x.pk for x in r1.subscribed]

        self.assertIn(u2.pk, c1_deref_subscribed)
        self.assertNotIn(u1.pk, c1_deref_subscribed)

        self.assertIn(u2.pk, r1_deref_subscribed)
        self.assertNotIn(u1.pk, r1_deref_subscribed)

        self.assertEqual(u2.users_invited, [])

    def test_feed_languages(self):
        c1 = Channel(
            channel_id=5005,
            username='@glados',
            description='Я живу в России. Я из города Липецк. Липецк...',
            last_entry_id=12,
            title='Меня зовут Маша'
        ).save()

        c2 = Channel(
            channel_id=1000,
            username='@parzival',
            description='Mi padre también va al parque a hacer deporte...',
            last_entry_id=12,
            title='El parque'
        ).save()

        self.assertEqual(c1.language, 'ru')
        self.assertEqual(c2.language, 'es')
