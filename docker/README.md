# Docker Images for `dcss`: Dungeon Crawl: Stone Soup

## Supported tags

* `0.25-release-console`
* `0.25-webtiles`

## How to build images

Use `./build <target>`. See the output of `./build --help` for a list of targets.

## Image Variants

### `dcss:release-console`

A normal build of DCSS. Use this if you want to play DCSS via a Docker image locally.

Run it with: `docker run --rm -ti dcss:release-console`

### `dcss:webtiles`

Optimised for running on webtiles servers. Includes full debug info, and custom paths for writing dynamic data.

Run this image like:

```sh
docker run --rm dcss:webtiles \
    -e NAME=$name \
    -e EXTRA_OPTS="-extra-opt-last travel_delay=20" \
    -v /host/dcss/webtiles-socket.sock:/webtiles-socket.sock \
    -v /host/dcss/save-dir:/save/ \
    -v /host/dcss/player-rc-file:/rc \
    -v /host/dcss/player-macro-file:/macro \
    -v /host/dcss/player-morgue-dir:/morgue/ \

```

Specify the following environment variables:

* `NAME`: player name
* `EXTRA_OPTS`: (optional) extra command-line options to pass to DCSS

Provide the following mounts:

* `/webtiles-socket.sock`: The webtiles server communication socket.
* `/save/`: The server's save directory. (This is where save files, logfile, and milestone files are written.)
* `/rc`: (optional) Player's RC file. If not provided, an empty one will be used.
* `/macro`: (optional) Player's macro file. If not mounted, an empty one will be used.
* `/morgue/`: (optional) Morgue directory for this player. If not mounted, the morgue files will be lost.

Inside the container, DCSS is run with the following options:

```sh
    crawl \
        -name "$NAME" -dir /save/ \
        -rc /rc -macro /macro -morgue /morgue/ \
        $EXTRA_OPTS \
        -await-connection -webtiles-socket /webtiles-socket.sock
```
