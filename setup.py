#!/usr/bin/env python

from setuptools import setup, find_packages

import versioneer

setup(name='pycompmusic',
      version=versioneer.get_version(),
      description='Tools for playing with the compmusic collection',
      author='CompMusic / MTG UPF',
      author_email='compmusic@upf.edu',
      url='http://compmusic.upf.edu',
      install_requires=['musicbrainzngs', 'requests', 'six', 'eyed3'],
      packages=find_packages(exclude=["test"]),
      cmdclass=versioneer.get_cmdclass()
)
