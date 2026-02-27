import base64

from src.get_pronunciation import handler


def test_handler_returns_audio_response(mock_requests_get_factory):
    mock_requests_get = mock_requests_get_factory(content=b"fake-audio")
    response = handler({"queryStringParameters": {"traditional": "你好"}}, {})

    mock_requests_get.assert_called_once_with(
        "https://translate.google.com.vn/translate_tts?ie=UTF-8&q=你好&tl=yue&client=tw-ob"
    )
    assert response == {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": {
            "content-type": "audio/mpeg",
            "Access-Control-Allow-Origin": "*",
        },
        "body": base64.b64encode(b"fake-audio").decode("utf-8"),
    }
