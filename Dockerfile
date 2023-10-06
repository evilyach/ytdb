FROM alpine:3.18.4 AS bot

WORKDIR /app/

RUN apk add --update --no-cache python3 ffmpeg && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN python3 -m pip install poetry

COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY . /app/
CMD ["python", "app.py"]
