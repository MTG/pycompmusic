#!/usr/bin/env python

import compmusic
import imp
import importlib
import inspect
import argparse
import os
import sys
import logging

from compmusic import extractors

logger = logging.getLogger("extractor")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def _get_module_by_path(modulepath):
    mod, clsname = modulepath.rsplit(".", 1)
    package = importlib.import_module(mod)
    cls = getattr(package, clsname)
    return cls

def _get_module_by_slug(slug):
    # Get all files in the module
    fname, dirname, desc = imp.find_module("extractors", compmusic.__path__)
    modules = set(["compmusic.extractors.%s" % os.path.splitext(module)[0]
                for module in os.listdir(dirname) if module.endswith(".py")])

    for m in modules:
        try:
            loaded = importlib.import_module(m)
            for name, mod in inspect.getmembers(loaded, inspect.isclass):
                if issubclass(mod, extractors.ExtractorModule) and name != "ExtractorModule":
                    if mod.__slug__ == slug:
                        return mod
        except ImportError:
            pass
    return None

def load_module(modulepath):
    if "." in modulepath:
        # it's an exact path
        module = _get_module_by_path(modulepath)
    else:
        # it's a slug, search for it.
        module = _get_module_by_slug(modulepath)
    if module:
        return module()
    else:
        return None

def save_data(module, data):
    output = module.__output__
    mbid = module.musicbrainz_id
    for key, d in data.items():
        ext = output[key]["extension"]
        if output[key].get("parts", False) is False:
            d = [d]
        for i in range(len(d)):
            fname = "%s-%s-%s.%s" % (mbid, key, i, ext)
            print "Writing output for type %s to %s" % (key, fname)
            open(fname, "wb").write(d[i])

def run_file(module, filename, mbid=None):
    if not mbid:
        md = compmusic.file_metadata(filename)
        mbid = md["meta"]["recordingid"]

    if mbid:
        module.musicbrainz_id = mbid
        ret = module.run(filename)
        save_data(module, ret)
    else:
        print >>sys.stderr, "Cannot find a mbid in this file. Use the mbid argument"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print >>sys.stderr, "usage: %s module file [mbid]" % sys.argv[0]
        print >>sys.stderr, "module can be a python path or slug"
        sys.exit(1)
    mbid = None
    if len(sys.argv) == 4:
        mbid = sys.argv[3]
    module = sys.argv[1]
    filename = sys.argv[2]

    themod = load_module(module)
    if themod:
        run_file(themod, filename, mbid)
    else:
        print >>sys.stderr, "could not load the module. does it exist and can"
        print >>sys.stderr, "you load it in a python shell?"

