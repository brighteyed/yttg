FROM python:3-alpine

RUN pip install --no-cache-dir youtube_dl
RUN apk add ffmpeg

RUN mkdir /var/downloads && chmod a+rw /var/downloads
VOLUME ["/var/downloads"]
WORKDIR /var/downloads

ENTRYPOINT [ "youtube-dl" ]
CMD ["--help"]

