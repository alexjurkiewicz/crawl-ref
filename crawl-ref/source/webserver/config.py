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
#    "filename": "webtiles.log",
    "level": logging.INFO,
    "format": "%(asctime)s %(levelname)s: %(message)s"
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
# 2. As extra games to append to this list from the `load_games` function
#
# %n in paths and urls is replaced by the current username
#
# morgue_url is for a publicly available URL to access morgue_path
#
# milestone_path is the path milestones are written (used for tracking active
# game actions in the lobby list). If not set, it can be calculated from
# dir_path. If that is also not set, there is no default. You just need to
# specify the path to the "milestones" file, the "milestones-seeded" file next
# to it will be automatically discovered.
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
        # Passed as -dir $dir_path to Crawl. Default: unset (not passed to Crawl).
        # dir_path = ".",
        # Directory we execute $crawl_binary in. Default: CWD.
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
    a dictionary as per the above examples, with an extra key `id` for the
    game's ID. Directory paths support %n as described above.

    This example function will only add or update games. It doesn't support
    removing or reordering games. If you want to add support for either, read
    the caveats below and please contribute the improvement as a pull request!

    Dynamic update caveats:

    1. The main use-case is to support adding new game modes to a running
       server. Other uses (like modifying or removing an existing game mode, or
       re-ordering the games list) are not well tested.
    2. If you do modify a game entry, the changed settings only affect new game
       sessions. Any existing sessions will use the old config until they close.
    3. Some settings will affect spectators as well. If you modify a running
       game's config, it might break spectating until the player restarts.
    """
    conf_subdir = "games.d"
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), conf_subdir)
    for file_name in sorted(os.listdir(base_path)):
        logging.debug("Parsing %s", file_name)
        path = os.path.join(base_path, file_name)
        if not os.path.isfile(path):
            continue
        if not file_name.endswith('.yaml'):
            continue
        with open(path) as f:
            raw_data = f.read()
        try:
            data = yaml.safe_load(raw_data)
        except yaml.YAMLError:
            logging.exception("Failed to load games from %s, skipping (parse failure).", file_name)
            continue
        if data is None or 'games' not in data:
            logging.warning("Failed to load games from %s, skipping (no 'games' key).", file_name)
            continue
        for game in data['games']:
            game_id = game['id']
            del(game['id'])
            action = "Updated" if game_id in games else "Loaded"
            games[game_id] = game
            logging.info("%s game config %s from %s.", action, game_id, file_name)


dgl_status_file = "./rcs/status"

# Extra paths for milestones to read. You should probably just use
# milestone_path in the games list.
# Can be a string or list of strings.
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
