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

import logging

extractor_log = logging.getLogger("extractor")
adapted_logs = {}

class ExtractorAdapter(logging.LoggerAdapter):
    """ A logging adapter that lets you set the document and sourcefile
    being processed.
    You can also pass in `modulename` and `moduleversion` as
    the `extra` parameter (see
    http://docs.python.org/2/howto/logging-cookbook.html#using-loggeradapters-to-impart-contextual-information )
    and it will send all of this information to the logger handler.
    """

    def set_documentid(self, docid):
        self.docid = docid

    def set_sourcefileid(self, sfid):
        self.sourcefileid = sfid

    def process(self, msg, kwargs):
        extra = {}
        if hasattr(self, "docid"):
            extra["documentid"] = self.docid
        if hasattr(self, "sourcefileid"):
            extra["sourcefileid"] = self.sourcefileid
        extra["modulename"] = self.extra["modulename"]
        extra["moduleversion"] = self.extra["moduleversion"]
        kwargs["extra"] = extra
        return (msg, kwargs)

def get_logger(modulename, moduleversion=None):
    global adapted_logs
    if modulename not in adapted_logs:
        assert moduleversion is not None, "First time getting the logger must include module version"
        adapted_logs[modulename] = ExtractorAdapter(extractor_log, {"modulename": modulename, "moduleversion": moduleversion})
    return adapted_logs[modulename]
