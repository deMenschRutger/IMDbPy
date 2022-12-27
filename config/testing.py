from os import environ

ENV = "testing"
TESTING = True

REDIS_HOST = environ.get("TESTING_REDIS_HOST", "127.0.0.1")
REDIS_PORT = environ.get("TESTING_REDIS_PORT", 6379)
REDIS_DB = environ.get("TESTING_REDIS_DB", 15)
