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

import compmusic.extractors
import subprocess

import tempfile
import os
import wave

class Mp3ToWav(compmusic.extractors.ExtractorModule):
    _version = "0.5"
    _sourcetype = "mp3"
    _slug = "wav"

    _output = {"wave": {"extension": "wav", "mimetype": "audio/wave"},
                  "length": {"extension": "dat", "mimetype": "text/plain"}
                 }

    def run(self, fname):
        fp, tmpname = tempfile.mkstemp(".wav")
        os.close(fp)
        proclist = ["lame", "--decode", fname, tmpname]
        p = subprocess.Popen(proclist)
        p.communicate()

        wfile = wave.open(tmpname, "rb")
        length = wfile.getnframes() * 1.0 / wfile.getframerate()
        wfile.close()
        contents = open(tmpname, "rb").read()
        os.unlink(tmpname)
        return {"wave": contents, "length": str(int(length))}
