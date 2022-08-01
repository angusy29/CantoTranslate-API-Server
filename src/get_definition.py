import boto3
import json
import logging
import os
import typing
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from dataclasses import dataclass
from functools import lru_cache

TABLE_NAME = 'CantoTranslate'

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(
    os.environ.get('LOGGING_LEVEL', logging.INFO)))


@dataclass
class Definition:
    traditional: str
    simplified: str
    jyutping: str
    pinyin: str
    definition: str


@lru_cache(maxsize=1)
def canto_translate_table() -> boto3.resource:
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(TABLE_NAME)


def get_definition(traditional: str) -> Definition:
    response = canto_translate_table().query(
        KeyConditionExpression=Key('traditional').eq(traditional)
    )

    if not response['Items']:
        logger.debug(f"No definition found for {traditional}")
        return None

    item = response['Items'][0]
    return Definition(
        traditional=item['traditional'],
        simplified=item['simplified'],
        jyutping=item['jyutping'],
        pinyin=item['pinyin'],
        definition=item['definition']
    )


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

    try:
        definition = get_definition(
            event['queryStringParameters']['traditional'])
        if not definition:
            return _create_response(body=json.dumps({}))

        return _create_response(body=json.dumps(definition.__dict__))
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.debug(error_code)
        if error_code == 'ResourceNotFoundException':
            return _create_response(body=json.dumps({'message': 'Cannot find resource'}), code=404)
        if error_code == 'InternalServerError':
            return _create_response(body=json.dumps({'message': 'Cannot connect to database'}), code=503)
        if error_code == 'RequestLimitExceeded':
            return _create_response(body=json.dumps({'message': 'Request throttled'}), code=429)

    return _create_response(body=json.dumps({'message': 'Unknown error'}), code=500)
