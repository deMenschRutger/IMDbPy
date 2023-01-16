import pytest

from app.services.redis import redis, retrieve_ratings, store_ratings

USER_ID = "ur0000001"
REDIS_KEY = f"user:{USER_ID}:ratings"


def test_store_ratings(all_movies):
    store_ratings(USER_ID, all_movies)

    assert redis.scard(REDIS_KEY) == 4


def test_retrieve_missing_ratings():
    with pytest.raises(KeyError):
        retrieve_ratings("ur1234567")


def test_retrieve_ratings(movie_one, all_movies):
    store_ratings(USER_ID, all_movies)

    ratings = retrieve_ratings(USER_ID)

    assert ratings == all_movies

    movie_one_rating = next(r for r in ratings if r.id == movie_one.id)
    assert movie_one_rating.title == movie_one.title
    assert movie_one_rating.year == movie_one.year
    assert movie_one_rating.runtime == movie_one.runtime
    assert movie_one_rating.genre == movie_one.genre
    assert movie_one_rating.rating == movie_one.rating
    assert movie_one_rating.date_rated == movie_one.date_rated
