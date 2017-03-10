#!/usr/bin/env python
# coding: utf-8

from os.path import exists

from setuptools import setup
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(name='mentor',
      version='0.2.1',
      description='Extensible Python Framework for Apache Mesos',
      url='http://github.com/daskos/mentor',
      maintainer='Krisztián Szűcs',
      maintainer_email='krisztian.szucs@daskos.com',
      license='Apache License, Version 2.0',
      keywords='mesos framework multiprocessing',
      packages=['mentor', 'mentor.messages', 'mentor.apis'],
      long_description=read_md('README.md'),
      install_requires=['cloudpickle', 'kazoo', 'futures', 'protobuf','neobunch'],
      extras_require={'mesos': ['mesos.native']},
      setup_requires=['pytest-runner','pypandoc'],
      tests_require=['pytest-mock', 'pytest', 'mock', 'pytest-tornado','pytest-cov'],
      zip_safe=False)
