from dataclasses import dataclass
from operator import attrgetter
from pathlib import Path
from typing import Union

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rich.console import Console
from rich.table import Table

from app.services.imdb import Movie


@dataclass
class Handler:
    from_name: str
    to_name: str
    from_movies: set[Movie]
    to_movies: set[Movie]
    both: dict[str, dict]
    only_from: list[Movie]
    only_to: list[Movie]

    @property
    def from_count(self) -> int:
        return len(self.from_movies)

    @property
    def to_count(self) -> int:
        return len(self.to_movies)

    @property
    def both_count(self) -> int:
        return len(self.both)

    @property
    def only_from_count(self) -> int:
        return len(self.only_from)

    @property
    def only_to_count(self) -> int:
        return len(self.only_to)

    def handle(self) -> None:
        raise NotImplementedError


class CliHandler(Handler):
    def handle(self):
        table = Table()
        table.add_column("Statistic", style="cyan")
        table.add_column(self.from_name, style="green")
        table.add_column(self.to_name, style="green")

        table.add_row("Number of ratings", str(self.from_count), str(self.to_count))
        table.add_row("Both rated", str(self.both_count), str(self.both_count))
        table.add_row("Only rated", str(self.only_from_count), str(self.only_to_count))

        console = Console()
        console.print(table)


@dataclass
class SheetHandler(Handler):
    path: Union[Path, str]

    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)

    def handle(self):
        wb = Workbook()
        both_sheet = wb.active
        both_sheet.title = "Both rated"
        from_sheet = wb.create_sheet(f"{self.from_name} only")
        to_sheet = wb.create_sheet(f"{self.to_name} only")

        both_sheet.append(["ID", "Title", self.from_name, self.to_name, "Difference"])
        both = sorted(
            self.both.values(), key=attrgetter("rating_difference"), reverse=True
        )
        for movie in both:
            both_sheet.append(
                [
                    movie.id,
                    movie.title,
                    movie.rating,
                    movie.compare_rating,
                    movie.rating_difference,
                ]
            )

        def add_only(movies: list[Movie], sheet: Worksheet):
            sheet.append(["ID", "Title", "Rating"])
            for movie in movies:
                sheet.append([movie.id, movie.title, movie.rating])

        add_only(self.only_from, from_sheet)
        add_only(self.only_to, to_sheet)

        wb.save(self.path)
