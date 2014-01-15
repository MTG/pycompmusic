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
