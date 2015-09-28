# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'
import os
import csv
import json
from math import floor
import numpy
import compmusic
import unicodedata
import re
from compmusic import dunya
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

class Metadata(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "metadata"

    _output = {
         "metadata": {"extension": "json", "mimetype": "application/json" }
         }

    def run(self, musicbrainzid, fname):
        symbtr = compmusic.dunya.makam.get_symbtr(musicbrainzid)
        symbtr_fname = symbtr['name'] + ".txt"

        return extract(fname, symbtr_fname)

def get_labels(): 
    symbtr_label_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makams_usuls', 'symbTrLabels.json')
    symbtr_label = json.load(open(symbtr_label_file, 'r'))

    return symbtr_label


def extract(scorefile, symbtrname, useMusicBrainz = False, extractAllLabels = False, 
    slugify = True):
    # get the metadata in the score name, works if the name of the 
    # file has not been changed
    symbtrdict = symbtrname.split('--')
    metadata = dict()
    try:
        [metadata['makam'], metadata['form'], metadata['usul'], metadata['name'], 
            metadata['composer']] = symbtrname.split('--')
        metadata['tonic'] = getTonic(metadata['makam'])

        if isinstance(metadata['composer'], list):
            print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
            metadata = dict()
    except ValueError:
        print 'The symbtrname is not in the form "makam--form--usul--name--composer"'
        
    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    if extension == ".txt":
        metadata['sections'] = extractSectionFromTxt(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels)
    elif extension == ".xml":
        metadata['sections'] = extractSectionFromXML(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels)
    elif extension == ".mu2":
        metadata['sections'] = extractSectionFromMu2(scorefile, slugify=slugify, 
            extractAllLabels=extractAllLabels)
    else:
        print "Unknown format"
        return -1

    if useMusicBrainz:
        extractSectionFromMusicBrainz

    return {'metadata': metadata}

def getTonic(makam):
    makam_tonic_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'makams_usuls', 'makam.json')
    makam_tonic = json.load(open(makam_tonic_file, 'r'))

    return makam_tonic[makam]['kararSymbol']

