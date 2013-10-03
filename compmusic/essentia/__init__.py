import log

class EssentiaModule(object):
    def __init__(self):
        classname = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        self.logger = log.get_logger(classname, self.__version__)

    def process_document(self, docid, sourcefileid, fname):
        self.logger.set_documentid(docid)
        self.logger.set_sourcefileid(sourcefileid)
        self.run(fname)
