# Warning! Servers will not update or merge with the version controlled copy of
# this file, so any parameters here, and code that uses them, need to come
# without the assumption that they will be present in any given config.py on a
# server. Furthermore, on a typical rebuild in a production server, a running
# webtiles server *will not restart*, so you can't even assume that any config-
# specific code that you've added will be consistently present. This
# particularly impacts templated html files, which are loaded and called
# dynamically, so *do* get updated immediately on a rebuild. If something like
# client.html raises an exception, this will trigger 500 errors across the whole
# server.
#
# One useful workaround for all this is to get config paramters with the builtin
# `getattr` function: e.g. `getattr(config, "dgl_mode", False) will safely get
# this variable from the module, defaulting to False if it doesn't exist (and
# not raising an exception). `hasattr` is also safe.

import os
import logging
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # type: ignore

import yaml

dgl_mode = True

bind_nonsecure = True # Set to false to only use SSL
bind_address = ""
bind_port = 8080
# Or listen on multiple address/port pairs (overriding the above) with:
# bind_pairs = (
#     ("127.0.0.1", 8080),
#     ("localhost", 8082),
#     ("", 8180), # All addresses
# )

logging_config = {
    # If a filename is not set, log to stdout
    # "filename": "webtiles.log",
    "level": logging.INFO,
    "format": "%(asctime)s %(levelname)s: %(message)s",
    # Log HTTP access requests. Defaults to enabled.
    "access_logs": False,
}

password_db = "./webserver/passwd.db3"
# Uncomment and change if you want this db somewhere separate from the
# password_db location.
#settings_db = "./webserver/user_settings.db3"

static_path = "./webserver/static"
template_path = "./webserver/templates/"

# Path for server-side unix sockets (to be used to communicate with crawl)
server_socket_path = None # Uses global temp dir

# Server name, so far only used in the ttyrec metadata
server_id = ""

# Disable caching of game data files
game_data_no_cache = True

# Watch socket dirs for games not started by the server
watch_socket_dirs = False

# Game configs
#
# You can define game configs in two ways:
# 1. With a static dictionary `games`
# 2. As extra games to append to this list from the `load_games` function (which
#    by default loads games as defined in `games.d/*.yaml`).
#
# All options in this config are documented in games.d/base.yaml.
games = OrderedDict([
    ("dcss-web-trunk", dict(
        name = "DCSS trunk",
        crawl_binary = "./crawl",
        rcfile_path = "./rcs/",
        macro_path = "./rcs/",
        morgue_path = "./rcs/%n",
        inprogress_path = "./rcs/running",
        ttyrec_path = "./rcs/ttyrecs/%n",
        socket_path = "./rcs",
        client_path = "./webserver/game_data/",
        # dir_path = ".",
        # cwd = ".",
        morgue_url = None,
        # milestone_path = "./rcs/milestones",
        send_json_options = True,
        # env = {"LANG": "en_US.UTF8"},
        )),
])

