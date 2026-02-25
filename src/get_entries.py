import json
import logging
import os
import re
import requests
import typing
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(
    os.environ.get('LOGGING_LEVEL', logging.INFO)))

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


def _fill_simplified(traditional: str, simplified: str) -> str:
    """
    Fill the simplified string using traditional characters where needed.

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


def _split_numbered_definitions(text: str) -> typing.List[str]:
    """
    Split a single definition string like
    "1. first meaning  2. second meaning"
    into separate items, if it appears to be numbered.
    """
    # If there is no "1." pattern, return as-is
    if "1." not in text:
        return [text.strip()]

    # Split on occurrences like "1.", "2.", ..., keeping text after each number
    parts = re.split(r"\s*\d+\.\s*", text)
    # re.split leaves an empty string before the first match
    parts = [p.strip() for p in parts if p.strip()]
    return parts or [text.strip()]


def handler(event: typing.Dict, _: typing.Dict):
    logger.debug(event)

    query_params = event.get("queryStringParameters") or {}
    user_input = query_params.get("traditional") or query_params.get("search")

    if not user_input:
        logger.debug("No 'traditional' or 'search' query parameter provided")
        return _create_response(body=json.dumps([]))

    page = requests.get(CANTONESE_URL, params={"q": user_input})

    soup = BeautifulSoup(page.content, "html.parser")
    results_table = soup.find("table")

    entries: typing.List[typing.Dict[str, typing.Any]] = []
    if not results_table:
        logger.debug("No results table found")
        return _create_response(body=json.dumps(entries))

    for row in results_table.find_all("tr"):
        if len(entries) >= LIMIT:
            break

        cell = row.find("td")
        if not cell:
            continue

        heading = cell.find("h3", {"class": "resulthead"})
        if not heading or not heading.contents:
            continue

        # First text node contains the traditional/simplified characters block
        chinese_block = str(heading.contents[0]).replace("〕", "").replace(" ", "")
        chinese_parts = chinese_block.split("〔")

        traditional = chinese_parts[0]
        raw_simplified = "" if len(chinese_parts) == 1 else chinese_parts[1]
        simplified = _fill_simplified(traditional, raw_simplified)

        jyutping_tag = heading.find("strong")
        jyutping = jyutping_tag.get_text(strip=True) if jyutping_tag else ""

        pinyin = ""
        if heading.small and len(heading.small.contents) > 1:
            # second content item contains pinyin wrapped in braces, e.g. "{nǐ hǎo}"
            pinyin_raw = str(heading.small.contents[1]).lstrip()
            if len(pinyin_raw) >= 2:
                pinyin = pinyin_raw[1:-1]

        definition_list = cell.find("ol", {"class": "defnlist"})
        if definition_list:
            raw_definitions = [
                item.get_text(strip=True) for item in definition_list.find_all("li")
            ]
        else:
            single_definition = cell.find("p", {"class": "resultbody"})
            if not single_definition:
                continue
            raw_definitions = [single_definition.get_text(strip=True)]

        # Flatten any numbered definitions like "1. foo  2. bar" into separate items
        definitions: typing.List[str] = []
        for raw in raw_definitions:
            definitions.extend(_split_numbered_definitions(raw))

        entry = Entry(
            traditional=traditional,
            simplified=simplified,
            jyutping=jyutping,
            pinyin=pinyin,
            definitions=definitions,
        )
        entries.append(entry.__dict__)

    logger.debug(entries)
    return _create_response(body=json.dumps(entries))
