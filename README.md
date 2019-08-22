pycompmusic
===========

Introduction
------------
Python tools for analysing and working with audio.

This repository contains utilities and algorithms for use in the Dunya
project (https://github.com/MTG/dunya, https://dunya.compmusic.upf.edu), 
but is separate to make it easier to develop.

Authors
-------
Dunya and pycompmusic have been developed by a number of people in the
CompMusic project. For a list of contributors see the AUTHORS file.
Dunya includes methods and techniques developed as part of CompMusic.
For a list of publications see https://compmusic.upf.edu/node/4.

License
=======
Dunya is Copyright 2013-2019 Music Technology Group - Universitat Pompeu Fabra

Dunya is released under the terms of the GNU Affero General Public
License (v3 or later). See the COPYING file for more information.

If you would prefer to get a (non FOSS) commercial license, please
contact us at mtg@upf.edu

Installation
============

This library is designed for python 3. We only support python 2 on a best-effort basis.

It is recommended to install pycompmusic and dependencies into a virtualenv.
Do it like this:

    virtualenv -p python3 env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install compmusic like this instead

    pip install -e .

Now you can install the rest of the dependencies:

    pip install -r requirements.txt

Documentation
=============

There are sphinx docs available in the `docs` directory. Install sphinx to be able to build them

    pip install sphinx
    
to build the docs run
    
    make html
    
from the root directory.

API Quick reference
---------------

In order to use the api is required to have a user in dunya. You can register on 
dunya through the web: https://dunya.compmusic.upf.edu/social/register/ .
Once your account is active you can start using the api, for example you can get
the information of all the recording of the makam collections with this url:
    https://dunya.compmusic.upf.edu/api/makam/recording

In this repository you can find the code to access the API with python. For 
example to access the recording in the makam collection:

    from compmusic import dunya
    dunya.set_token("<your_token>")
    recordings = dunya.makam.get_recordings()

In order to get your API token you have to log in to dunya 
(https://dunya.compmusic.upf.edu/social/login/) and then go to your profile:
https://dunya.compmusic.upf.edu/social/profile/ where you will find your token.

