import logging

essentia_log = logging.getLogger("essentia")

# module/moduleversion
# sourcefile
# document

class EssentiaAdapter(logging.LoggerAdapter):

    def set_document(self, doc):
        self.doc = doc

    def process(self, msg, kwargs):
        if hasattr(self, "doc"):
            kwargs["doc"] = self.doc
        print "process, extra is ", kwargs
        return (msg, kwargs)

def get_logger(modulename, moduleversion):
    log = EssentiaAdapter(essentia_log, {"modulename": modulename, "moduleversion": moduleversion})
    return log
