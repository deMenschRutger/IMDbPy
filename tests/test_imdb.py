import pytest

from app.services.imdb import Movie, compare_ratings, retrieve_ratings


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


@pytest.mark.parametrize("limit", [1, 2, 3, 4])
def test_retrieve_ratings_with_limit(limit, ratings_request_multiple_pages, all_movies):
    result = retrieve_ratings("ur0000001", limit)

    assert len(result) == limit


def test_compare_movie_lists(movie_one, movie_two, movie_three, movie_four):
    from_list = {movie_one, movie_two, movie_four}
    to_list = {movie_three, movie_four}

    both, from_only, to_only = compare_ratings(from_list, to_list)

    assert both == [movie_four]
    assert from_only == [movie_one, movie_two]
    assert to_only == [movie_three]
