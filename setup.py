#!/usr/bin/env python
# coding: utf-8

from os.path import exists

from setuptools import setup

setup(name='mentor',
      version='0.2.1',
      description='Extensible Python Framework for Apache Mesos',
      url='http://github.com/daskos/mentor',
      maintainer='Krisztián Szűcs',
      maintainer_email='krisztian.szucs@daskos.com',
      license='Apache License, Version 2.0',
      keywords='mesos framework multiprocessing',
      packages=['mentor', 'mentor.proxies', 'mentor.apis'],
      long_description=(open('README.md').read() if exists('README.md')
                        else ''),
      install_requires=['cloudpickle', 'kazoo', 'futures'],
      extras_require={'mesos': ['mesos.native']},
      setup_requires=['pytest-runner'],
      tests_require=['pytest-mock', 'pytest'],
      zip_safe=False)
