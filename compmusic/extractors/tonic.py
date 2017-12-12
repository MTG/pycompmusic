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

import json
import os
import subprocess

import essentia.standard
import numpy as np
import yaml
from docserver import util

import compmusic.extractors
from compmusic import dunya
from compmusic.dunya import carnatic
from compmusic.dunya import hindustani

dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")


class TonicExtract(compmusic.extractors.ExtractorModule):
    _version = "0.2"
    _sourcetype = "mp3"
    _slug = "tonic"

    _output = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def run(self, musicbrainzid, fname):
        audio = essentia.standard.MonoLoader(filename=fname)()
        tonic = essentia.standard.TonicIndianArtMusic()(audio)

        return {"tonic": str(tonic)}


class CTonicExtract(compmusic.extractors.ExtractorModule):
    _version = "0.3"
    _sourcetype = "mp3"
    _slug = "ctonic"

    _output = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def get_from_file(self, mbid):
        data_root = "/mnt/compmusic/incoming/derived/annotations"
        mbidfile = os.path.join(data_root, "%s.yaml" % mbid)
        if os.path.exists(mbidfile):
            ydata = yaml.load(open(mbidfile))
            tonic = ydata.get("tonic", {}).get("votedValue", None)
            return tonic
        return None

    def run(self, musicbrainzid, fname):
        wavfname = util.docserver_get_filename(musicbrainzid, "wav", "wave")
        proclist = ["/srv/dunya/PitchCandExt_O3", "-m", "T", "-t", "V", "-i", wavfname]
        p = subprocess.Popen(proclist, stdout=subprocess.PIPE)
        output = p.communicate()
        tonic = output[0]

        return {"tonic": str(tonic)}


class TonicVote(compmusic.extractors.ExtractorModule):
    """ Vote on tonics to filter out small errors by the tonic identification script
    """
    _sourcetype = "mp3"

    _output = {"tonic": {"extension": "dat", "mimetype": "text/plain"}}

    def find_nearest_index(self, arr, value):
        """
        For a given value, the function finds the nearest value
        in the array and returns its index.
        :param arr: An array of numbers
        :param value: value to be looked up
        """
        arr = np.array(arr)
        index = (np.abs(arr - value)).argmin()
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

        cents_diff = abs(1200 * np.log2(tonic / _median))
        if cents_diff > 350:
            tonic = float(_median)

        return tonic

    def _get_tonic(self, recordingid):
        # Return the ctonic if it's been computed, otherwise the
        # regular one.
        try:
            tonic = dunya.file_for_document(recordingid, "ctonic", "tonic")
            return tonic
        except dunya.HTTPError:
            pass
        try:
            tonic = dunya.file_for_document(recordingid, "tonic", "tonic")
            return tonic
        except dunya.HTTPError:
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
                    tonics.append((r, float(tonic)))
            self.set_key(key, json.dumps(tonics), 3600)
        return tonics

    def run(self, musicbrainzid, fname):
        artists = self._artists_for_recording(musicbrainzid)

        thistonic = self._get_tonic(musicbrainzid)
        if len(artists) == 1 and thistonic:
            thistonic = float(thistonic)
            aid = artists[0]

            tonics = self.get_tonics_for_artist(aid)
            voted = self.vote(tonics, thistonic)
            if voted != thistonic:
                return {"tonic": str(voted)}

        return {"tonic": str(thistonic)}


class HindustaniTonicVote(TonicVote):
    _slug = "hindustanivotedtonic"
    _version = "0.1"

    def _artists_for_recording(self, recordingid):
        recording = hindustani.get_recording(recordingid)
        release = recording.get("release")
        if release:
            release = hindustani.get_release(release[0]["mbid"])
            artists = release["release_artists"]
            return [a["mbid"] for a in artists]
        else:
            return []

    def _recordings_for_artist(self, artistid):
        recordings = []
        artist = hindustani.get_artist(artistid)
        releases = artist["releases"]
        for r in releases:
            release = hindustani.get_release(r["mbid"])
            tracks = release["recordings"]
            for t in tracks:
                recordings.append(t["mbid"])
        return recordings


class CarnaticTonicVote(TonicVote):
    _slug = "carnaticvotedtonic"
    _version = "0.1"

    def _artists_for_recording(self, recordingid):
        recording = carnatic.get_recording(recordingid)
        concert = recording.get("concert")
        if concert:
            concertid = concert[0]["mbid"]
            concert = carnatic.get_concert(concertid)
            artists = concert["concert_artists"]
            return [a["mbid"] for a in artists]
        else:
            return []

    def _recordings_for_artist(self, artistid):
        recordings = []
        artist = carnatic.get_artist(artistid)
        releases = artist["concerts"]
        for r in releases:
            release = carnatic.get_concert(r["mbid"])
            relrecs = release["recordings"]
            for t in relrecs:
                recordings.append(t["mbid"])
        return recordings
