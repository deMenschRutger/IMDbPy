from unittest.mock import Mock, call

import pytest

from app.services.imdb import Movie, compare_ratings, retrieve_ratings


def test_movies_are_equal():
    movie_one = (
        Movie(
            id="tt000001",
            title="A certain title",
            year=2020,
            runtime="1 hr 30 min",
            genre="Action",
            rating=8,
            date_rated="",
        ),
    )
    movie_two = (
        Movie(
            id="tt000001",
            title="A title in a different language",
            year=2021,
            runtime="1 hr 40 min",
            genre="Comedy",
            rating=6,
            date_rated="",
        ),
    )

    assert movie_one == movie_two


def test_movies_are_not_equal():
    movie_one = (
        Movie(
            id="tt000001",
            title="A certain title",
            year=2020,
            runtime="1 hr 30 min",
            genre="Action",
            rating=8,
            date_rated="",
        ),
    )
    movie_two = (
        Movie(
            id="tt000002",
            title="A certain title",
            year=2020,
            runtime="1 hr 30 min",
            genre="Action",
            rating=8,
            date_rated="",
        ),
    )

    assert not movie_one == movie_two


def test_movie_is_not_other_type(movie_one):
    assert not movie_one == "a different type"


def test_movies_are_combined_in_set(movie_one):
    movies = {movie_one, movie_one}

    assert len(movies) == 1


def test_retrieve_ratings_from_single_page(ratings_request_without_footer, movie_one):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 1
    assert result == {movie_one}

    result = result.pop()
    assert result.title == movie_one.title
    assert result.year == movie_one.year
    assert result.runtime == movie_one.runtime
    assert result.genre == movie_one.genre
    assert result.rating == movie_one.rating
    assert result.date_rated == movie_one.date_rated


def test_retrieve_ratings_without_next_page(
    ratings_request_without_next_page, movie_one
):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 1
    assert result == {movie_one}


def test_retrieve_ratings_from_multiple_pages(
    ratings_request_multiple_pages, all_movies
):
    result = retrieve_ratings("ur0000001")

    assert len(result) == 4
    assert result == all_movies


def test_retrieve_ratings_with_pagination(ratings_request_multiple_pages):
    on_first = Mock()
    on_next = Mock()

    retrieve_ratings("ur0000001", on_first_page=on_first, on_next_page=on_next)

    assert on_first.call_count == 1
    assert on_first.call_args == call(2)
    assert on_next.call_count == 1
    assert on_next.call_args == call(2)


@pytest.mark.parametrize("limit", [1, 2, 3, 4])
def test_retrieve_ratings_with_limit(limit, ratings_request_multiple_pages):
    result = retrieve_ratings("ur0000001", limit)

    assert len(result) == limit


def test_compare_different_movie_lists(
    movie_one, movie_two, movie_three, movie_four, movie_with_rating, comparison_result
):
    movie_two_from = movie_with_rating(movie_two, 8)
    movie_two_to = movie_with_rating(movie_two, 7)
    movie_four_from = movie_with_rating(movie_four, 3)
    movie_four_to = movie_with_rating(movie_four, 5)

    from_list = {movie_one, movie_two_from, movie_four_from}
    to_list = {movie_two_to, movie_three, movie_four_to}

    both, only_from, only_to = compare_ratings(from_list, to_list)

    expected_both, expected_only_from, expected_only_to = comparison_result
    assert both == expected_both
    assert both[movie_two.id].rating == 8
    assert both[movie_two.id].compare_rating == 7
    assert both[movie_two.id].rating_difference == 1
    assert both[movie_four.id].rating == 3
    assert both[movie_four.id].compare_rating == 5
    assert both[movie_four.id].rating_difference == 2
    assert only_from == expected_only_from
    assert only_to == expected_only_to


def test_compare_only_from_movie_lists(
    all_movies, movie_one, movie_two, movie_three, movie_four
):
    from_list = all_movies
    to_list = set()

    both, from_only, to_only = compare_ratings(from_list, to_list)

    assert both == {}
    assert from_only == [movie_one, movie_three, movie_two, movie_four]
    assert to_only == []


def test_compare_only_to_movie_lists(
    all_movies, movie_one, movie_two, movie_three, movie_four
):
    from_list = set()
    to_list = all_movies

    both, from_only, to_only = compare_ratings(from_list, to_list)

    assert both == {}
    assert from_only == []
    assert to_only == [movie_one, movie_three, movie_two, movie_four]
