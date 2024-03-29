import logging
import re
from dataclasses import dataclass
from datetime import date, datetime
from math import ceil
from operator import attrgetter
from typing import Callable, Iterable, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


@dataclass
class Movie:
    id: str
    title: str
    year: int
    runtime: str
    genre: str
    rating: int
    date_rated: date
    compare_rating: Optional[int] = None
    compare_date_rated: Optional[date] = None
    rating_difference: Optional[int] = None

    def __eq__(self, other) -> bool:
        if not isinstance(other, Movie):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# TODO Add option to specify the language.
def _retrieve_single_ratings_page(url: str) -> tuple[list[Movie], int, Optional[str]]:
    response = requests.get(
        f"https://www.imdb.com{url}", headers={"accept-language": "en-US,en"}
    )
    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", id="ratings-container")
    assert isinstance(container, Tag)
    total_pages = 1

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

        year = node.find("span", attrs={"class": "lister-item-year"})
        if year:
            years = re.search(r"[0-9]{4}", year.string)
            if years:
                year = int(years.group(0))

        runtime = node.find("span", attrs={"class": "runtime"})
        if runtime:
            runtime = runtime.string

        genre = node.find("span", attrs={"class": "genre"})
        if genre:
            genre = genre.string.strip()

        rating = node.find("div", attrs={"class": "ipl-rating-star--other-user"}).find(
            "span", attrs={"class": "ipl-rating-star__rating"}
        )
        if rating:
            rating = int(rating.string)

        def find_date_rated_tag(tag: Tag) -> bool:
            if not tag.name == "p":
                return False
            if not tag.has_attr("class") or "text-muted" not in tag.attrs["class"]:
                return False
            if not tag.string:
                return False
            return tag.string.startswith("Rated on")

        date_rated = node.find(find_date_rated_tag)
        if date_rated:
            date_rated = datetime.strptime(
                date_rated.string.strip(), "Rated on %d %b %Y"
            ).date()

        movies.append(Movie(id, title, year, runtime, genre, rating, date_rated))

    # Retrieve pagination information.
    footer = container.find("div", attrs={"class": "footer filmosearch"})
    if not footer:
        return movies, total_pages, None

    # Determine the number of pages.
    pagination_range_el = container.find("span", attrs={"class": "pagination-range"})
    if pagination_range_el:
        movie_count = pagination_range_el.text.strip().split()[-1]
        # IMDb returns the movie count using . as a separator, but sometimes a , can be
        # retrieved as well. The reason for this is unknown.
        total_pages = ceil(int(movie_count.replace(".", "").replace(",", "")) / 100)

    # Find the next page, if available.
    next_page_el = container.find("a", attrs={"class": "next-page"})
    if not next_page_el:
        return movies, total_pages, None
    assert isinstance(next_page_el, Tag)

    href = next_page_el.get("href")
    if not href or href == "#":
        return movies, total_pages, None

    return movies, total_pages, cast(str, next_page_el["href"])


def retrieve_ratings(
    user_id: str,
    limit: Optional[int] = None,
    on_first_page: Optional[Callable[[int], None]] = None,
    on_next_page: Optional[Callable[[int], None]] = None,
) -> set[Movie]:
    next_page_url = cast(Optional[str], f"/user/{user_id}/ratings")
    movies = []
    page_count = 1
    while next_page_url:
        logger.debug(f"Retrieving ratings from page {page_count}.")
        page_movies, total_pages, next_page_url = _retrieve_single_ratings_page(
            next_page_url
        )
        if page_count == 1 and on_first_page:
            on_first_page(total_pages)
        if page_count > 1 and on_next_page:
            on_next_page(page_count)
        movies.extend(page_movies)
        page_count += 1
        if limit and len(movies) >= limit:
            return set(movies[0:limit])
    return set(movies)


def compare_ratings(
    from_movies: set[Movie], to_movies: set[Movie]
) -> tuple[dict[str, Movie], list[Movie], list[Movie]]:
    from_by_id = {m.id: m for m in from_movies}
    to_by_id = {m.id: m for m in to_movies}
    both: dict[str, Movie] = dict()
    for movie in from_movies.intersection(to_movies):
        # We retrieve the movie from the 'from' list again to make sure we have the
        # 'from' rating as the value of the Movie.rating attribute.
        movie = from_by_id[movie.id]
        movie.compare_rating = to_by_id[movie.id].rating
        movie.compare_date_rated = to_by_id[movie.id].date_rated
        # It doesn't matter who had the higher rating, we're just interested in the
        # difference between the two.
        difference = movie.rating - movie.compare_rating
        if difference < 0:
            difference = 0 - difference
        movie.rating_difference = difference
        both[movie.id] = movie

    def sort_ratings(movies: Iterable[Movie]) -> list[Movie]:
        return sorted(movies, key=attrgetter("rating", "date_rated"), reverse=True)

    only_from = sort_ratings(from_movies.difference(to_movies))
    only_to = sort_ratings(to_movies.difference(from_movies))

    return both, only_from, only_to
