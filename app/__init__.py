from pprint import pprint

import click
from flask import Flask
from flask.cli import AppGroup

from app.imdb import retrieve_ratings

app = Flask(__name__)
compare_cli = AppGroup("compare")


@compare_cli.command("lists")
@click.argument("user-id")
def compare_lists(user_id: str):
    movies = retrieve_ratings(user_id)
    pprint(movies)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


app.cli.add_command(compare_cli)
