#!/usr/bin/env python
from setuptools import setup
import versioneer

setup(name='pycompmusic',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass()
)
