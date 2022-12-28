from pathlib import Path
from typing import Optional

import click
from flask.cli import AppGroup
from rich.progress import Progress
from rich.prompt import Confirm

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

    with Progress(transient=True) as progress:
        task = progress.add_task("Retrieving ratings...", start=False)

        def on_first_page(total_pages: int) -> None:
            progress.update(task, total=total_pages)
            progress.start_task(task)
            progress.advance(task, advance=1)

        def on_next_page(_page_number: int) -> None:
            progress.advance(task, advance=1)

        movies = imdb.retrieve_ratings(
            user_id, on_first_page=on_first_page, on_next_page=on_next_page
        )

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
    path = Path("var/sheet.xlsx")
    if path.exists() and not Confirm.ask(
        f"A file already exists at '{path}'. Do you want to overwrite it?"
    ):
        return

    from_movies = redis.retrieve_ratings(from_id)
    to_movies = redis.retrieve_ratings(to_id)
    both_movies, only_from, only_to = imdb.compare_ratings(from_movies, to_movies)

    from_name = from_name or from_id
    to_name = to_name or to_id

    handler_name = getattr(handlers, f"{output_type.capitalize()}Handler")
    handler = handler_name(
        from_name,
        to_name,
        from_movies,
        to_movies,
        both_movies,
        only_from,
        only_to,
        path,
    )
    handler.handle()


app.cli.add_command(lists_cli)
