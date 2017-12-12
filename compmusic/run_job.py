#!/usr/bin/env python
from __future__ import print_function

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import imp
import importlib
import inspect
import argparse
import logging
import json
import compmusic
from compmusic import extractors
import numpy as np

logger = logging.getLogger("extractor")
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#logger.addHandler(ch)

def _get_module_by_path(modulepath):
    mod, clsname = modulepath.rsplit(".", 1)
    try:
        package = importlib.import_module(mod)
        cls = getattr(package, clsname)
        return cls
    except ImportError:
        logger.warn("Cannot import the module: %s" % mod)
        logger.warn("Try it in a terminal and see what the error is")

def _get_module_by_slug(slug):
    # Get all files in the module
    fname, dirname, desc = imp.find_module("extractors", compmusic.__path__)
    modules = set(["compmusic.extractors.%s" % os.path.splitext(module)[0]
                for module in os.listdir(dirname) if module.endswith(".py")])

    unloaded = []
    matching = []
    for m in modules:
        try:
            loaded = importlib.import_module(m)
            for name, mod in inspect.getmembers(loaded, inspect.isclass):
                if issubclass(mod, extractors.ExtractorModule) and name != "ExtractorModule":
                    if mod._slug == slug:
                        matching.append(mod)
        except ImportError:
            unloaded.append(m)

    if unloaded:
        logger.warn("Failed to load these modules due to an import error, check that you have all their dependencies installed")
        for u in unloaded:
            logger.warn(u)

    if len(matching) > 1:
        logger.warn("Found more than one module with the same slug. Slugs must be unique")
        logger.warn("For slug: %s" % slug)
        for m in matching:
            logger.warn("  %s" % m)
    elif len(matching) == 1:
        return matching[0]
    else:
        logger.warn("Cannot find a module with the slug: %s" % slug)
        logger.warn("Check that you have spelt it correctly")
        if unloaded:
            logger.warn("or that the module it is in can be loaded (is it in one of the above failed modules?)")
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

class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # or map(int, obj)
        return json.JSONEncoder.default(self, obj)

def save_data(module, data):
    modulemeta = module._output
    mbid = module.musicbrainz_id
    for key, d in data.items():
        ext = modulemeta[key]["extension"]
        if modulemeta[key].get("parts", False) is False:
            d = [d]
        for i in range(len(d)):
            fname = "%s-%s-%s.%s" % (mbid, key, i, ext)
            print("Writing output for type %s to %s" % (key, fname))
            if modulemeta[key]["mimetype"] == "application/json":
                output = json.dumps(d[i], cls=NumPyArangeEncoder)
            else:
                output = d[i]
            open(fname, "wb").write(output)

def run_file(module, filename, mbid=None):
    if not mbid:
        if filename.lower().endswith(".mp3"):
            md = compmusic.file_metadata(filename)
            mbid = md["meta"]["recordingid"]
    if mbid:
        module.musicbrainz_id = mbid
        ret = module.run(mbid, filename)
        save_data(module, ret)
    else:
        logging.error("Cannot find a mbid in this file. Use the mbid argument")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: %s module file [mbid]" % sys.argv[0], file=sys.stderr)
        print("module can be a python path or slug", file=sys.stderr)
        sys.exit(1)
    mbid = None
    if len(sys.argv) == 4:
        mbid = sys.argv[3]
    module = sys.argv[1]
    filename = sys.argv[2]

    themod = load_module(module)
    if themod:
        run_file(themod, filename, mbid)

