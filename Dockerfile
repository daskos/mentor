FROM lensa/mesos-python:0.27.0-py2.7-python-2.7

ADD . /satyr
WORKDIR /satyr
RUN pip install .
