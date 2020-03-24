# Webtiles server

This is the Webtiles server and client.

## Contents

* [Prerequisites](#prerequisites)
* [Running the server for testing purposes](#running-the-server-for-testing-purposes)
* [Running a production server](#running-a-production-server)
* [Contributing](#contributing)

## Prerequisites

To run the server, you need:

* Linux or macOS (other platforms are untested)
* Python 2.6 or 2.7 (Python 3 is not supported)
* The dependencies specified in `requirements.txt`

Note: If you are using Python 2.6, you also need the `ordereddict` package.

Note: Tornado 3.x is required, versions 4 and above are known not to work.

You'll need to compile Crawl passing `WEBTILES=y` to make to get a
suitable binary. For publicly accessible servers, you should also use
`USE_DGAMELAUNCH=y`; this disables some things like Wizmode, and enables
the milestone and player location display in the lobby.

## Running the server for testing purposes

1. `cd` to the Crawl source directory
2. Compile Crawl with `WEBTILES=y`
3. Set up a Python virtualenv:

    ```sh
    python3 -m virtualenv -p python3 webserver/venv # Remove the "3"s to use Py2
    . ./webserver/venv/bin/activate
    pip install -r webserver/requirements/dev.py3.txt # dev.py2.txt for Py2
    ```

4. Run the server: `python webserver/server.py`

    (You need to activate the virtualenv every time you start the server)

5. Browse to [localhost:8080](http://localhost:8080/) and you should see the lobby.

When developing, you'll probably want to automatically log in as a
testing user and disable caching of non-game-data files; see the
"autologin" and "no_cache" options in webserver/config.py for this.

## Running a production server

Use the requirements files `requirements/base.{py2,py3}.txt`.

The server can be configured by modifying the file `config.py`. Most of
the options are commented or should be self-evident. You should
probably set uid and gid to a non-privileged user; you will also want
to enable logging to a file by removing the # before the relevant line
in `logging_config`.

You will also need a script that initializes user-specific data, like
copying a default rc file if the user doesn't yet have one --
currently this is not done by the server. You can have the script be
run on every login by setting `init_player_program`. There is an example
script in `util/webtiles-init-player.sh`, but you will probably want to
customize it.

## Contributing

For Python developers, several utilities are available:

* `make format` -- format code
* `make lint` -- run several Python linters (with Flake8)
* `requirements.in/sync.sh` -- update requirements files
