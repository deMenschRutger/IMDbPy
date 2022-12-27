from typing import Optional

import click
from flask.cli import AppGroup
from rich.console import Console
from rich.table import Table

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
@click.option("--from-name")
@click.option("--to-name")
def compare(from_id: str, to_id: str, from_name: Optional[str], to_name: Optional[str]):
    from_movies = redis.retrieve_ratings(from_id)
    to_movies = redis.retrieve_ratings(to_id)
    both, only_from, only_to = imdb.compare_ratings(from_movies, to_movies)

    from_name = from_name or from_id
    to_name = to_name or to_id

    table = Table()
    table.add_column("Statistic", style="cyan")
    table.add_column(from_name, style="green")
    table.add_column(to_name, style="green")

    table.add_row("Number of ratings", str(len(from_movies)), str(len(to_movies)))
    table.add_row("Both rated", str(len(both)), str(len(both)))
    table.add_row("Only rated", str(len(only_from)), str(len(only_to)))

    console = Console()
    console.print(table)


app.cli.add_command(lists_cli)
