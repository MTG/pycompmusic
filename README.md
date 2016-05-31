pycompmusic
===========

Introduction
------------
Python tools for analysing and working with audio.

This repository contains utilities and algorithms for use in the Dunya
project (https://github.com/MTG/dunya, http://dunya.compmusic.upf.edu), 
but is separate to make it easier to develop.

Authors
-------
Dunya and pycompmusic have been developed by a number of people in the
CompMusic project. For a list of contributors see the AUTHORS file.
Dunya includes methods and techniques developed as part of CompMusic.
For a list of publications see http://compmusic.upf.edu/node/4.

License
=======
Dunya is Copyright 2013 Music Technology Group - Universitat Pompeu Fabra

Dunya is released under the terms of the GNU Affero General Public
License (v3 or later). See the COPYING file for more information.

If you would prefer to get a (non FOSS) commercial license, please
contact us at mtg@upf.edu

Installation
============

It is recommended to install pycompmusic and dependencies into a virtualenv.
Do it like this:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then
install compmusic like this instead

    pip install -e .

You need to install some other dependencies as well. If you are using Ubuntu then
it's recommended you use the system versions of numpy and scipy so that you don't
need to compile them from scratch. Do that like this:

    sudo apt-get install python-numpy python-scipy
    ln -s /usr/lib/python2.7/dist-packages/numpy* env/lib/python2.7/site-packages
    ln -s /usr/lib/python2.7/dist-packages/scipy* env/lib/python2.7/site-packages

You need to do the same with essentia:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Now you can install the rest of the dependencies:

    pip install -r requirements

Documentation
=============

There are sphinx docs available in the `docs` directory. To compile them, run
`make html` from the root directory.
You need to be able to import each module in order to be able to do the autodocs.
This means that you will need all the dependencies available in the python path.
One way to do this is to use python from a virtualenv directly:

    env/bin/python /usr/bin/sphinx-build -b html -d build/doctrees docs build/html

Or install sphinx in the virtualenv

API Quick reference
---------------

In order to use the api is required to have a user in dunya. You can register on 
dunya through the web: http://dunya.compmusic.upf.edu/social/register/ .
Once your account is active you can start using the api, for example you can get
the information of all the recording of the makam collections with this url:
    http://dunya.compmusic.upf.edu/api/makam/recording

In this repository you can find the code to access the API with python. For 
example to access the recording in the makam collection:

    from compmusic import dunya
    dunya.set_token("<your_token>")
    recordings = dunya.makam.get_recordings()

In order to get your API token you have to log in to dunya 
(http://dunya.compmusic.upf.edu/social/login/) and then go to your profile:
http://dunya.compmusic.upf.edu/social/profile/ where you will find your token.

