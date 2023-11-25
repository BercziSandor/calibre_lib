FROM python:3-alpine3.17
#https://medium.com/@harpalsahota/dockerizing-python-poetry-applications-1aa3acb76287

RUN mkdir -p /app/calibre2md
COPY /calibre2md /app/calibre2md
COPY pyproject.toml /app

WORKDIR /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip install --upgrade pip
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
#CMD [ "poetry", "run", "python", "-c", "calibre2md/main.py" ]
