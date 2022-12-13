from unittest.mock import MagicMock

from app import imdb


# TODO Add coverage.
def test_retrieve_ratings():
    with open("tests/fixtures/ratings.html") as f:
        mock = MagicMock()
        mock.return_value.text = f.read()
    imdb.requests.get = mock

    result = imdb.retrieve_ratings("ur0000001")

    assert len(result) == 2
    assert result == [
        imdb.Movie(id="tt6710474", title="Everything Everywhere All at Once", rating=8),
        imdb.Movie(id="tt0110322", title="Legends of the Fall", rating=7),
    ]
