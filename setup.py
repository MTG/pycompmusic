#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pycompmusic',
      version='0.1',
      description='Tools for playing with the compmusic collection',
      author='CompMusic / MTG UPF',
      url='http://compmusic.upf.edu',
      install_requires=['musicbrainzngs', 'requests', 'six', 'eyed3']
      packages=find_packages(exclude=["test"])
)
