import json

import click
from flask.cli import AppGroup

from app.services.imdb import retrieve_ratings
from app.services.redis import redis

from . import app

lists_cli = AppGroup("lists")


@lists_cli.command("sync")
@click.argument("user-id")
def sync(user_id: str):
    redis.ping()
    movies = set(retrieve_ratings(user_id))
    key = f"user:{user_id}:ratings"
    redis.delete(key)
    for movie in movies:
        redis.sadd(key, json.dumps(movie.__dict__))
    print(f"Synchronized {len(movies)} movies.")


app.cli.add_command(lists_cli)
