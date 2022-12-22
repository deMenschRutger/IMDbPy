from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(scope="session")
def ratings_page_one():
    with open("tests/fixtures/ratings_page_one.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture(scope="session")
def ratings_page_two():
    with open("tests/fixtures/ratings_page_two.html") as f:
        return MagicMock(text=f.read())


@pytest.fixture
def ratings_request(ratings_page_one, ratings_page_two):
    with patch("app.imdb.requests") as requests:
        requests.get.side_effect = [ratings_page_one, ratings_page_two]
        yield requests
