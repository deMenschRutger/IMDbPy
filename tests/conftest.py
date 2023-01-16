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


@pytest.fixture()
def configure_redis():
    yield
    redis.flushdb()


@pytest.fixture(scope="session")
def movie_one():
    return Movie(
        id="tt6710474",
        title="Everything Everywhere All at Once",
        year=2022,
        runtime="2 hr 19 min",
        genre="Action, Adventure, Comedy",
        rating=8,
        date_rated="17 Jun 2022",
    )


@pytest.fixture(scope="session")
def movie_two():
    return Movie(
        id="tt0110322",
        title="Legends of the Fall",
        year=1994,
        runtime="2 hr 13 min",
        genre="Drama, Romance, War",
        rating=7,
        date_rated="02 Jun 2022",
    )


@pytest.fixture(scope="session")
def movie_three():
    return Movie(
        id="tt11003218",
        title="Pig",
        year=2021,
        runtime="1 hr 32 min",
        genre="Drama, Mystery",
        rating=8,
        date_rated="May 16 2022",
    )


@pytest.fixture(scope="session")
def movie_four():
    return Movie(
        id="tt0185183",
        title="Battlefield Earth",
        year=2000,
        runtime="1 hr 58 min",
        genre="Action, Adventure, Sci-Fi",
        rating=2,
        date_rated="04 Apr 2021",
    )


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
def comparison_result(
    movie_one: Movie, movie_two: Movie, movie_three: Movie, movie_four: Movie
):
    movie_two = deepcopy(movie_two)
    movie_two.rating = 8
    movie_two.compare_rating = 7
    movie_two.rating_difference = 1
    movie_four = deepcopy(movie_four)
    movie_four.rating = 3
    movie_four.compare_rating = 5
    movie_four.rating_difference = 2

    both = {
        movie_two.id: movie_two,
        movie_four.id: movie_four,
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
