pycompmusic
===========

Python tools for interacting with the compmusic infrastructure

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
