from pathlib import PosixPath
from unittest.mock import patch

import pytest

from app import app
from app.services.redis import redis

USER_ID_ONE = "ur0000001"
USER_ID_TWO = "ur0000002"
REDIS_KEY_ONE = f"user:{USER_ID_ONE}:ratings"


@pytest.fixture()
def runner():
    return app.test_cli_runner()


@pytest.fixture()
def test_sheet_path(tmp_path: PosixPath):
    return tmp_path.joinpath("test.xlsx")


@pytest.fixture()
def existing_file(test_sheet_path: PosixPath):
    with open(test_sheet_path, "a") as f:
        f.write("existing file")
    return test_sheet_path


def test_sync_command(configure_redis, ratings_request_multiple_pages, runner):
    result = runner.invoke(args=["lists", "sync", USER_ID_ONE])

    assert result.output.strip() == "Synchronized 4 movies."
    assert redis.scard(REDIS_KEY_ONE) == 4


def test_compare_command_file_does_not_exist(runner, test_sheet_path: PosixPath):
    result = runner.invoke(
        args=[
            "lists",
            "compare",
            USER_ID_ONE,
            USER_ID_TWO,
            "-o",
            "sheet",
            "-p",
            test_sheet_path,
        ]
    )

    assert (
        result.output.strip()
        == f"The sheet was successfully created at {test_sheet_path}."
    )
    assert test_sheet_path.exists()


@patch("app.commands.Confirm")
def test_compare_command_file_exists(confirm, runner, existing_file: PosixPath):
    confirm.ask.return_value = False

    result = runner.invoke(
        args=[
            "lists",
            "compare",
            USER_ID_ONE,
            USER_ID_TWO,
            "-o",
            "sheet",
            "-p",
            existing_file,
        ]
    )

    assert result.output.strip() == "Aborted!"


@patch("app.commands.Confirm")
def test_compare_command_overwrite(confirm, runner, existing_file: PosixPath):
    confirm.ask.return_value = True

    result = runner.invoke(
        args=[
            "lists",
            "compare",
            USER_ID_ONE,
            USER_ID_TWO,
            "-o",
            "sheet",
            "-p",
            existing_file,
        ]
    )

    assert (
        result.output.strip()
        == f"The sheet was successfully created at {existing_file}."
    )
    assert existing_file.exists()
