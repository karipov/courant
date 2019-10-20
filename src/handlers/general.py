"""
Handles "general" functionality that pertains to the workings of the program
post-setup.

Currently contains handlers for:
- text-messages within the set-up FSM states

Currently contains filters for:
- text messages with certain FSM states
"""
from .shared import txt, config, remove_message
from models import User, RSS
from scrape import rss_parse
import utility

from mongoengine import errors
from telegram.message import MessageEntity


def master(update, context):
    """
    This handler is implemented to generally deal with FSM states in incoming
    messages.
    """
    db_user = User.get_user(update.message.from_user.id)
    user_state = db_user.settings.fsm_state

    # the reason why a list such as this is used instead of a tree, such as the
    # one used in callback.py (master_callback) is due to the fact that
    # messages don't carry future state information -> but they don't need to.
    # this is done in the functions.
    allowed_states = ['2.1', '2.2', '3.3.1']

    if user_state not in allowed_states:
        remove_message(update, context, db_user)
        return

    fsm_options = {
        '2.1': manual_compile,
        '2.2': explore_compile,

        '3.3.1': manual_compile
    }

    fsm_options[user_state](update, context, db_user)


def general_compile(update, context, user):
    """
    Handles general messages for compilation.

    This could be useful in case the need arises to add more services,
    which will all basically use the same backend or same pieces of code.
    """
    # TODO: this will need an extra parameter to indicate the "future" FSM
    # state that needs to be set, because messages don't tend to carry
    # this information.
    raise NotImplementedError()


def manual_compile(update, context, user):
    """
    Detects whether the answer to the Manual Entry is a link, or username
    """
    entities = update.message.parse_entities(
        types=['mention', 'url']
    )

    if not entities:
        context.bot.send_message(
            chat_id=update.message.from_user.id,
            text=txt['CALLBACK']['error'][user.settings.language]
        )
        return

    for key, link in entities.items():
        if key.type == MessageEntity.URL:
            rss_compile(update, context, user, link)
            continue

        # TODO: implement Telegram channels.


def rss_compile(update, context, user, link):
    """
    Handler: fsm:2.1 -> 3

    :param user: mongoengine User object
    :param link: the extracted entity from the message
    """
    news = rss_parse.parse_url(link)
    language = user.settings.language
    state = user.settings.fsm_state

    # check the source for possible errors, such as bozo and format
    if not rss_parse.check_source(news):
        context.bot.send_message(
            chat_id=user.user_id,
            text=txt['CALLBACK']['error_link'][language]
        )
        return

    # check the actual feed, i.e.:
    # stuff like title, subtitle, link and such.
    checked_feed = rss_parse.check_parsed(
        news.feed, config['SCRAPE']['RSS']['req_feed_keys']
    )

    # implement the checking described above
    if not checked_feed:
        context.bot.send_message(
            chat_id=user.user_id,
            text=txt['CALLBACK']['error_feed'][language]
        )
        return

    # all entries must be checked for certain required elements
    # this must strike a fine balance between universality and enough
    # information for a good display of the RSS feed
    checked_all_entries = all([
        rss_parse.check_parsed(
            x, config['SCRAPE']['RSS']['req_entry_keys']
            ) for x in news.entries
        ])

    # implement the checking above
    if not checked_all_entries:
        context.bot.send_message(
            chat_id=user.user_id,
            text=txt['CALLBACK']['error_entries'][language]
        )
        return

    # if all the checks have so far been passed, then we create the RSS
    # feed in our database and register it - unless it already exists for the
    # user.
    try:
        db_news = RSS(
            rss_link=link,
            link=news.feed.link,
            title=news.feed.title,
            subtitle=news.feed.get('subtitle', ''),
            summary=news.feed.get('summary', ''),
        )
        db_news.subscribed.append(user.user_id)
        db_news.save()

    # if an identical RSS feed exists instead of saving, we fetch the existing
    except errors.NotUniqueError:
        db_news = RSS.get_rss(rss_link=link)

        if user.user_id in db_news.subscribed:
            context.bot.send_message(
                chat_id=user.user_id,
                text=txt['CALLBACK']['repeated_rss'][language]
            )
            return

        db_news.subscribed.append(user.user_id)
        db_news.fetched = True
        db_news.save()

    user.subscribed.rss_list.append(db_news.pk)
    user.save()

    feed_formatted = f"<a href=\"{db_news.link}\">{db_news.title}</a>"

    # TODO: fix txt from CALLBACK to FSM
    # does this mean other changes such as tree checking?
    if not len(news.entries) > 0:
        context.bot.send_message(
            chat_id=user.user_id,
            text=feed_formatted +
            txt['CALLBACK']['empty_feed'][language],
            parse_mode='HTML'
        )
        return

    db_news.last_entry_link = news.entries[0].link
    db_news.save()

    # because this function is used both in the setup and post-setup, we assign
    # a special 'b' sub-state that the user never takes on, but that contains
    # the buttons required to move on to the next FSM state.
    context.bot.send_message(
        chat_id=user.user_id,
        text=txt['FSM'][f'{state}b']['text'][language].format(
            feed_formatted
        ),
        parse_mode='HTML',
        reply_markup=utility.gen_keyboard(
            txt['FSM'][f'{state}b']['markup'][language],
            txt['FSM'][f'{state}b']['payload']
        )
    )


def channel_compile(update, context, user):
    """ Handler: fsm:2.1 -> ___ """
    pass


def explore_compile(update, context, user):
    pass
