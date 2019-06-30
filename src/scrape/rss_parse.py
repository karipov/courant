import feedparser
from feedparser import FeedParserDict


def parse_url(url: str) -> FeedParserDict:
    """ Proxy function """
    return feedparser.parse(url)


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


def check_parsed(parsed: FeedParserDict, req_keys: list) -> bool:
    """
    Checks either the feed or entry of a parsed RSS feed

    :param parsed: valid, utf-8 feedparsed RSS
    :req_keys: keys that the `parsed` must contain
    :return: whether the parsed has the needed elements
    """
    return all([x in parsed.feed for x in req_keys])


# --- testing area ---

if __name__ == "__main__":
    import json
    from pathlib import Path

    config = json.load(open(Path.cwd().joinpath('src/config.json')))
    rss = json.load(open(Path.cwd().joinpath(
        'src/scrape/news-feed-list-of-countries.json'
        )))

    total_etag = 0
    total_bozo = 0
    total_sources = 0
    good_sources = 0

    print(f"Total countries: {len(rss.keys())}")
    print()

    for country in rss.keys():
        country = 'UZ'
        # print(f"New country: {rss[country]['name']}")

        for feed_data in rss[country]['sources']:
            info = parse_url(feed_data['feedlink'])

            if info.bozo == 1:
                continue

            if any([info.get('etag'), info.get('updated_parsed')]):
                continue

            if not len(info.entries) >= 1:
                continue

            print(type(info.entries[0]))
