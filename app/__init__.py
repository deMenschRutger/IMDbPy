import logging
import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()
env = os.environ.get("ENV", "production")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config.from_object("config.base")
app.config.from_object(f"config.{env}")

from . import commands, views  # noqa: E402, F401
