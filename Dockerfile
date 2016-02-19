FROM python:2.7

RUN wget http://downloads.mesosphere.io/master/debian/8/mesos-0.27.0-py2.7-linux-x86_64.egg -O mesos.egg && \
    easy_install mesos.egg

ADD . /satyr
RUN pip install --upgrade pip mesos.interface && \
    pip install /satyr
