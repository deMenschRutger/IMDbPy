from marshmallow import Schema, fields, post_load

from app.services.imdb import Movie


class MovieSchema(Schema):
    id = fields.Str()
    title = fields.Str()
    rating = fields.Int()

    @post_load
    def make_movie(self, data, **_kwargs):
        return Movie(**data)
