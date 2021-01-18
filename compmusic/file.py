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

import logging
import os

import eyed3
import eyed3.mp3

try:
    eyed3.utils.log.log.setLevel(logging.ERROR)
except AttributeError:
    eyed3.log.setLevel("ERROR")


def get_coverart(fname):
    """Get the embedded coverart, or None.
    Currently returns the first found coverart."""
    audfile = eyed3.load(fname)
    images = audfile.tag.frame_set.get(b"APIC", [])
    if images:
        for i in images:
            if i.picture_type == i.FRONT_COVER:
                return i.image_data
        return images[0].image_data
    else:
        return None


def is_mp3_file(fname):
    return os.path.isfile(fname) and fname.lower().endswith(".mp3")


def _mb_id(tag, key):
    texttags = tag.frame_set.get(b"TXXX", [])
    tags = [t for t in texttags if t.description == key]
    if len(tags):
        return tags[0].text
    else:
        return None


def mb_release_id(tag):
    """Return the Musicbrainz release ID in an eyed3 tag"""
    return _mb_id(tag, "MusicBrainz Album Id")


def mb_artist_id(tag):
    return _mb_id(tag, "MusicBrainz Artist Id")


def mb_recording_id(tag):
    ids = list(tag.unique_file_ids)

    for i in ids:
        if i.owner_id == b"http://musicbrainz.org":
            d = i.data.split(b"\0")
            mbid = d[-1]
            if not isinstance(mbid, str):
                mbid = str(mbid)
            return mbid
    return None


def file_metadata(fname):
    """ Get the file metadata for an mp3 file.
    The argument is expected to be an mp3 file. No checking is done
    """
    # We load the file directly instead of using .load() because
    # load calls magic(), which is not threadsafe.
    audfile = eyed3.mp3.Mp3AudioFile(fname)
    if not audfile or not audfile.tag:
        return None
    duration = audfile.info.time_secs
    artist = audfile.tag.artist
    title = audfile.tag.title
    release = audfile.tag.album

    releaseid = mb_release_id(audfile.tag)
    # TODO: Album release artist.
    # TODO: If there are 2 artists, the tags are separated by '; '
    # TODO: In id3 2.4 it's a \0
    artistid = mb_artist_id(audfile.tag)
    recordingid = mb_recording_id(audfile.tag)
    return {"file": fname,
            "duration": duration,
            "meta": {"artist": artist,
                     "title": title,
                     "release": release,
                     "releaseid": releaseid,
                     "artistid": artistid,
                     "recordingid": recordingid
                     }
            }
