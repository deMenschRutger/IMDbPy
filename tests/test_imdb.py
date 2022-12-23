from app.imdb import Movie, retrieve_ratings


def test_movies_are_equal():
    movie_one = (Movie(id="tt000001", title="A certain title", rating=8),)
    movie_two = (
        Movie(id="tt000001", title="A title in a different language", rating=6),
    )

    assert movie_one == movie_two


def test_movies_are_not_equal():
    movie_one = (Movie(id="tt000001", title="A certain title", rating=8),)
    movie_two = (Movie(id="tt000002", title="A certain title", rating=8),)

    assert not movie_one == movie_two


def test_movie_is_not_other_type(movie_one):
    assert not movie_one == "a different type"


def test_movies_are_combined_in_set(movie_one):
    movies = {movie_one, movie_one}

    assert len(movies) == 1


def test_retrieve_ratings_from_single_page(ratings_request_without_footer, movie_one):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 1
    assert result == [movie_one]


def test_retrieve_ratings_without_next_page(
    ratings_request_without_next_page, movie_one
):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 1
    assert result == [movie_one]


def test_retrieve_ratings_from_multiple_pages(
    ratings_request_multiple_pages, all_movies
):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 4
    assert result == all_movies
