FROM python:3.11.7-alpine3.18
#FROM ubuntu:latest
#https://medium.com/@harpalsahota/dockerizing-python-poetry-applications-1aa3acb76287

RUN pip install --upgrade pip
RUN pip3 install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN mkdir -p /app/calibre2web/work

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:/app:/app/calibre2web:/app/calibre2web/calibre_tools

COPY pyproject.toml poetry.lock ./
COPY calibre2web ./calibre2web
RUN touch ./README.md

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR
ENTRYPOINT [ "poetry", "run", "python", "-m", "calibre2web.main"]
