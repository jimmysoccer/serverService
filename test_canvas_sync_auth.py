import errno
from unittest.mock import Mock, patch

from app.routers.canvas_sync.canvas_route import _save_credentials


def test_read_only_token_cache_does_not_fail_sync():
    credentials = Mock()
    credentials.to_json.return_value = '{"refresh_token":"test"}'

    with patch(
        "app.routers.canvas_sync.canvas_route.TOKEN_PATH.write_text",
        side_effect=OSError(errno.EROFS, "Read-only file system"),
    ):
        _save_credentials(credentials)


def test_unexpected_token_write_error_is_not_hidden():
    credentials = Mock()
    credentials.to_json.return_value = '{}'

    with patch(
        "app.routers.canvas_sync.canvas_route.TOKEN_PATH.write_text",
        side_effect=OSError(errno.ENOSPC, "No space left on device"),
    ):
        try:
            _save_credentials(credentials)
        except OSError as exc:
            assert exc.errno == errno.ENOSPC
        else:
            raise AssertionError("Unexpected filesystem errors must propagate")
