FROM debian:10 as builder

RUN apt-get update \
    && apt-get -y install build-essential libncursesw5-dev bison flex \
        liblua5.1-0-dev libsqlite3-dev libz-dev pkg-config python2 python-yaml \
    && apt-get clean

WORKDIR /crawl-ref
COPY . .
WORKDIR /crawl-ref/source
RUN make -j$(nproc) install prefix=/usr

FROM gcr.io/distroless/base-debian10:latest
COPY --from=builder /usr/share/crawl /usr/share/crawl
COPY --from=builder /usr/games/crawl /crawl
COPY --from=builder \
    /usr/lib/x86_64-linux-gnu/liblua5.1.so.0 \
    /usr/lib/x86_64-linux-gnu/libsqlite3.so.0 \
    /usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
    /usr/lib/x86_64-linux-gnu/
COPY --from=builder \
    /lib/x86_64-linux-gnu/libz.so.1 \
    /lib/x86_64-linux-gnu/libncursesw.so.6 \
    /lib/x86_64-linux-gnu/libtinfo.so.6 \
    /lib/x86_64-linux-gnu/libgcc_s.so.1 \
    /lib/
COPY --from=builder \
    /lib/terminfo \
    /lib/terminfo
RUN ["/crawl", "-builddb"]

CMD ["/crawl"]
