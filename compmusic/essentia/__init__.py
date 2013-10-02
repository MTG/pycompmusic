import log

class EssentiaModule(object):
    def __init__(self):
        classname = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        self.logger = log.get_logger(classname, self.__version__)

    def do_run(self, docid, sourcefile, fname):
        self.logger.set_document(docid)
        self.run(fname)
