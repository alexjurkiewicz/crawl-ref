FROM debian:10 as builder

RUN apt-get update \
    && apt-get -y install build-essential libncursesw5-dev bison flex \
        liblua5.1-0-dev libsqlite3-dev libz-dev pkg-config python2 python-yaml \
        gdb libsdl2-image-dev libsdl2-mixer-dev libsdl2-dev libfreetype6-dev \
        libpng-dev ttf-dejavu-core advancecomp pngcrush \
    && apt-get clean

WORKDIR /crawl-ref
COPY . .
WORKDIR /crawl-ref/source
RUN make -j$(nproc) install \
    USE_DGAMELAUNCH=y \
    WEBTILES=y \
    STRIP=true \
    EXTERNAL_FLAGS_L="-g" \
    prefix=/usr \
    SAVEDIR=/save \
    WEBDIR=/web

FROM debian:10
RUN apt-get update \
    && apt-get -y install libncursesw5-dev liblua5.1-0-dev libsqlite3-dev \
        libz-dev gdb libsdl2-image-dev libsdl2-mixer-dev libsdl2-dev \
        libfreetype6-dev libpng-dev ttf-dejavu-core \
    && apt-get clean
WORKDIR /
COPY entry.sh .
COPY --from=builder \
    /usr/games/crawl \
    /usr/games/crawl
COPY --from=builder \
    /usr/share/crawl \
    /usr/share/crawl

CMD ["/entry.sh"]
