FROM python:3-alpine

RUN apk add ffmpeg

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache --virtual .build-deps gcc libffi-dev musl-dev openssl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

ENV TOKEN="changeme" MEDIADIR="/tmp/yttg" PROXY="{}" USERS="[]"
COPY yttg_bot.py ./

CMD ["python", "./yttg_bot.py"]

