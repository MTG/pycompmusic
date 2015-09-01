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
import numpy as np

import essentia.standard
import subprocess

import tempfile
import os
from docserver import util
import yaml
import json

from compmusic import dunya
#from compmusic import hindustani
import hindustani
from compmusic.dunya import carnatic
import requests
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

class TonicExtract(compmusic.extractors.ExtractorModule):
    __version__ = "0.2"
    __sourcetype__ = "mp3"
    __slug__ = "tonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def run(self, fname):
        audio = essentia.standard.MonoLoader(filename=fname)()
        tonic = essentia.standard.TonicIndianArtMusic()(audio)

        return {"tonic": str(tonic)}

class CTonicExtract(compmusic.extractors.ExtractorModule):
    __version__ = "0.3"
    __sourcetype__ = "mp3"
    __slug__ = "ctonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def get_from_file(self, mbid):
        data_root = "/mnt/compmusic/incoming/derived/annotations"
        mbidfile = os.path.join(data_root, "%s.yaml" % mbid)
        if os.path.exists(mbidfile):
            ydata = yaml.load(open(mbidfile))
            tonic = ydata.get("tonic", {}).get("votedValue", None)
            return tonic
        return None

#    def run(self, fname):
#
#        yamltonic = self.get_from_file(self.musicbrainz_id)
#        if yamltonic:
#            print "Got tonic from a yaml file"
#            tonic = yamltonic
#        else:
#            print "Need to calculate the tonic from scratch"
#            wavfname = util.docserver_get_filename(self.musicbrainz_id, "wav", "wave")
#            proclist = ["/srv/dunya/PitchCandExt_O3", "-m", "T", "-t", "V", "-i", wavfname]
#            p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
#            output = p.communicate()
#            tonic = output[0]
#
#        return {"tonic": str(tonic)}


    def run(self, fname):
        wavfname = util.docserver_get_filename(self.musicbrainz_id, "wav", "wave")
        proclist = ["/srv/dunya/PitchCandExt_O3", "-m", "T", "-t", "V", "-i", wavfname]
        p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
        output = p.communicate()
        tonic = output[0]

        return {"tonic": str(tonic)}

class TonicVote(compmusic.extractors.ExtractorModule):
    """ Vote on tonics to filter out small errors by the tonic identification script
    """
    __version__ = "0.3"
    __sourcetype__ = "mp3"
    __slug__ = "votedtonic"

    __output__ = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    carn_colls = ["f8bf7d1e-70d2-44f6-a3cb-5a6ded00be1f", # Bootleg carnatic
            "f96e7215-b2bd-4962-b8c9-2b40c17a1ec6", # Dunya carnatic
            "a163c8f2-b75f-4655-86be-1504ea2944c2" # Carnatic CC
            ]
    hind_colls = ["213347a9-e786-4297-8551-d61788c85c80", # Hindustani
            "6adc54c6-6605-4e57-8230-b85f1de5be2b" # Hindustani CC
            ]

    def find_nearest_index(self, arr, value):
        """
        For a given value, the function finds the nearest value
        in the array and returns its index.
        :param arr: An array of numbers
        :param value: value to be looked up
        """
        arr = np.array(arr)
        index = (np.abs(arr-value)).argmin()
        return index

    def vote(self, artist_tonics, tonic):
        """ Given a list of (mbid, tonic) tonics for an artist, and another
        tonic to check, see if this tonic should be moved
        """
        data = np.array(artist_tonics)
        data = data[:, 1].astype("float")
        [n, bins] = np.histogram(data)
        max_index = np.argmax(n)
        _median = data[self.find_nearest_index(data, bins[max_index])]

        cents_diff = abs(1200*np.log2(tonic/_median))
        if cents_diff > 350:
            tonic = float(_median)

        return tonic

    def _get_tonic(self, recordingid):
        # Return the ctonic if it's been computed, otherwise the
        # regular one.
        try:
            tonic = dunya.file_for_document(recordingid, "ctonic", "tonic")
            return tonic
        except requests.exceptions.HTTPError:
            pass
        try:
            tonic = dunya.file_for_document(recordingid, "tonic", "tonic")
            return tonic
        except requests.exceptions.HTTPError:
            pass
        return None

    def get_tonics_for_artist(self, artistid):
        key = "artist-tonics-%s" % artistid
        tonics = self.get_key(key)
        if tonics:
            return json.loads(tonics)

        if tonics is None:
            recordings = self._recordings_for_artist(artistid)
            tonics = []
            for r in recordings:
                tonic = self._get_tonic(r)
                if tonic:
                    tonics.append( (r, float(tonic)) )
            self.set_key(key, json.dumps(tonics), 3600)
        return tonics

    def run(self, fname):
        artists = self._artists_for_recording(self.musicbrainz_id)

        thistonic = self._get_tonic(self.musicbrainz_id)
        if len(artists) == 1 and thistonic:
            thistonic = float(thistonic)
            aid = artists[0]

            tonics = self.get_tonics_for_artist(aid)
            voted = self.vote(tonics, thistonic)
            if voted != thistonic:
                return {"tonic": str(voted)}

        return {"tonic": str(thistonic)}

class HindustaniTonicVote(TonicVote):
    __slug__ = "hindustanivotedtonic"

    def _artists_for_recording(self, recordingid):
        recording = hindustani.models.Recording.objects.get(mbid=recordingid)
        artists = recording.release_set.get().artists.all()
        return [a.mbid for a in artists]

    def _recordings_for_artist(self, artistid):
        recordings = []
        artist = hindustani.models.Artist.objects.get(mbid=artistid)
        for r in artist.primary_concerts.all():
            for t in r.recordings.all():
                recordings.append(t.mbid)
        return recordings


class CarnaticTonicVote(TonicVote):
    __slug__ = "carnaticvotedtonic"

    def _artists_for_recording(self, recordingid):
        recording = carnatic.get_recording(recordingid)
        concertid = recording["concert"]["mbid"]
        concert = carnatic.get_concert(concertid)
        artists = concert["concert_artists"]
        return [a["mbid"] for a in artists]

    def _recordings_for_artist(self, artistid):
        recordings = []
        artist = carnatic.get_artist(artistid)
        releases = artist["concerts"]
        for r in releases:
            release = carnatic.get_concert(r["mbid"])
            tracks = release["tracks"]
            for t in tracks:
                recordings.append(t["mbid"])
        return recordings

