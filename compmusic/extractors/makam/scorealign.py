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
import compmusic.extractors
import subprocess
import socket

import tempfile
import wave
import subprocess
from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class ScoreAlign(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "scorealign"

    _output = {
        "notesalign": {"extension": "json", "mimetype": "application/json"}
    }

    def run(self, musicbrainzid, fname):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["MCR_CACHE_ROOT"] = "/tmp/emptydir"
        #subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        subprocess_env["LD_LIBRARY_PATH"] = "/usr/local/MATLAB/MATLAB_Runtime/v85/runtime/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/bin/glnxa64:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/os/glnxa64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sy    s/java/jre/glnxa64/jre/lib/amd64/:/usr/local/MATLAB/MATLAB_Runtime/v85/sys/java/jre/glnxa64/jre/lib/amd64/server"
        rec_data = dunya.makam.get_recording(musicbrainzid)
 
        if len(rec_data['works']) == 0:
            raise Exception('No work on recording %s' % musicbrainzid)
 
        symbtrtxt =util.docserver_get_symbtrtxt(rec_data['works'][0]['mbid'])
        if not symbtrtxt:
            raise Exception('No work on recording %s' % musicbrainzid)
        metadata = util.docserver_get_filename(rec_data['works'][0]['mbid'], "metadata", "metadata", version="0.1")
        tonic = util.docserver_get_filename(rec_data['works'][0]['mbid'], "tonictempotuning", "tonic", version="0.1")
        tempo = util.docserver_get_filename(rec_data['works'][0]['mbid'], "tonictempotuning", "tempo", version="0.1")
        tuning = util.docserver_get_filename(rec_data['works'][0]['mbid'], "tonictempotuning", "tuning", version="0.1")
        melody = util.docserver_get_filename(musicbrainzid, "makampitch", "matlab", version="0.6")

        mp3file = fname
        output = tempfile.mkdtemp()
        
        proc = subprocess.Popen(["/srv/dunya/alignAudioScore %s %s '' %s %s %s %s %s %s" % (symbtrtxt, metadata, mp3file, melody, tonic, tempo, tuning, output)], stdout=subprocess.PIPE, shell=True, env=subprocess_env)
        (out, err) = proc.communicate()
        
        ret = {}
        for f in sorted(os.listdir(output)):
            if os.path.isfile(os.path.join(output, f + '.json')):
                json_file = open(os.path.join(output, f + '.json'))
                ret['notesalign'] = json_file.read()
                json_file.close()
                os.remove(os.path.join(output, f + '.json'))
        os.rmdir(output)

        return ret
