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
    __version__ = "0.1"
    __sourcetype__ = "mp3"
    __slug__ = "scorealign"

    __output__ = {
                  "test": {"extension": "dat", "mimetype": "text/plain"}
                 }

    def run(self, fname):
        server_name = socket.gethostname()
        os.environ["XAPPLRESDIR"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/X11/app-defaults" % server_name
        os.environ["LD_LIBRARY_PATH"] = "/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/runtime/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/bin/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/sys/os/glnxa64:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/sys/java/jre/glnxa64/jre/lib/amd64/server:/mnt/compmusic/%s/MATLAB/MATLAB_Compiler_Runtime/v82/sys/java/jre/glnxa64/jre/lib/amd64" % ((server_name,) * 6)
        proc = subprocess.Popen(["/tmp/MyMCC"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        return {"test": out}
