import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_requests_get_factory():
    patcher = patch("src.get_pronunciation.requests.get")
    mock_requests_get = patcher.start()

    def _factory(content: bytes) -> Mock:
        mock_response = Mock()
        mock_response.content = content
        mock_requests_get.return_value = mock_response
        return mock_requests_get

    yield _factory
    patcher.stop()