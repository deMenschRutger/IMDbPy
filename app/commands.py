from typing import cast

import click
from flask.cli import AppGroup

from app.schemas import MovieSchema
from app.services.imdb import Movie, compare_ratings, retrieve_ratings
from app.services.redis import redis

from . import app

lists_cli = AppGroup("lists")


@lists_cli.command("sync")
@click.argument("user-id")
def sync(user_id: str):
    redis.ping()
    movies = set(retrieve_ratings(user_id))
    key = f"user:{user_id}:ratings"
    redis.delete(key)
    for movie in movies:
        movie = MovieSchema().dumps(movie)
        redis.sadd(key, cast(str, movie))
    print(f"Synchronized {len(movies)} movies.")


@lists_cli.command("compare")
@click.argument("from-id")
@click.argument("to-id")
def compare(from_id: str, to_id: str):
    def retrieve_ratings_for_user(user_id: str) -> set[Movie]:
        movies = redis.smembers(f"user:{user_id}:ratings")
        movies = {MovieSchema().loads(cast(str, m)) for m in movies}
        return cast(set[Movie], movies)

    from_movies = retrieve_ratings_for_user(from_id)
    to_movies = retrieve_ratings_for_user(to_id)
    both, only_from, only_to = compare_ratings(from_movies, to_movies)

    print(f"User '{from_id}' has rated {len(from_movies)} movies.")
    print(f"User '{to_id}' has rated {len(to_movies)} movies.")
    print(f"There are {len(both)} movies that both users have rated.")
    print(
        f"User '{from_id}' has rated {len(only_from)} movies that user '{to_id}' has not rated."  # noqa: E501
    )
    print(
        f"User '{to_id}' has rated {len(only_to)} movies that user '{from_id}' has not rated."  # noqa: E501
    )


app.cli.add_command(lists_cli)
