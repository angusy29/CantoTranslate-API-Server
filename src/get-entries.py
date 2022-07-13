import json
import logging
import os
import requests
import typing
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ['LOGGING_LEVEL']))

CANTONESE_URL = "https://cantonese.org/search.php?q="
LIMIT = 5


@dataclass
class Entry:
    traditional: str
    simplified: str
    jyutping: str
    pinyin: str
    definitions: typing.List[str]


def _create_response(body: str, code: int = 200) -> object:
    return {
        'isBase64Encoded': False,
        'statusCode': code,
        'headers': {
            'content-type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': body
    }


def _fill_simplified(traditional: str, simplified: str) -> None:
    """
    Fills simplified with traditional words if it does not
    have a simplfieid equivalent

    :param traditional: Traditional Chinese words
    :param simplified: Simplified Chinese words, if it doesn't have
                    a simplified equivalent, it will use - as placeholder
    :return: returns simplified Chinese with all - filled
    """
    # converts any non 0 length string into a list of characters
    simplified = list(simplified)
    if not len(simplified):
        # converts any length 0 string into dashes
        simplified = ['-' for _ in range(len(traditional))]

    for i in range(len(traditional)):
        if simplified[i] == '-':
            simplified[i] = traditional[i]

    return ''.join(simplified)


def handler(event: typing.Dict, _: typing.Dict):
    logger.debug(event)
    user_input = event['queryStringParameters']['search']
    page = requests.get(f'{CANTONESE_URL}{user_input}')

    soup = BeautifulSoup(page.content, "html.parser")
    rows = soup.find("table")

    entries = []
    for idx, row in enumerate(rows):
        # shortcut to only allow API to return max limit results
        if idx >= LIMIT:
            break

        cc_canto_entry = row.find("td")
        cc_canto_entry_heading = cc_canto_entry.find(
            "h3", {"class": "resulthead"})

        # Example return value: ['哈囉', '-啰']
        cc_canto_entry_chinese = cc_canto_entry_heading.contents[0].replace(
            '〕', '').replace(' ', '').split('〔')

        traditional = cc_canto_entry_chinese[0]
        simplified = '' if len(
            cc_canto_entry_chinese) == 1 else cc_canto_entry_chinese[1]
        jyutping = cc_canto_entry_heading.strong.text
        # strip the leading space and strip out the squiggly brackets
        # from the front and back
        pinyin = cc_canto_entry_heading.small.contents[1].lstrip()[1:-1]

        # lists of definitions are encapsulated in defnlist
        cc_canto_definition_list = cc_canto_entry.find(
            "ol", {"class": "defnlist"})

        if cc_canto_definition_list:
            definitions = [
                definition.text for definition in cc_canto_definition_list.find_all('li')]
        else:
            cc_canto_single_definition_entry = cc_canto_entry.find(
                "p", {"class": "resultbody"})
            definitions = [cc_canto_single_definition_entry.text]

        entry = Entry(traditional=traditional, simplified=_fill_simplified(traditional, simplified),
                      jyutping=jyutping, pinyin=pinyin, definitions=definitions)

        entries.append(entry.__dict__)

    logger.debug(entries)
    return _create_response(body=json.dumps(entries))
