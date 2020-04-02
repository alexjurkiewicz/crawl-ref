import datetime
import logging
import random
import time

import tornado.ioloop
import tornado.websocket
from tornado.ioloop import IOLoop

import config

try:
    from typing import Dict, Tuple, NewType, Optional, NamedTuple
except ImportError:
    pass

class LoginToken(NamedTuple):
    username # type: str
    token_id # type: int
class FailedLoginToken(NamedTuple):
    username # type: str
    token_id # type: None
class LoginResult(NamedTuple):
    username # type: str
    logged_in # type: bool

login_tokens = {}  # type: Dict[LoginToken, datetime.datetime]
rand = random.SystemRandom()


def purge_login_tokens():
    # type: () -> None
    for token in list(login_tokens):
        if datetime.datetime.now() > login_tokens[token]:
            del login_tokens[token]


def purge_login_tokens_timeout():
    # type: () -> None
    purge_login_tokens()
    IOLoop.current().add_timeout(time.time() + 60 * 60 * 1000,
                                 purge_login_tokens_timeout)


def log_in_as_user(request, username):
    # type: (Any, str) -> None
    token_id = rand.getrandbits(128)
    expires = datetime.datetime.now() + datetime.timedelta(config.login_token_lifetime)
    login_tokens[LoginToken(username, token_id)] = expires
    cookie = username + "%20" + str(token_id)
    if not isinstance(request, tornado.websocket.WebSocketHandler):
        request.set_cookie("login", cookie)
    return cookie


def _parse_login_cookie(cookie):
    # type (str) -> Union[LoginToken, FailedLoginToken]
    username, raw_token = cookie.split('%20', 1)
    try:
        token = int(raw_token)
    except ValueError:
        return FailedLoginToken(username, None)
    return LoginToken(username, token)


def check_login_cookie(cookie):
    # type (str) -> LoginResult
    """Parse and validate login cookie. Returns (username, logged_in)."""
    login_token = _parse_login_cookie(cookie)
    if login_token.token_id is None:
        return LoginResult(login_token.username, False)
    return LoginResult(username, login_token in login_tokens)


def forget_login_cookie(cookie):
    # type (str) -> None
    login_token = _parse_login_cookie(cookie)
    try:
        del login_tokens[login_token]
    except KeyError:
        return
