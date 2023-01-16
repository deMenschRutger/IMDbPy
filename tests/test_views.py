from typing import cast

import pytest
from flask.testing import FlaskClient

from app import app
from app.services.redis import store_ratings

USER_ID = "ur0000001"


@pytest.fixture
def client():
    return app.test_client()


def test_view_existing_ratings(client: FlaskClient, all_movies, movie_one):
    store_ratings(USER_ID, all_movies)

    response = cast(list[dict], client.get("/api/ratings/ur0000001").json)

    assert len(response) == 4
    assert response[0]["id"] == movie_one.id
    assert response[0]["title"] == movie_one.title
    assert response[0]["rating"] == movie_one.rating
    assert response[0]["dateRated"] == movie_one.date_rated.isoformat()