def extractSectionFromTxt(scorefile, slugify = True, extractAllLabels=False):
    all_labels = [l for sub_list in get_labels().values() for l in sub_list] 
    struct_lbl = all_labels if extractAllLabels else get_labels()['structure'] 

    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')
        comma_col = header.index('Koma53')
        dur_col = header.index('Ms')
        code_col = header.index('Sira')

        lyrics = []
        offset = []
        comma = []
        dur = []
        code = []
        for row in reader:
            lyrics.append(row[lyrics_col].decode('utf-8'))
            offset.append(float(row[offset_col]))
            comma.append(int(row[comma_col]))
            dur.append(int(row[dur_col]))
            code.append(int(row[code_col]))

    # shift offset such that the first note of each measure has an integer offset
    offset.insert(0, 0)
    offset = offset[:-1]

    sections = []
    # Check lyrics information; without it we cannot really do anything
    # unless we incorporate symbolic analysis
    if all(l == '' for l in lyrics):
        print "    Lyrics is empty. Cannot determine the sections"
    else:
        # get the measure starts
        measure_start = []
        measure_blacklist = []  # embellishments and control rows!
        for i, o in zip(xrange(len(offset), 1, -1), reversed(offset)):
            # start of measure; this row can be the measure start
            if integerOffset(o):
                # this row is an annotation comment
                if i+1 in measure_start or i+1 in measure_blacklist:
                    measure_blacklist.append(i)
                else:
                    measure_start.append(i)
        measure_start.append(1) # 1st note always starts the measure
        measure_start = measure_start[::-1] # flip the list

        # note the explicit structures
        for i, l in enumerate(lyrics):
            if l in struct_lbl:
                sections.append({'name':slugify_tr(l) if slugify else l, 
                    'startNote':i+1, 'endNote':[]})

        # get the section from the spaces in the lyrics line
        real_lyrics_idx = []
        for i, l in enumerate(lyrics):
            if '  ' in l:
                sections.append({'name':"LYRICS_SECTION", 'startNote':[], 'endNote':i+1})
                
            # note the actual lyrics from other information in the lyrics column
            # annotation/control rows, embelishments (rows w dur = 0) are ignored
            if not (l in all_labels  or l in ['.', '', ' '] or dur[i] == 0):
                real_lyrics_idx.append(i+1)

        # from lyrics_end estimate the end of the lyrics line
        startNotes = [s['startNote'] for s in sections]
        startNotes.append(len(lyrics)+1) # the last note + 1 to close the last section
        endNotes = [s['endNote'] for s in sections]
        endNotes.append(0) # the zeroth note 
        for se in reversed(sections): # start from the last lyrics section
            # print se['name'] + ' ' + str(se['startNote']) + ' ' + str(se['endNote'])
            if se['name'] == 'LYRICS_SECTION':

                # find the next closest start
                # since we start from the end, the first lyrics section we check  
                # cannot be before another; hence the first section we will find
                # will not have an ambiguous/empty startNote
                se['endNote'] = min(x for x in startNotes if x > se['endNote']) - 1

                # update endNotes
                endNotes = [s['endNote'] for s in sections]
                endNotes.append(0) # the zeroth note 

                # estimate the start of the lyrics sections
                # find the previous closest start or end
                try:
                    prevClosestStart = max(x for x in startNotes if x < se['endNote'])
                except ValueError: # no section label in lyrics columns
                    prevClosestStart = -1
                try:
                    prevClosestEnd = max(x for x in endNotes if x < se['endNote'])
                except ValueError: # no vocal sections
                    prevClosestEnd = -1

                if prevClosestEnd > prevClosestStart:
                    # at this point only the lyrics sections have a known ending
                    # thus the current lyrics section is next to another
                    nextLyricsStart = min(x for x in real_lyrics_idx if x > prevClosestEnd)
                    nextLyricsOffset = floor(offset[nextLyricsStart-1])
                    # check if nextLyricsStart and prevClosestEnd are in the same 
                    # measure. Ideally it shouldn't happen
                    if floor(offset[nextLyricsStart-1]) == floor(offset[prevClosestEnd-1]):
                        print ("    " + str(floor(offset[nextLyricsStart-1])) + ':'
                        ' ' + lyrics[prevClosestEnd] + ' and ' + lyrics[nextLyricsStart] + ' '
                        'are in the same measure!')
                        # start the section in the same measure, from the first lyrics syllable
                        # after the last end
                        se['startNote'] = nextLyricsStart

                    else: # The section starts on the first measure the lyrics start again
                        # do inexact integer matching
                        dist = [abs(o - nextLyricsOffset) for o in offset]
                        se['startNote'] = dist.index(min(dist)) + 1

                elif prevClosestEnd < prevClosestStart:
                    # at this point only the non-vocal sections have a start
                    # thus the current lyrics section is next to one of these
                    # The section starts on the first measure the lyrics start again
                    nextLyricsStart = min(x for x in real_lyrics_idx if x > prevClosestStart)
                    nextLyricsOffset = floor(offset[nextLyricsStart-1])

                    # The section starts on the first measure the lyrics start again
                    # do inexact integer matching
                    dist = [abs(o - nextLyricsOffset) for o in offset]
                    se['startNote'] = dist.index(min(dist)) + 1
                else:
                    print "    No section information is available in the score"
                    return []

                

                # update startNotes
                startNotes = [s['startNote'] for s in sections]
                startNotes.append(len(lyrics)+1) # the last note + 1 to close the last section
            else:
                break # all the lyrics sections are appended consecutively

        # start a section if there are no sections starting in note 1
        startNotes = [s['startNote'] for s in sections]
        if 1 not in startNotes:
            sections.append({'name':"Section1", 'startNote':1, 'endNote':[]})

        # close any which doesn't have a endNote
        startNotes = [s['startNote'] for s in sections]
        startNotes.append(len(lyrics)+1) # the last note + 1 to close the last section
        endNotes = [s['endNote'] for s in sections]
        for s in sections:
            if not s['endNote']:
                s['endNote'] = min(x for x in startNotes if x > s['startNote']) - 1

        # the refine section names according to the lyrics, pitch and durations
        sections = refineSections(sections)

        # warnings
        for s in sections:
            # check whether section starts on the measure or not
            if s['startNote'] not in measure_start and s['name'] not in ['SAZ', 'KARAR']:
                print("    " + str(s['startNote']) + ', ' + s['name'] + ' does '
                	'not start on a measure: ' + str(offset[s['startNote']-1]))
            # check if the end of a section somehow got earlier than its start
            if s['startNote'] > s['endNote']:
                print("    " + str(s['startNote']) + '->' + str(s['endNote']) + ''
                    ', ' + s['name'] + ' ends before it starts: ' + str(offset[s['startNote']-1]))

        # sort the sections
        sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] for s in sections]), 
            key=lambda x:x[1])]
        sections = [sections[s] for s in sortIdx]

        # check section continuity
        ends = [0] + [s['endNote'] for s in sections]
        starts = [s['startNote'] for s in sections] + [len(dur)+1]
        for s, e in zip(starts, ends):
            if not s - e == 1:
                print "    " + str(e) + '->' + str(s) + ', Gap between the sections'

    return sections

def extractSectionFromXML(scorefile, slugify = True):
    pass

def extractSectionFromMu2(scorefile, slugify = True):
    pass

def extractSectionFromMusicBrainz(scorefile, slugify = True):
    pass

def integerOffset(offset):
    # The measure changes when the offset is an integer
    # (Note that offset was shifted by one earlier for asier processing )
    # Since integer check in floating point math can be inexact,
    # we accept +- 0.001 
    return abs(offset - round(offset)) * 1000.0 < 1.0

def slugify_tr(value):  
    value_slug = value.replace(u'\u0131', 'i')
    value_slug = unicodedata.normalize('NFKD', value_slug).encode('ascii', 'ignore').decode('ascii')
    value_slug = re.sub('[^\w\s-]', '', value_slug).strip()
    
    return re.sub('[-\s]+', '-', value_slug)

def refineSections(sections):
    # TODO
    return sections
