import pytest

from app.services.redis import redis, retrieve_ratings, store_ratings

USER_ID = "ur0000001"
REDIS_KEY = f"user:{USER_ID}:ratings"


@pytest.fixture(autouse=True)
def auto_use_redis(configure_redis):
    yield


def test_store_ratings(all_movies):
    store_ratings(USER_ID, all_movies)

    assert redis.scard(REDIS_KEY) == 4


def test_retrieve_ratings(movie_one, movie_two, movie_three, movie_four, all_movies):
    store_ratings(USER_ID, all_movies)

    ratings = retrieve_ratings(USER_ID)

    assert ratings == all_movies
