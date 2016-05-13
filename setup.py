#!/usr/bin/env python
# coding: utf-8

from os.path import exists

from setuptools import setup

setup(name='satyr',
      version='0.1.4',
      description='Extensible Python Framework for Apache Mesos',
      url='http://github.com/lensacom/satyr',
      maintainer='Krisztián Szűcs',
      maintainer_email='krisztian.szucs@lensa.com',
      license='Apache License, Version 2.0',
      keywords='mesos framework multiprocessing',
      packages=['satyr', 'satyr.proxies', 'satyr.apis'],
      long_description=(open('README.md').read() if exists('README.md')
                        else ''),
      install_requires=['cloudpickle', 'kazoo'],
      extras_require={'mesos': ['mesos.native']},
      setup_requires=['pytest-runner'],
      tests_require=['pytest-mock', 'pytest'],
      zip_safe=False)
