"""
Helper module for various functionality. If gets too large will be turned
into a folder. For now - manageable.
"""
import html
import io
import random

import feedparser
import langdetect
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def parse_url(url: str, timeout=(3.05, 4)) -> feedparser.FeedParserDict:
    """
    Proxy function

    requests is used for fetching the data and feedparser used only for parsing
    """
    try:
        resp = requests.get(url, timeout=timeout)
    except (requests.ReadTimeout, requests.ConnectTimeout,
            requests.ConnectionError):
        # just a random byte to cause a feedparser bozo
        resp = b'0'
    except requests.exceptions.MissingSchema:
        resp = requests.get(f'http://{url}', timeout=timeout)

    try:
        content = resp.content
    except AttributeError:  # if response has no content attribute
        content = b'0'

    return feedparser.parse(io.BytesIO(content))


def check_source(parsed: feedparser.FeedParserDict) -> bool:
    """
    Checks the parsed feed for encoding et bozo

    :param parsed: potentially invalid RSS feed
    :return: whether the RSS feed is actually valid or not
    """
    if parsed.bozo == 1:
        return False
    if not parsed.get('encoding'):
        return False
    if not parsed.encoding.upper() == 'utf-8'.upper():
        return False

    return True


def check_parsed(parsed: feedparser.FeedParserDict, req_keys: list) -> bool:
    """
    Checks either the feed or entry of a parsed RSS feed

    :param parsed: valid, utf-8 feedparsed RSS
    :req_keys: keys that the `parsed` must contain
    :return: whether the parsed has the needed elements
    """
    return all([parsed.get(x) is not None for x in req_keys])


def escape(text: str):
    """
    Escape HTML tags.

    :param text: non-escaped string
    :return: escaped string
    """
    return html.escape(text)


def extract_payload(text: str, num_values=1, delim=' ') -> list:
    """
    Extract additional information from commands

    :param text: the entire command string
    :param num_values:
    """
    return text.split(delim)[1:num_values+1]


def gen_keyboard(label: list, data: list, width=2) -> InlineKeyboardMarkup:
    """
    Generates a markup keyboard for a list of labels and their callback data
    :param label: associated visible text for each button
    :param data: data associated with each button
    :param width: the number of buttons allowed on a single row
    """
    assert len(label) == len(data)
    tuples = zip(label, data)
    buttons = [InlineKeyboardButton(l, callback_data=c) for l, c in tuples]
    menu = [buttons[i:i + width] for i in range(0, len(buttons), width)]

    return InlineKeyboardMarkup(menu)


def lang(lang: str, allowed: list, default='en') -> str:
    """
    Prunes the language_code from update object.

    :param lang: the language_code string
    :param allowed: the allowed language codes
    :param default: the default language code
    :return: the pruned language code
    """
    if lang is None:
        return default

    if lang not in allowed:
        return default
    else:
        return lang


def gen_ngrams(text: str, min_size: int = 2, max_len: int = 120) -> list:
    """
    Generates and assigns a list of n-grams for a given text

    :param text: text to be n-gramed
    :param min_size: minimum character length for each 'gram'
    :param max_len: maximum number of n-gram's
    """
    length = len(text)
    size_range = range(min_size, max(length, min_size) + 1)

    n_grams = list(set(
        text[i:i + size].strip()  # remove whitespace
        for size in size_range
        for i in range(0, max(0, length - size) + 1)
    ))

    # cannot allow the list to be too large, so random deletion.
    # TODO: better way to handle this?
    if len(n_grams) > max_len:
        to_delete = set(random.sample(
            range(len(n_grams)), abs(max_len - len(n_grams))
        ))
        n_grams = [x for i, x in enumerate(n_grams) if i not in to_delete]

    return n_grams


def detect_language(all_strings: list) -> str:
    """
    :param all_strings: list of strings to detect langs from.
    """
    LANGUAGES = [
        'en', 'da', 'nl', 'fi', 'fr', 'de', 'hu', 'it',
        'ro', 'ru', 'es', 'sv', 'tr', 'nb', 'pt'
    ]

    total = ' '.join(all_strings)
    code = langdetect.detect(total)

    if code not in LANGUAGES:
        return 'none'

    return code
