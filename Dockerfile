FROM kszucs/mesos-alpine:python

ADD . /satyr
RUN pip --no-cache-dir install /satyr \
 && rm -rf /satyr
