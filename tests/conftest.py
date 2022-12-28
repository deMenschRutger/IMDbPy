from copy import deepcopy
from unittest.mock import MagicMock, patch

import pytest

from app import app
from app.services.imdb import Movie
from app.services.redis import redis


def pytest_sessionstart():
    if not app.config["ENV"] == "testing":
        pytest.exit(
            "Please set the env variable 'ENV' to 'testing' when running the tests."
        )
    if redis.dbsize() > 0:
        pytest.exit(
            "An empty Redis database is required to run the tests, "
            f"but database {app.config['REDIS_DB']} is not empty."
        )


@pytest.fixture(scope="session")
def movie_one():
    return Movie(id="tt6710474", title="Everything Everywhere All at Once", rating=8)


@pytest.fixture(scope="session")
def movie_two():
    return Movie(id="tt0110322", title="Legends of the Fall", rating=7)


@pytest.fixture(scope="session")
def movie_three():
    return Movie(id="tt11003218", title="Pig", rating=8)


@pytest.fixture(scope="session")
def movie_four():
    return Movie(id="tt0185183", title="Battlefield Earth", rating=2)


@pytest.fixture(scope="session")
def all_movies(movie_one, movie_two, movie_three, movie_four):
    return {
        movie_one,
        movie_two,
        movie_three,
        movie_four,
    }


@pytest.fixture
def movie_with_rating():
    def copy_movie(movie, rating):
        movie = deepcopy(movie)
        movie.rating = rating
        return movie

    return copy_movie


@pytest.fixture(scope="session")
def comparison_result(movie_one, movie_two, movie_three, movie_four):
    both = {
        movie_two.id: {
            "id": movie_two.id,
            "title": movie_two.title,
            "from_rating": 8,
            "to_rating": 7,
            "difference": 1,
        },
        movie_four.id: {
            "id": movie_four.id,
            "title": movie_four.title,
            "from_rating": 3,
            "to_rating": 5,
            "difference": 2,
        },
    }
    only_from = [movie_one]
    only_to = [movie_three]
    return both, only_from, only_to


@pytest.fixture(scope="session")
def ratings_without_footer():
    with open("tests/fixtures/ratings_without_footer.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture(scope="session")
def ratings_without_next_page():
    with open("tests/fixtures/ratings_without_next_page.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture(scope="session")
def ratings_page_one():
    with open("tests/fixtures/ratings_page_one.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture(scope="session")
def ratings_page_two():
    with open("tests/fixtures/ratings_page_two.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture
def ratings_request_without_footer(ratings_without_footer):
    with patch("app.services.imdb.requests") as requests:
        requests.get.side_effect = [ratings_without_footer]
        yield requests


@pytest.fixture
def ratings_request_without_next_page(ratings_without_next_page):
    with patch("app.services.imdb.requests") as requests:
        requests.get.side_effect = [ratings_without_next_page]
        yield requests


@pytest.fixture
def ratings_request_multiple_pages(ratings_page_one, ratings_page_two):
    with patch("app.services.imdb.requests") as requests:
        requests.get.side_effect = [ratings_page_one, ratings_page_two]
        yield requests
