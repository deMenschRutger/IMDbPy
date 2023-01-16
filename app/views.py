from operator import attrgetter

from app import app
from app.services.redis import MovieSchema, retrieve_ratings


# TODO Add pagination options.
# TODO Validation of query parameters.
# TODO Improve the way exceptions are rendered.
@app.route("/api/ratings/<user_id>")
def hello_world(user_id: str):
    movies = sorted(
        retrieve_ratings(user_id),
        key=attrgetter("rating", "date_rated"),
        reverse=True,
    )
    return [MovieSchema().dump(m) for m in movies]
