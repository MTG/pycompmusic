#!/usr/bin/env python

import sys
import os
import argparse

import compmusic.file
import compmusic.musicbrainz
import musicbrainzngs as mb

import eyed3
import logging
eyed3.utils.log.log.setLevel(logging.ERROR)

def is_mp3_file(fname):
    return os.path.isfile(fname) and fname.lower().endswith(".mp3")

def duration_of_release(releasedir):
    duration = 0
    for fname in os.listdir(releasedir):
        fpath = os.path.join(releasedir, fname)
        if is_mp3_file(fpath):
            meta = compmusic.file.file_metadata(fpath)
            duration += meta["duration"]
    return duration

def work_stats_for_recording(recordingid):
    """ Given a recording id, get its work (if it exists) and
        the composer and lyricist of the work """
    recording = mb.get_recording_by_id(recordingid, includes=["work-rels"]) 


    work = mb.get_work_by_id(workid, includes=["artist-rels"])

def format_seconds(secs):
    seconds = secs % 60
    minutes = (secs / 60) % 60
    hours = secs / 60 / 60
    ret = ""
    if hours > 0:
        ret += "%d:" % hours
    ret += "%d:%d" % (minutes, seconds)
    return ret

def main(collectionid, colldir):
    artist_set = set()
    composer_set = set()
    lyricist_set = set()
    release_set = set()
    recording_set = set()
    duration = 0

    num_releases = 0
    for root, dirs, files in os.walk(colldir):
        if len(files):
            num_releases += 1
            duration += duration_of_release(root)
    print num_releases, "total releases"
    print "duration", format_seconds(duration)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("col", help="MBID of the collection")
    p.add_argument("dir", help="Directory to get stats from")
    args = p.parse_args()
    if args.col and args.dir:
        main(args.col, args.dir)
