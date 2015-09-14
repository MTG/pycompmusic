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

class ScoreAlign(compmusic.extractors.ExtractorModule):
    __version__ = "0.2"
    __sourcetype__ = "mp3"
    __slug__ = "scorealign"

    __output__ = {
                  "test": {"extension": "dat", "mimetype": "text/plain"}
                 }

    def run(self, fname):
        server_name = socket.gethostname()
        subprocess_env = os.environ.copy()
        subprocess_env["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v85/sys/os/glnxa64" % ((server_name,)*3)
        proc = subprocess.Popen(["/srv/dunya/extractTonicTempoTuning /tmp/test/muhayyer--pesrev--devrikebir----tanburi_cemil_bey.txt /tmp/test/132_Muhayyer_Pesrev__Mansur_Ney_.mp3 /tmp/test/predominantMelody.mat"], stdout=subprocess.PIPE, shell=True, env=subprocess_env)
        (out, err) = proc.communicate()
        return {"test": out}