def load_games():
    """Load game definitions from games.d/*.yaml files.

    This function will be called on startup and every time the webserver is sent
    a USR1 signal (eg `kill -USR1 <pid>`). This allows dynamic modification of
    the games list without interrupting active game sessions.

    The format of the source YAML files is: `games: [<game>, ...]`. Each game is
    a dictionary matching the format of entries in the `games` variable above,
    with an extra key `id` for the game's ID. Directory paths support %n as
    described above.

    This example function will only add or update games. It doesn't support
    removing or reordering games. If you want to add support for either, read
    the caveats below and please contribute the improvement as a pull request!

    Dynamic update caveats:

    1. The main use-case is to support adding new game modes to a running
       server. Other uses (like modifying or removing an existing game mode, or
       re-ordering the games list) may work, but are not well tested.
    2. If you do modify a game entry, the changed settings only affect new game
       sessions (including new spectators). Existing sessions use the old config
       until they close.
    3. Some settings affect spectators. If you modify a running game's config,
       the mismatch of settings between the player and new spectators might
       cause spectating to fail until the player restarts with new settings.
    """
    conf_subdir = "games.d"
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), conf_subdir)
    delta = OrderedDict()
    for file_name in sorted(os.listdir(base_path)):
        path = os.path.join(base_path, file_name)
        if not file_name.endswith('.yaml') and not file_name.endswith('.yml'):
            logging.warn("Skipping loading games data from non-yaml file %s",
                file_name)
            continue
        try:
            with open(path) as f:
                yaml_text = f.read()
        except OSError as e:
            logging.warn("Couldn't read file %s: %s", path, e)
        try:
            data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            logging.warning("Failed to load games from %s, skipping (parse failure: %s).",
                file_name, e)
            continue
        if data is None or 'games' not in data:
            logging.warning("Failed to load games from %s, skipping (no 'games' key).",
                file_name)
            continue
        logging.debug("Loading data from %s", file_name)
        messages = []
        for game in data['games']:
            if not validate_game_dict(game):
                continue
            game_id = game['id']
            if game_id in delta:
                logging.warning("Game %s from %s was specified in an earlier config file, skipping.", game_id, path)
            delta[game_id] = game
            action = "Updated" if game_id in games else "Loaded"
            messages.append(("%s game config %s from %s.", action, game_id, file_name))
    if delta:
        assert len(delta.keys()) == len(messages)
        logging.info("Updating live games config")
        games.update(delta)
        for message in messages:
            logging.info(*message)


def validate_game_dict(game):
    """Validate a game dictionary.

    Log warnings about issues and return validity.
    """
    if 'id' not in game:
        # Log the full game definition to help identify the game
        logging.warn("Missing 'id' from game definition %r", game)
        return False
    found_errors = False
    required = ('id', 'name', 'crawl_binary', 'rcfile_path', 'macro_path',
        'morgue_path', 'inprogress_path', 'ttyrec_path',
        'socket_path', 'client_path')
    optional = ('dir_path', 'cwd', 'morgue_url', 'milestone_path',
        'send_json_options', 'options', 'env')
    boolean = ('send_json_options',)
    string_array = ('options',)
    string_dict = ('env', )
    for prop in required:
        if prop not in game:
            found_errors = True
            logging.warn("Missing required property '%s' in game '%s'",
                prop, game['id'])
    for prop, value in game.items():
        expected = prop in required or prop in optional
        if not expected:
            # Don't count this as an error
            logging.warn("Unknown property '%s' in game '%s'",
            prop, game['id'])
        if prop in boolean:
            if not isinstance(value, bool):
                found_errors = True
                logging.warn("Property '%s' value should be boolean in game '%s'",
                    prop, game['id'])
        elif prop in string_array:
            if not isinstance(value, list):
                found_errors = True
                logging.warn("Property '%s' value should be list of strings in game '%s'",
                    prop, game['id'])
                continue
            for item in value:
                if not isinstance(item, str):
                    found_errors = True
                    logging.warn("Item '%s' in property '%s' should be a string in game '%s'",
                        item, prop, game['id'])
        elif prop in string_dict:
            if not isinstance(value, dict):
                found_errors = True
                logging.warn("Property '%s' value should be a map of string: string in game '%s'",
                    prop, game['id'])
                continue
            for item_key, item_value in value.items():
                if not isinstance(item_key, str):
                    error = True
                    logging.warn("Item key '%s' in property '%s' should be a string in game '%s'",
                        item_key, prop, game['id'])
                if not isinstance(item_value, str):
                    error = True
                    logging.warn("Item value '%s' of key '%s' in property '%s' should be a string in game '%s'",
                        item_value, item_key, prop, game['id'])
        else:
            # String property
            if not isinstance(value, str):
                found_errors = True
                logging.warn("Property '%s' value should be string in game '%s'",
                    prop, game['id'])
    return not found_errors


