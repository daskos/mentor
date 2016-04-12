#!/usr/bin/env python

from os.path import exists

from setuptools import setup

setup(name='satyr',
      version='0.1',
      description='A Mesos framework library mimicing multiprocessing',
      url='http://github.com/lensacom/satyr',
      maintainer='Zoltan Nagy',
      maintainer_email='zoltan.nagy@lensa.com',
      license='BSD',
      keywords='mesos framework multiprocessing',
      packages=['satyr'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      install_requires=['cloudpickle', 'colorlog', 'kazoo', 'toolz'],
      extras_require={'mesos': ['mesos.native']},
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-mock'],
      zip_safe=False)
