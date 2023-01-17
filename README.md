# IMDbPy

IMDbPy is a tool that allows you to compare the movie ratings of two IMDb users. There are many IMDb libraries out there, but most are focused on retrieving information about movies, whereas this tool only compares ratings lists (and in the future hopefully other types of IMDb lists like watchlists as well).

This tool was created for a number of reasons. First, to find new potentially interesting movies to watch. IMDb has some features for this, but they aren't always complete or accessible, especially when comparing large lists. The tool also provides me with boilerplate code for various common coding solutions in Python that can be reused for future projects, since even a small application like this already contains many common coding challenges. Finally, the code base is meant to give an impression of the way I code.

Since the official IMDb API is hidden behind a paywall, this tool retrieves information about ratings by scraping the IMDb website. Unfortunately this means that if IMDb changes the structure of their HTML, the tool will stop working until it is updated to use the new structure. Therefore the correct working of this tool is not guaranteed. It is meant for personal use only and should not be used in a production environment.

## Usage

IMDbPy uses [Poetry](https://python-poetry.org/) for dependency management. Dependencies can be installed in your virtual environment using a simple `poetry install`. It also requires a Redis database, which can be configured in a dotenv file.

Currently IMDbPy exposes two CLI commands: one to synchronize ratings data for a user to Redis, and another to compare the ratings data in Redis for two users. To synchronize ratings, you can use the `lists sync` command like this:

    flask lists sync ur0000001

The last argument is the ID of the user on IMDb, including the 'ur' prefix that IMDb adds to users. Synchronizing the ratings of a user this way can take a bit of time, especially for lists containing a thousand ratings or more. Afterwards the user ratings will be stored in a set in Redis.

Once you have synchronized the ratings for multiple users, you can compare them using the `lists compare` command like this:

    flask lists compare ur0000001 0000002 --from-name John --to-name Peter --output-type sheet

This will create a XLSX sheet at `var/sheet.xlsx` (or a location of your choice). It will contain three tabs: two tabs for movies that one user has rated but the other has not, and one that compares the ratings for movies that both users have rated.

If you do not provide the `--output-type` it will default to the `cli` type, which only prints some statistics about the users' ratings to the terminal.

## Development

IMDbPy uses a number of useful tools to improve and maintain the quality of the code. This includes a test suite (using [pytest](https://docs.pytest.org/en/7.2.x/)) and various linters. For the sake of convenience an overview of the available tools and how to use them can be found in the `Makefile` in the root directory.