dgl_status_file = "./rcs/status"

# Extra paths to tail for milestone updates. This is a legacy setting, you
# should use `milestone_path` or `dir_path` for each game in the games dict.
# (This setting can be a string or list of strings.)
milestone_file = ["./milestones"]

status_file_update_rate = 5

recording_term_size = (80, 24)

max_connections = 100

# Script to initialize a user, e.g. make sure the paths
# and the rc file exist. This is not done by the server
# at the moment.
init_player_program = "./util/webtiles-init-player.sh"

ssl_options = None # No SSL
#ssl_options = {
#    "certfile": "./webserver/localhost.crt",
#    "keyfile": "./webserver/localhost.key"
#}
ssl_address = ""
ssl_port = 8081
# Or listen on multiple address/port pairs (overriding the above) with:
# ssl_bind_pairs = (
#     ("127.0.0.1", 8081),
#     ("localhost", 8083),
# )

connection_timeout = 600
max_idle_time = 5 * 60 * 60

use_gzip = True

# Seconds until stale HTTP connections are closed
# This needs a patch currently not in mainline tornado.
http_connection_timeout = None

# Set this to true if you are behind a reverse proxy
# Your proxy must set header X-Real-IP
#
# Enabling this option when webtiles is NOT protected behind a reverse proxy
# introduces a security risk. An attacker could inject a false address into the
# X-Real-IP header. Do not enable this option if the webtiles server is
# directly exposed to users.
http_xheaders = None

kill_timeout = 10 # Seconds until crawl is killed after HUP is sent

nick_regex = r"^[a-zA-Z0-9]{3,20}$"
max_passwd_length = 20

allow_password_reset = False # Set to true to allow users to request a password reset email. Some settings must be properly configured for this to work

# Set to the primary URL where a player would reach the main lobby
# For example: "http://crawl.akrasiac.org/"
# This is required for for password reset, as it will be the base URL for
# recovery URLs.
lobby_url = None

# Proper SMTP settings are required for password reset to function properly.
# if smtp_host is anything other than `localhost`, you may need to adjust the
# timeout settings (see server.py, calls to ioloop.set_blocking_log_threshold).
# TODO: set_blocking_log_threshold is deprecated in tornado 5+...
# Ideally, test out these settings carefully in a non-production setting
# before enabling this, as there's a bunch of ways for this to go wrong and you
# don't want to get your SMTP server blacklisted.
smtp_host = "localhost"
smtp_port = 25
smtp_use_ssl = False
smtp_user = "" # set to None for no auth
smtp_password = ""
smtp_from_addr = "noreply@crawl.example.org" # The address from which automated
                                             # emails will be sent

# crypt() algorithm, e.g. "1" for MD5 or "6" for SHA-512; see crypt(3). If
# false, use traditional DES (but then only the first eight characters of the
# password are significant). If set to "broken", use traditional DES with
# the password itself as the salt; this is necessary for compatibility with
# dgamelaunch, but should be avoided if possible because it leaks the first
# two characters of the password's plaintext.
crypt_algorithm = "broken"

# The length of the salt string to use. If crypt_algorithm is false, this
# setting is ignored and the salt is two characters.
crypt_salt_length = 16

login_token_lifetime = 7 # Days

uid = None  # If this is not None, the server will setuid to that (numeric) id
gid = None  # after binding its sockets.

umask = None # e.g. 0077

chroot = None

pidfile = None
daemon = False # If true, the server will detach from the session after startup

# Set to a URL with %s where lowercased player name should go in order to
# hyperlink WebTiles spectator names to their player pages.
# For example: "http://crawl.akrasiac.org/scoring/players/%s.html"
# Set to None to disable player page hyperlinks
player_url = None

# Only for development:
# This is insecure; do not set development_mode = True in production!
development_mode = False

# Disable caching of static files which are not part of game data.
no_cache = development_mode
# Automatically log in all users with the username given here.
autologin = None
