import click
from flask.cli import AppGroup

from app.services import imdb, redis

from . import app

lists_cli = AppGroup("lists")


@lists_cli.command("sync")
@click.argument("user-id")
def sync(user_id: str):
    redis.redis.ping()
    movies = imdb.retrieve_ratings(user_id)
    redis.store_ratings(user_id, movies)
    print(f"Synchronized {len(movies)} movies.")


@lists_cli.command("compare")
@click.argument("from-id")
@click.argument("to-id")
def compare(from_id: str, to_id: str):
    from_movies = redis.retrieve_ratings(from_id)
    to_movies = redis.retrieve_ratings(to_id)
    both, only_from, only_to = imdb.compare_ratings(from_movies, to_movies)

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
