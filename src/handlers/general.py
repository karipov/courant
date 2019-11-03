"""
Handles "general" functionality that pertains to the workings of the program
post-setup.

Currently contains handlers for:
- text-messages within the set-up FSM states

Currently contains filters for:
- text messages with certain FSM states
"""
from . import txt, client, config, remove_message
from models import User, RSS, Channel
from scrape import rss_parse
import utility

from mongoengine import errors
from telegram.message import MessageEntity
from telegram.error import BadRequest


# session_list = {
#     # user_id: [str, str, str...]
# }


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
    edit_id = user.settings.last_msg_id
    state = user.settings.fsm_state
    entities = update.message.parse_entities(
        types=['mention', 'url']
    )

    main_text = (
        txt['FSM'][state]['text'][user.settings.language]
        + '\n\n'
    )

    keyboard = utility.gen_keyboard(
        txt['FSM'][state]['markup'][user.settings.language],
        txt['FSM'][state]['payload']
    )

    if not entities:
        remove_message(update, context, user)
        try:
            context.bot.edit_message_text(
                chat_id=update.message.from_user.id,
                message_id=edit_id,
                text=(
                    main_text
                    + '\n'
                    + txt['CALLBACK']['error'][user.settings.language]
                ),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except BadRequest:
            # if message isn't modified, it's ok.
            pass
        return

    for key, text in entities.items():

        # the feeds the user has already entered
        for i, sub in enumerate(user.subscribed.session_list):
            main_text += f"{i}. {sub}\n"

        if key.type == MessageEntity.URL:
            rss_compile(update, context, user, text,
                        edit_id, keyboard, main_text)
            continue
        if key.type == MessageEntity.MENTION:
            channel_compile(update, context, user, text,
                            edit_id, keyboard, main_text)
            continue


def rss_compile(update, context, user, link, edit_id, keyboard, main_text):
    """
    Handler: fsm:2.1 -> 3

    :param user: mongoengine User object
    :param link: the extracted entity from the message
    """
    news = rss_parse.parse_url(link)
    language = user.settings.language
    state = user.settings.fsm_state

    # almost like it "absorbs" a message
    remove_message(update, context, user)

    # check the source for possible errors, such as bozo and format
    if not rss_parse.check_source(news):
        try:
            context.bot.edit_message_text(
                chat_id=user.user_id,
                message_id=edit_id,
                text=(
                    main_text
                    + '\n'
                    + txt['CALLBACK']['error_link'][language]
                ),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except BadRequest:
            pass
        return

    # check the actual feed, i.e.:
    # stuff like title, subtitle, link and such.
    checked_feed = rss_parse.check_parsed(
        news.feed, config['SCRAPE']['RSS']['req_feed_keys']
    )

    # implement the checking described above
    if not checked_feed:
        try:
            context.bot.edit_message_text(
                chat_id=user.user_id,
                message_id=edit_id,
                text=(
                    main_text
                    + '\n'
                    + txt['CALLBACK']['error_feed'][language]
                ),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except BadRequest:
            pass
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
        try:
            context.bot.edit_message_text(
                chat_id=user.user_id,
                message_id=edit_id,
                text=(
                    main_text
                    + '\n'
                    + txt['CALLBACK']['error_entries'][language]
                ),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except BadRequest:
            pass
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
            try:
                context.bot.edit_message_text(
                    chat_id=user.user_id,
                    message_id=edit_id,
                    text=(
                        main_text
                        + '\n'
                        + txt['CALLBACK']['repeated_rss'][language]
                    ),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            except BadRequest:
                pass
            return

        db_news.subscribed.append(user.user_id)
        db_news.fetched = True
        db_news.save()

    user.subscribed.rss_list.append(db_news.pk)
    user.subscribed.session_list.append(news.feed.title)
    user.save()

    feed_formatted = f"<a href=\"{db_news.link}\">" + \
        f"{utility.escape(db_news.title)}</a>"

    # TODO: fix txt from CALLBACK to FSM
    # does this mean other changes such as tree checking?
    if not len(news.entries) > 0:
        try:
            context.bot.edit_message_text(
                chat_id=user.user_id,
                message_id=edit_id,
                text=(
                    main_text
                    + '\n'
                    + txt['CALLBACK']['empty_feed'][language]
                ),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except BadRequest:
            pass
        return

    db_news.last_entry_link = news.entries[0].link
    db_news.save()

    # because this function is used both in the setup and post-setup, we assign
    # a special 'b' sub-state that the user never takes on, but that contains
    # the buttons required to move on to the next FSM state.
    context.bot.edit_message_text(
        chat_id=user.user_id,
        message_id=edit_id,
        text=(
            main_text
            + '\n'
            + txt['FSM'][f'{state}b']['text'][language].format(feed_formatted)
        ),
        reply_markup=keyboard,
        parse_mode='HTML'
    )


def channel_compile(update, context, user, text, edit_id, keyboard, main_text):
    """ Handler: fsm:2.1 -> ___ """
    language = user.settings.language
    state = user.settings.fsm_state

    # TODO: don't use a context menu -> takes too long to start up.
    # use client.start() at initializiation.
    with client:
        # TODO: make sure the client doesn't get Floodwaited..
        # If more accounts (i.e. clients) are to be used, there needs to be
        # an efficient way to distribute the load.
        channel = client.get_chat(text)

        if channel.type != 'channel':
            context.bot.send_message(
                chat_id=user.user_id,
                text=txt['CALLBACK']['error_channel'][language]
            )
            return

        last_message_id = client.get_history(
            chat_id=channel.id,
            limit=1
        )[0].message_id

    try:
        db_channel = Channel(
            channel_id=channel.id,
            last_entry_id=last_message_id,
            title=channel.title,
            description=channel.description
        ).save()
    except errors.NotUniqueError:
        db_channel = Channel.get_channel(channel.id)

        if user.user_id in db_channel.subscribed:
            context.bot.send_message(
                chat_id=user.user_id,
                text=txt['CALLBACK']['repeated_channel'][language]
            )
            return

    # adding the user to subscribed list in the channel document
    db_channel.subscribed.append(user.user_id)
    db_channel.save()
    # adding channel to subscribed on the user document
    user.subscribed.channel_list.append(db_channel.pk)
    user.subscribed.session_list.append(db_channel.title)
    user.save()

    # format the channel looks, etc.
    channel_formatted = f"<a href=\"https://t.me/{channel.username}\">" + \
        f"{utility.escape(channel.title)}</a>"

    context.bot.send_message(
        chat_id=user.user_id,
        text=txt['FSM'][f'{state}b']['text'][language].format(
            channel_formatted
        ),
        parse_mode='HTML',
        reply_markup=utility.gen_keyboard(
            txt['FSM'][f'{state}b']['markup'][language],
            txt['FSM'][f'{state}b']['payload']
        )
    )


def explore_compile(update, context, user):
    pass
