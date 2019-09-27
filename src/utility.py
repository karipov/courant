"""
Helper module for various functionality
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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


def check_fsm(current: str, future: str, tree: dict) -> bool:
    """
    Checks if the user is correctly following the Finite State Machine

    :param current: current FSM state of the user
    :param future: FSM that is to be set
    :param tree: the order in which the FSM must be executed
    :return: whether or not user is doing a legal operation
    """
    # it's ok for a user to remain in the same state after multiple actions
    # such as the deletion of RSS feeds in the same menu.
    # therefore, we allow for the below to proceed
    if current == future:
        return True

    # recusrive function
    def lookup(tree, a, b, flag=False):
        if tree['name'] == b and flag:
            return True
        return any(lookup(
            j, a, b, tree['name'] == a
            ) for j in tree.get('children', []))

    return any([lookup(tree, current, future), lookup(tree, future, current)])


# testing area:
if __name__ == "__main__":
    tree = {
        "name": "1",
        "children": [
            {
                "name": "2",
                "children": [
                    {
                        "name": "2.1",
                        "children": [{"name": "3"}]
                    },
                    {
                        "name": "2.2",
                        "children": [
                            {
                                "name": "2.2.1",
                                "children": [{"name": "3"}]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    current = "2.2.1"
    future = "2.2"

    print(check_fsm(
        current=current,
        future=future,
        tree=tree
    ))
