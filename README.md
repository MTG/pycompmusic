pycompmusic
===========

Introduction
------------
API Interface to CompMusic Dunya. Dunya is a research project that studies several 
world music traditions from the point of view of the information technologies, 
with the aim to facilitate the cataloging and discovery of music recordings
within large repositories. For more information: http://compmusic.upf.edu

Authors
-------
PyCompmusic was written by members of the Music Technology Group at 
Universitat Pompeu Fabra (https://www.upf.edu/web/mtg/).

License
=======
Pycompmusic is Copyright 2013-2024 Music Technology Group - Universitat Pompeu Fabra

Pycompmusic is released under the terms of the MIT License. See the LICENSE file for
more information.

Installation
============

This library is designed for use with Python 3

It is recommended to install pycompmusic and dependencies into a virtualenv.
Do it like this:

    python -m venv venv
    source venv/bin/activate
    python setup.py install

Alternatively, install directly from pypi:

    pip install pycompmusic

Documentation
=============

There are sphinx docs available in the `docs` directory. Install sphinx to be able to build them

    pip install sphinx
    
to build the docs run
    
    make html
    
from the root directory.

API Quick reference
-------------------

In order to use the API you need to register for a user account with Dunya. 
You can register at https://dunya.compmusic.upf.edu/user/register/ .
Once your account is active you can start using the api.

In this repository you can find the code to access the API with python. For 
example to access recordings in the makam collection:

    from compmusic import dunya
    dunya.set_token("<your_token>")
    recordings = dunya.makam.get_recordings()

In order to get your API token you have to log in to dunya 
(https://dunya.compmusic.upf.edu/social/login/) and then go to your profile:
https://dunya.compmusic.upf.edu/social/profile/ where you will find your token.

