#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pycompmusic',
      version='0.1',
      description='Tools for playing with the compmusic collection',
      author='CompMusic / MTG UPF',
      url='http://compmusic.upf.edu',
      packages=find_packages(exclude=["test"])
)
