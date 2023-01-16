from datetime import datetime
from pathlib import PosixPath
from unittest.mock import MagicMock, patch

from openpyxl import load_workbook

from app.handlers import CliHandler, SheetHandler

FILENAME = "test.xlsx"


@patch("app.handlers.Console")
def test_cli_handler(console: MagicMock):
    handler = CliHandler("John", "Peter", set(), set(), {}, [], [])
    handler.handle()

    console.return_value.print.assert_called_once()


def test_save_sheet(
    comparison_result,
    movie_one,
    movie_two,
    movie_three,
    movie_four,
    tmp_path: PosixPath,
):
    both, only_from, only_to = comparison_result
    path = tmp_path.joinpath(FILENAME)

    handler = SheetHandler(
        "John", "Peter", set(), set(), both, only_from, only_to, path
    )
    handler.handle()

    assert path.exists()
    wb = load_workbook(path)
    ws_both = tuple(wb["Both rated"].values)
    ws_only_from = tuple(wb["John only"].values)
    ws_only_to = tuple(wb["Peter only"].values)

    assert len(ws_both) == 3
    assert len(ws_only_from) == 2
    assert len(ws_only_to) == 2

    assert ws_both[1] == (
        movie_four.id,
        movie_four.title,
        movie_four.year,
        movie_four.genre,
        movie_four.runtime,
        3,
        # openpyxl internally converts instances of date back to instances of datetime.
        datetime(
            movie_four.date_rated.year,
            movie_four.date_rated.month,
            movie_four.date_rated.day,
        ),
        5,
        datetime(2021, 4, 11),
        2,
    )
    assert ws_both[2] == (
        movie_two.id,
        movie_two.title,
        movie_two.year,
        movie_two.genre,
        movie_two.runtime,
        8,
        datetime(2022, 6, 2),
        7,
        datetime(2022, 6, 5),
        1,
    )
    assert ws_only_from[1] == (
        movie_one.id,
        movie_one.title,
        movie_one.year,
        movie_one.genre,
        movie_one.runtime,
        8,
        datetime(
            movie_one.date_rated.year,
            movie_one.date_rated.month,
            movie_one.date_rated.day,
        ),
    )
    assert ws_only_to[1] == (
        movie_three.id,
        movie_three.title,
        movie_three.year,
        movie_three.genre,
        movie_three.runtime,
        8,
        datetime(
            movie_three.date_rated.year,
            movie_three.date_rated.month,
            movie_three.date_rated.day,
        ),
    )


def test_save_sheet_with_string_path(tmp_path: PosixPath):
    path = tmp_path.joinpath(FILENAME)

    handler = SheetHandler("John", "Peter", set(), set(), dict(), [], [], str(path))
    handler.handle()

    assert path.exists()
