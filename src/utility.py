"""
Helper module for various functionality
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def extract_payload(text, num_values=1, delim=' '):
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
