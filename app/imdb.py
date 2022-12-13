import re
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup


@dataclass
class Movie:
    id: str
    title: str
    rating: int


# TODO Retrieve multiple pages.
def retrieve_ratings(user_id: str) -> List[Movie]:
    response = requests.get(f"https://www.imdb.com/user/{user_id}/ratings")
    soup = BeautifulSoup(response.text, "html.parser")
    root = soup.find("div", id="root")
    nodes = root.find_all("div", attrs={"class": "lister-item mode-detail"})
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

    return movies
