import re
from dataclasses import dataclass
from typing import Optional, cast

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Movie:
    id: str
    title: str
    rating: int

    def __eq__(self, other) -> bool:
        if not isinstance(other, Movie):
            return False
        return self.id == other.id


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


def retrieve_ratings(user_id: str) -> list[Movie]:
    next_page_url = cast(Optional[str], f"/user/{user_id}/ratings")
    movies = []
    while next_page_url:
        page_movies, next_page_url = _retrieve_single_ratings_page(next_page_url)
        movies.extend(page_movies)
    return movies
