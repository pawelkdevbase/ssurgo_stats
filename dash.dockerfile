ARG BASE_IMAGE=python:3.10.0-slim-bullseye
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get upgrade -y
WORKDIR /usr/src/app
COPY ../show.py show.py
COPY ../gis/ gis/
COPY ../report.csv report.csv
COPY ../requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN ls gis
ENV PYTHONPATH=/usr/src/app
