import logging
import os
import requests
import typing
import base64


logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(
    os.environ.get('LOGGING_LEVEL', logging.INFO)))


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


def handler(event: typing.Dict, _: typing.Dict):
    logger.debug(event)

    phrase = event['queryStringParameters']['traditional']
    url = f"https://translate.google.com.vn/translate_tts?ie=UTF-8&q={phrase}&tl=yue&client=tw-ob"
    try:
        audio = requests.get(url)
        encoded_audio = base64.b64encode(audio.content).decode("utf-8")

        return {
            "isBase64Encoded": True,
            "statusCode": 200,
            "headers": {
                "content-type": "audio/mpeg",
                "Access-Control-Allow-Origin": "*",
            },
            "body": encoded_audio,
        }
    except Exception:
        logger.exception("Failed to get pronunciation audio")
        return _create_response(body='{"message": "Unknown error"}', code=500)
