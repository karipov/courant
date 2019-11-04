import feedparser
from feedparser import FeedParserDict

import requests
import io


def parse_url(url: str) -> FeedParserDict:
    """
    Proxy function

    requests is used for fetching the data and feedparser used only for parsing
    """
    try:
        resp = requests.get(url, timeout=(3.05, 4))
    except (requests.ReadTimeout, requests.ConnectTimeout):
        # just a random byte to cause a feedparser bozo
        resp = b'0'

    return feedparser.parse(io.BytesIO(resp.content))


def check_source(parsed: FeedParserDict) -> bool:
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


def check_parsed(parsed: FeedParserDict, req_keys: list) -> bool:
    """
    Checks either the feed or entry of a parsed RSS feed

    :param parsed: valid, utf-8 feedparsed RSS
    :req_keys: keys that the `parsed` must contain
    :return: whether the parsed has the needed elements
    """
    return all([parsed.get(x) is not None for x in req_keys])


# --- testing area ---

if __name__ == "__main__":
    import json
    from pathlib import Path

    config = json.load(open(Path.cwd().joinpath('src/config.json')))
    rss = json.load(open(Path.cwd().joinpath(
        'src/scrape/news-feed-list-of-countries.json'
        )))
