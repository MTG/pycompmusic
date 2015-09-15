# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

import log
from warnings import warn
try:
    import redis
except ImportError:
    pass

class Settings(dict):
    __getattr__ = dict.__getitem__

class ExtractorModule(object):
    """ A module that runs on a file and returns an output.

    Logging:
    Inside a subclass, use self.logger to log a message.
    Inside an external module you can use
       from compmusic.extractors import log
       logger = log.get_logger("module_slug")
    where module_slug is the value defined in _slug, below
    """

    """The version of your module. String. If it changes then the algorithm
    will run again, but we don't check if it's changed 'up' or 'down'"""
    _version = None
    """The slug of the source file type that this module takes as input"""
    _sourcetype = None
    
    _depends = None
    """A handy slug that can be used to refer to this module. Should be unique
    over all modules"""
    _slug = None
    """A dictionary of output formats that this runner creates. Of the form:
    {"outputname": {"extension": "json"|"png"|"..etc",
                    "mimetype": "application/json",
                    "parts": bool},
     ...}
    The `run` method should return a dict of {"outputname": output}
    If extension is "json" then the data is considered to be a python dictionary and is
    serialised to json before writing to disk. Otherwise it's written directly and the
    extension is used as the file extension.
    If parts is True then the data is a list of parts that make up this data.
    omit `parts' to say that there is only one item in the returned data.
    If _output is missing, then the output is expected to be a json dict with no parts.
    """
    _output = None

    """
    The many_files flag indicates if the `run` method receives one file or many files
    as input
    """
    _many_files = False

    hostname = "(unknown)"

    def __init__(self, **kwargs):
        """Set up the logger, and run a setup method if it's been defined."""
        self.logger = log.get_logger(self._slug, self._version)
        self.settings = Settings()
        self.add_settings(**kwargs)
        self.setup()
        self.redis = None
        if "redis_host" in self.settings and 'redis' in globals():
            self.redis = redis.StrictRedis(host=self.settings["redis_host"])
        # This cache is used for a single process when redis is not installed
        self.cache = {}

    def get_key(self, k):
        key = "%s-%s-%s" % (self._slug, self._version, k)
        if not self.redis:
            warn("Redis not configured, assuming running locally and using local cache")
            return self.cache.get(key)
        else:
            return self.redis.get(key)

    def set_key(self, k, val, timeout=None):
        key = "%s-%s-%s" % (self._slug, self._version, k)
        if not self.redis:
            warn("Redis not configured, assuming running locally and using local cache")
            self.cache[key] = val
        else:
            if timeout:
                self.redis.setex(key, timeout, val)
            else:
                self.redis.set(key, val)

    def setup(self):
        """ Override this if you want to do some pre-setup after
        the module has been created but before you process each
        document. For example, you might want to run
        self.add_settings(a=1, b=2)
        to set up some global settings.
        """
        pass

    def process_document(self, docid, sourcefileid, musicbrainzid, fname):
        """ Set up some class state and call run. This should
        never be called publicly """
        try:
            self.document_id = docid
            self.logger.set_documentid(docid)
            self.logger.set_sourcefileid(sourcefileid)
            self.musicbrainz_id = musicbrainzid
            self.logger.info("Worker %s" % self.hostname)
            return self.run(fname)
        except Exception, e:
            self.logger.error(e)
            raise e

    def run(self, fname):
        """Overwrite this to process a file. If you need the document ID then it's available at
        self.document_id. There is a logger available at self.logger that is written to the
        docserver database."""
        pass

    def add_settings(self, **kwargs):
        """Add some global settings"""
        for k, v in kwargs.items():
            self.settings[k] = v

