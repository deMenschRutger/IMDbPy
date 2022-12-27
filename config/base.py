from os import environ

TESTING = False

REDIS_HOST = environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
REDIS_DB = environ.get("REDIS_DB", 0)
