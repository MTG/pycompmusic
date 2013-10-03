import logging

essentia_log = logging.getLogger("essentia")

class EssentiaAdapter(logging.LoggerAdapter):
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

def get_logger(modulename, moduleversion):
    log = EssentiaAdapter(essentia_log, {"modulename": modulename, "moduleversion": moduleversion})
    return log
