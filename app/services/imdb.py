import logging
import re
from dataclasses import dataclass
from operator import attrgetter
from typing import Iterable, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


@dataclass
class Movie:
    id: str
    title: str
    rating: int

    def __eq__(self, other) -> bool:
        if not isinstance(other, Movie):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


def _retrieve_single_ratings_page(url: str) -> tuple[list[Movie], Optional[str]]:
    response = requests.get(f"https://www.imdb.com{url}")
    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", id="ratings-container")
    assert isinstance(container, Tag)

    # Find all movies on the page.
    nodes = container.find_all("div", attrs={"class": "lister-item mode-detail"})
    movies = []
    for node in nodes:
        id = node.find("div", attrs={"class": "lister-item-image ribbonize"}).attrs[
            "data-tconst"
        ]
        title = node.find("div", attrs={"class": "lister-item-content"}).h3.a
        if title:
            title = re.sub(r"\s+", " ", title.string)
        rating = node.find("div", attrs={"class": "ipl-rating-star--other-user"}).find(
            "span", attrs={"class": "ipl-rating-star__rating"}
        )
        if rating:
            rating = int(rating.string)
        movies.append(Movie(id, title, rating))

    # Find the next page, if available.
    footer = container.find("div", attrs={"class": "footer filmosearch"})
    if not footer:
        return movies, None

    next_page_el = container.find("a", attrs={"class": "next-page"})
    if not next_page_el:
        return movies, None
    assert isinstance(next_page_el, Tag)

    href = next_page_el.get("href")
    if not href or href == "#":
        return movies, None

    return movies, cast(str, next_page_el["href"])


def retrieve_ratings(user_id: str, limit: Optional[int] = None) -> set[Movie]:
    next_page_url = cast(Optional[str], f"/user/{user_id}/ratings")
    movies = []
    page_count = 1
    while next_page_url:
        logger.debug(f"Retrieving ratings from page {page_count}.")
        page_movies, next_page_url = _retrieve_single_ratings_page(next_page_url)
        movies.extend(page_movies)
        page_count += 1
        if limit and len(movies) >= limit:
            return set(movies[0:limit])
    return set(movies)


def compare_ratings(
    from_movies: set[Movie], to_movies: set[Movie]
) -> tuple[dict[str, dict], list[Movie], list[Movie]]:
    from_by_ratings = {m.id: m.rating for m in from_movies}
    to_by_ratings = {m.id: m.rating for m in to_movies}
    both: dict[str, dict] = dict()

    for movie in from_movies.intersection(to_movies):
        from_rating = from_by_ratings[movie.id]
        to_rating = to_by_ratings[movie.id]
        difference = from_rating - to_rating
        # It doesn't matter who had the higher rating, we're just interested in the
        # difference between the two.
        if difference < 0:
            difference = 0 - difference
        both[movie.id] = {
            "id": movie.id,
            "title": movie.title,
            "from_rating": from_rating,
            "to_rating": to_rating,
            "difference": difference,
        }

    def sort_ratings(movies: Iterable[Movie]) -> list[Movie]:
        movies = sorted(movies, key=attrgetter("title"))
        return sorted(movies, key=attrgetter("rating"), reverse=True)

    only_from = sort_ratings(from_movies.difference(to_movies))
    only_to = sort_ratings(to_movies.difference(from_movies))

    return both, only_from, only_to
