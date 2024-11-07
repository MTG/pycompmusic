#!/usr/bin/env python
from setuptools import setup
import versioneer

setup(name='compmusic',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass()
)
