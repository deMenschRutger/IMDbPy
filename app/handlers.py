from dataclasses import dataclass
from operator import itemgetter

from openpyxl import Workbook
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


class SheetHandler(Handler):
    def handle(self):
        wb = Workbook()
        both_sheet = wb.active
        both_sheet.title = "Both rated"
        from_sheet = wb.create_sheet(f"{self.from_name} only")
        to_sheet = wb.create_sheet(f"{self.to_name} only")

        both_sheet.append(["ID", "Title", self.from_name, self.to_name, "Difference"])
        both = sorted(self.both.values(), key=itemgetter("difference"), reverse=True)
        for movie in both:
            row = [
                movie["id"],
                movie["title"],
                movie["from_rating"],
                movie["to_rating"],
                movie["difference"],
            ]
            both_sheet.append(row)

        from_sheet.append(["ID", "Title", "Rating"])
        for movie in self.only_from:
            row = [movie.id, movie.title, movie.rating]
            from_sheet.append(row)

        to_sheet.append(["ID", "Title", "Rating"])
        for movie in self.only_to:
            row = [movie.id, movie.title, movie.rating]
            to_sheet.append(row)

        wb.save("var/sheet.xlsx")
