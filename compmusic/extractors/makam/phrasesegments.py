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
import os
import json
import shutil
import compmusic.extractors
import subprocess
import socket

from docserver import util
from docserver import models
import tempfile
import wave
import subprocess
from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class TrainPhraseSeg(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrtxt"
    _slug = "trainphraseseg"
    _many_files = True

    _output = {
         "boundstat": {"extension": "mat", "mimetype": "application/octet-stream"},
         "fldmodel": {"extension": "mat", "mimetype": "application/octet-stream" }
         }

    def run_many(self, id_fnames):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["MCR_CACHE_ROOT"] = "/tmp/emptydir"
        subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        #subprocess_env["LD_LIBRARY_PATH"] = "/usr/local/MATLAB/MATLAB_Runtime/v85/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/os/glnxa64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/server"

        files = []
        for mbid, fname in id_fnames:
            try:
                symbtr = compmusic.dunya.makam.get_symbtr(mbid)
                files.append({ 'path': fname, 'name': symbtr['name']})
            except:
                pass
        fp, files_json = tempfile.mkstemp(".json")
        f = open(files_json, 'w')
        json.dump(files, f)
        f.close()
        os.close(fp)

        fp, boundstat = tempfile.mkstemp(".mat")
        os.close(fp)
        fp, fldmodel = tempfile.mkstemp(".mat")
        os.close(fp)

        proc = subprocess.Popen(["/srv/dunya/phraseSeg trainWrapper %s %s %s" % (files_json, boundstat, fldmodel)], stdout=subprocess.PIPE, shell=True, env=subprocess_env)

        (out, err) = proc.communicate()

        ret = {"boundstat": None, "fldmodel": None}

        boundstat_file = open(boundstat)
        ret["boundstat"] = boundstat_file.read()
        fldmodel_file = open(fldmodel)
        ret["fldmodel"] = fldmodel_file.read()

        os.unlink(files_json)
        os.unlink(boundstat)
        os.unlink(fldmodel)

        return ret

class SegmentPhraseSeg(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "symbtrtxt"
    _slug = "segmentphraseseg"

    _output = {
         "segments": {"extension": "json", "mimetype": "application/json"},
         }

    def run(self, musicbrainzid, fname):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["MCR_CACHE_ROOT"] = "/tmp/emptydir"
        subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        #subprocess_env["LD_LIBRARY_PATH"] = "/usr/local/MATLAB/MATLAB_Runtime/v85/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/os/glnxa64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/server"

        boundstat, fldmodel = (None, None)
        try:
            boundstat = util.docserver_get_filename('31b52b29-be39-4ccb-98f2-2154140920f9', "trainphraseseg", "boundstat", version="0.1")
            fldmodel = util.docserver_get_filename('31b52b29-be39-4ccb-98f2-2154140920f9', "trainphraseseg", "fldmodel", version="0.1")
        except util.NoFileException:
            raise Exception('No training files found for recording %s' % musicbrainzid)

        files = []
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        files.append({ 'path': fname, 'name': symbtr['name']})

        fp, files_json = tempfile.mkstemp(".json")
        f = open(files_json, 'w')
        json.dump(files, f)
        f.close()
        os.close(fp)

        fp, out_json = tempfile.mkstemp(".json")
        os.close(fp)

        proc = subprocess.Popen(["/srv/dunya/phraseSeg segmentWrapper %s %s %s %s" % (boundstat, fldmodel, files_json, out_json)], stdout=subprocess.PIPE, shell=True, env=subprocess_env)

        (out, err) = proc.communicate()
        ret = {"segments": []}

        segments_file = open(out_json, 'r')
        segments = segments_file.read()
        if segments == "":
            segments = "[]"
        ret["segments"].append(json.loads(segments))

        os.unlink(files_json)
        os.unlink(out_json)

        return ret
