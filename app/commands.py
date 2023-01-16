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

lists_cli = AppGroup("lists", help="Synchronize and compare rating lists.")


@lists_cli.command("sync")
@click.argument("user-id")
def sync(user_id: str):
    """
    The sync command retrieves all ratings for a specific IMDb user by scraping the
    IMDb website, then stores the ratings in a Redis database. Scraping IMDb takes a
    long time, so we don't want to have to visit it every time we use a command that
    needs user ratings. Subsequent commands, such as the compare command, do not work
    unless the ratings for the provided users have been synchronized first.

    USER_ID The ID of the user on IMDb, including the 'ur' prefix
    """
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
    click.echo(f"Synchronized {len(movies)} movies.")


@lists_cli.command("compare")
@click.argument("from-id")
@click.argument("to-id")
@click.option(
    "-o",
    "--output-type",
    type=click.Choice([OUTPUT_TYPE_CLI, OUTPUT_TYPE_SHEET], case_sensitive=False),
    default=OUTPUT_TYPE_CLI,
    help="How to output the results of the comparison.",
)
@click.option(
    "--from-name", help="The name of the first user. Defaults to the user's IMDb ID."
)
@click.option(
    "--to-name", help="The name of the second user. Defaults to the user's IMDb ID."
)
@click.option(
    "-p",
    "--path",
    default="var/sheet.xlsx",
    help="Path to write the sheet to if the output type is 'sheet'. Defaults to "
    "'var/sheet.xlsx'.",
)
def compare(
    from_id: str,
    to_id: str,
    output_type: str,
    from_name: Optional[str],
    to_name: Optional[str],
    path: Path,
):
    """
    This command takes the ratings of two IMDb users and compares them. The results can
    be shown in the terminal or written to a sheet. On the terminal only some basic
    statistics will be shown. However, the sheet will include three separate tabs,
    two for movies that only one of the users has rated and one for the movies both
    users have rated. The latter also includes information about the difference in
    rating between the two users per movie.

    \b
    FROM_ID The IMDb ID of the first user to compare
    TO_ID The IMDb ID of the second user to compare
    \f
    """
    path = Path(path)
    if path.exists() and not Confirm.ask(
        f"A file already exists at '{path}'. Do you want to overwrite it?"
    ):
        click.echo("Aborted!")
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

    click.echo(f"The sheet was successfully created at {path}.")


app.cli.add_command(lists_cli)
