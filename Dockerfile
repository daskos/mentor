FROM python:2.7

USER root
RUN wget http://downloads.mesosphere.io/master/debian/8/mesos-0.25.0-py2.7-linux-x86_64.egg -O mesos.egg && \
    easy_install mesos.egg

ADD . /satyr
WORKDIR /satyr
RUN pip install .
