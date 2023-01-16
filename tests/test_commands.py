import pytest

from app import app
from app.services.redis import redis

USER_ID = "ur0000002"
REDIS_KEY = f"user:{USER_ID}:ratings"


@pytest.fixture()
def runner():
    return app.test_cli_runner()


def test_sync_command(configure_redis, ratings_request_multiple_pages, runner):
    result = runner.invoke(args=["lists", "sync", USER_ID])

    assert result.output.strip() == "Synchronized 4 movies."
    assert redis.scard(REDIS_KEY) == 4
