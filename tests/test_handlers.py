from pathlib import PosixPath

from openpyxl import load_workbook

from app.handlers import SheetHandler

FILENAME = "test.xlsx"


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
        5,
        2,
    )
    assert ws_both[2] == (
        movie_two.id,
        movie_two.title,
        movie_two.year,
        movie_two.genre,
        movie_two.runtime,
        8,
        7,
        1,
    )
    assert ws_only_from[1] == (
        movie_one.id,
        movie_one.title,
        movie_one.year,
        movie_one.genre,
        movie_one.runtime,
        8,
    )
    assert ws_only_to[1] == (
        movie_three.id,
        movie_three.title,
        movie_three.year,
        movie_three.genre,
        movie_three.runtime,
        8,
    )


def test_save_sheet_with_string_path(tmp_path: PosixPath):
    path = tmp_path.joinpath(FILENAME)

    handler = SheetHandler("John", "Peter", set(), set(), dict(), [], [], str(path))
    handler.handle()

    assert path.exists()
