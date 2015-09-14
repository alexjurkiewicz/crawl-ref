"""Tornado handler to save/list/download Crawl games.

Used by administrators for bug troubleshooting.
"""

import logging
import os
import shutil
import time

import tornado.web
from tornado.escape import url_unescape

import userdb
from conf import config


class SaveHandler(tornado.web.RequestHandler):

    """Handle save backup requests.

    These can be:
    1. Back up a current save
    2. Serve a backed-up save (to devs).
    3. List currently backed-up saves.
    """

    def _listsaves(self):
        """List all files in the save backup directory."""
        save_path = config['save_backup_path']
        saves = [item for item in os.listdir(save_path) if
                 os.path.isfile(os.path.join(save_path,
                                item))]
        logging.debug("Listing %s saves", len(saves))
        self.write('<br>\n'.join(saves))

    def _getsave(self):
        """Serve a save file.

        TODO: check request is authorised.
        """
        save_path = config['save_backup_path']
        if 'id' not in self.request.arguments:
            self.send_error(400, message="Missing id!")
        saveid = self.request.arguments['id'][0]
        name = saveid + '.cs'

        logging.debug("Sending save %s", name)
        path = os.path.join(config['save_backup_path'], name)
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition",
                        "attachment; filename=" + name)
        fh = open(path, "rb")
        self.write(fh.read())
        fh.close()
        self.flush()

    def _createsave(self):
        """Back up the current save for name in game gameid."""
        save_path = config['save_backup_path']
        # savename = '{date}-{gameid}-{name}'
        sid = self.get_cookie("sid")
        session = None
        if sid:
            session = userdb.session_info(url_unescape(sid))
        if not session:
            self.fail(403, "You must be logged in to access this.")
            return

        username = session["username"]
        game_id = self.request.arguments['id'][0]

        if "dir_path" not in config['games'][game_id]:
            logging.warn("Someone tried to save a game for "
                         "%s which doesn't have dir_path set", config['games'][game_id])
            self.fail(400, "Can't backup saves for this game sorry.")
            return
        base_path = config['games'][game_id]['dir_path']

        source_file = os.path.join(base_path, username + '.cs')
        dest_file = os.path.join(save_path, '{date}-{name}-{gameid}'.format(date=time.strftime('%Y-%m-%d %H:%M:%S'), name=username, gameid=game_id))

        logging.info("Copying %s to %s", source_file, dest_file)


    def get(self, command):
        """Handle requests."""
        if not command:
            self._listsaves()
        elif command == 'get':
            self._getsave()
        elif command == 'create':
            self._createsave()
        else:
            self.send_error(400, message="Unknown command!")

    def write_error(self, status_code, **kwargs):
        """Handler override for error page rendering."""
        if "message" in kwargs:
            msg = "{0}: {1}".format(status_code, kwargs["message"])
            self.write("<html><body>{0}</body></html>".format(msg))
