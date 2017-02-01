FROM python:3.5.2-alpine

ADD . /mentor
WORKDIR /mentor
RUN pip install .