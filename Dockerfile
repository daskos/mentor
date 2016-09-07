FROM kszucs/mesos-alpine:python

ADD . /satyr
RUN pip install -e /satyr
