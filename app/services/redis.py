from typing import cast

from marshmallow import Schema, fields, post_load
from redis import Redis

from app import app
from app.services.imdb import Movie


class MovieSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    year = fields.Int()
    runtime = fields.Str()
    genre = fields.Str()
    rating = fields.Int()
    date_rated = fields.Date()

    @post_load
    def make_movie(self, data, **_kwargs):
        return Movie(**data)


redis = Redis(
    host=app.config["REDIS_HOST"],
    port=app.config["REDIS_PORT"],
    db=app.config["REDIS_DB"],
)


def store_ratings(user_id: str, movies: set[Movie]) -> None:
    key = f"user:{user_id}:ratings"
    redis.delete(key)
    for movie in movies:
        movie = MovieSchema().dumps(movie)
        redis.sadd(key, cast(str, movie))


def retrieve_ratings(user_id: str) -> set[Movie]:
    movies = redis.smembers(f"user:{user_id}:ratings")
    movies = {MovieSchema().loads(cast(str, m)) for m in movies}
    return cast(set[Movie], movies)
