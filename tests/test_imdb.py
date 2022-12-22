from app import imdb


# TODO Add coverage.
def test_retrieve_ratings_from_multiple_pages(ratings_request):
    result = imdb.retrieve_ratings("ur0000001")

    assert len(result) == 4
    assert result == [
        imdb.Movie(id="tt6710474", title="Everything Everywhere All at Once", rating=8),
        imdb.Movie(id="tt0110322", title="Legends of the Fall", rating=7),
        imdb.Movie(id="tt11003218", title="Pig", rating=8),
        imdb.Movie(id="tt0185183", title="Battlefield Earth", rating=2),
    ]
