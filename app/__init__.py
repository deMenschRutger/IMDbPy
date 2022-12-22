import json
import logging
from cmath import log

import click
from flask import Flask
from flask.cli import AppGroup
from redis import Redis

from app.imdb import retrieve_ratings

logging.basicConfig(level=logging.DEBUG)

redis = Redis()
app = Flask(__name__)
lists_cli = AppGroup("lists")


@lists_cli.command("sync")
@click.argument("user-id")
def sync(user_id: str):
    movies = set(retrieve_ratings(user_id))
    key = f"user:{user_id}:ratings"
    redis.delete(key)
    for movie in movies:
        redis.sadd(key, json.dumps(movie.__dict__))
    print(f"Synchronized {len(movies)} movies.")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


app.cli.add_command(lists_cli)
