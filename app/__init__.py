import logging

from flask import Flask

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

from . import commands, views  # noqa: E402, F401
