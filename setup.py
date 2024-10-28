#!/usr/bin/env python

from setuptools import setup, find_packages

import versioneer

setup(name='pycompmusic',
      version=versioneer.get_version(),
      description='Tools for playing with the compmusic collection',
      author='CompMusic / MTG UPF',
      author_email='compmusic@upf.edu',
      url='https://compmusic.upf.edu',
      install_requires=['requests'],
      packages=find_packages(),
      cmdclass=versioneer.get_cmdclass()
)
