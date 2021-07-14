FROM python:3.9-slim

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD uvicorn --host 0.0.0.0 routes.api:app
