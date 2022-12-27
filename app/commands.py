from typing import Optional

import click
from flask.cli import AppGroup

from app import handlers
from app.services import imdb, redis

from . import app

OUTPUT_TYPE_CLI = "cli"
OUTPUT_TYPE_SHEET = "sheet"

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
@click.option(
    "-o",
    "--output-type",
    type=click.Choice([OUTPUT_TYPE_CLI, OUTPUT_TYPE_SHEET], case_sensitive=False),
    default=OUTPUT_TYPE_CLI,
)
@click.option("--from-name")
@click.option("--to-name")
def compare(
    from_id: str,
    to_id: str,
    output_type: str,
    from_name: Optional[str],
    to_name: Optional[str],
):
    from_movies = redis.retrieve_ratings(from_id)
    to_movies = redis.retrieve_ratings(to_id)
    both_movies, only_from, only_to = imdb.compare_ratings(from_movies, to_movies)

    from_name = from_name or from_id
    to_name = to_name or to_id

    handler_name = getattr(handlers, f"{output_type.capitalize()}Handler")
    handler = handler_name(
        from_name, to_name, from_movies, to_movies, both_movies, only_from, only_to
    )
    handler.handle()


app.cli.add_command(lists_cli)
