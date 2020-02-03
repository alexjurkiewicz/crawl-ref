#!/bin/sh

CRAWL="/usr/games/crawl"

if [ -z "${NAME}" ] ; then
    echo 'NAME env var not provided' >&2
    exit 1
fi
if ! [ -S /webtiles-socket.sock ] ; then
    echo '/webtiles-socket.sock is not a socket' >&2
    exit 1
fi
if ! [ -d /save/ ] ; then
    echo '/save/ is not a directory' >&2
    exit 1
fi

# shellcheck disable=SC2086
exec $CRAWL -name "$NAME" -dir /save/ -rc /rc -macro /macro -morgue /morgue/ $EXTRA_OPTS -await-connection -webtiles-socket /webtiles-socket.sock
