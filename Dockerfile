FROM kszucs/miniconda-mesos

ADD . /opt/satyr
RUN pip --no-cache-dir install /opt/satyr \

