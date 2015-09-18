# -*- coding: utf-8 -*-
__author__ = 'sertansenturk'
import os
import csv
import json
from math import floor
import numpy

class Metadata(compmusic.extractors.ExtractorModule):
    _version = "0.1"
    _sourcetype = "txt"
    _slug = "metadata"

    _output = {
         "metadata": {"extension": "json", "mimetype": "application/json" }
         }

    def run(self, musicbrainzid, fname):
        return extract(fname)

def extract(scorefile, useMusicBrainz = False):
    # get the metadata in the score name, works if the name of the 
    # file has not been changed
    metadata = dict()
    try:
        symbtrname = os.path.splitext(os.path.basename(scorefile))[0]
        [metadata['makam'], metadata['form'], metadata['usul'], metadata['name'], 
        metadata['composer']] = symbtrname.split('--')

        if isinstance(metadata['composer'], list):
            print 'The SymbTr name is not "makam--form--usul--name--composer"'
            metadata = dict()
    except ValueError:
        print 'The SymbTr name is not "makam--form--usul--name--composer"'
        
    # get the extension to determine the SymbTr-score format
    extension = os.path.splitext(scorefile)[1]

    if extension == ".txt":
        metadata['sections'] = extractSectionFromTxt(scorefile)
    elif extension == ".xml":
        metadata['sections'] = extractSectionFromXML(scorefile)
    elif extension == ".mu2":
        metadata['sections'] = extractSectionFromMu2(scorefile)
    else:
        print "Unknown format"
        return -1

    if useMusicBrainz:
        extractSectionFromMusicBrainz

    return json.dumps(metadata)



def extractSectionFromTxt(scorefile):
    structure_labels = {"structure": ["ARANA\u011eME", "TESL\u0130M", "1. HANE", "2. HANE", "KARAR", "3. HANE", "4. HANE", "M\u00dcL\u00c2Z\u0130ME", "TESL\u0130M", "2. HANEYE", "3. HANEYE", 
        "4. HANEYE", "2. HANE VE TESL\u0130M", "1. HANE VE M\u00dcL\u00c2Z\u0130ME", "TESL\u0130M", "4. HANE", "TERENN\u00dcM", "SESLERLE N\u0130NN\u0130", 
        "K\u00dc\u015eAT", "G\u0130R\u0130\u015e SAZI", "SERH\u00c2NE", "H\u00c2NE-\u0130 S\u00c2N\u0130", "H\u00c2NE-\u0130 S\u00c2L\u0130S", 
        "G\u0130R\u0130\u015e",  "3. HANE", "2. HANE", "1. HANE", "SON HANE", "SERHANE", "R\u0130TM", "II.", "I.", "G\u0130R\u0130\u015e VE ARA SAZI", 
        "ARA SAZI", "OYUN KISMI", "ORTA HANE", "M\u00dcZ\u0130K (Y\u00dcR\u00dcK)", "F\u0130NAL", "5. HANE" ],
        "timing": [ "A\u011eIRLAMA", "A\u011eIR", "A\u011eIRLA\u015eARAK", "YAVA\u015eLAYARAK", "D\u00d6N\u00dc\u015eTE YAVA\u015eLAYARAK", "CANLI OLARAK", "SERBEST"], 
        "instrumentation": ["SAZ","DAVUL", "BANDO"]
    }
    structure_labels = [l for sub_list in structure_labels.values() for l in sub_list ]

    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')
        comma_col = header.index('Koma53')
        dur_col = header.index('Ms')

        lyrics = []
        offset = []
        comma = []
        dur = []
        for row in reader:
            lyrics.append(row[lyrics_col].decode('utf-8'))
            offset.append(float(row[offset_col]))
            comma.append(int(row[comma_col]))
            dur.append(int(row[dur_col]))

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
            if isFirstNote(o):
                # this row is an annotation comment
                if i+1 in measure_start or i+1 in measure_blacklist:
                    measure_blacklist.append(i)
                else:
                    measure_start.append(i)
        measure_start.append(1) # 1st note always starts the measure
        measure_start = measure_start[::-1] # flip the list

        # note the explicit structures
        for i, l in enumerate(lyrics):
            if l in structure_labels:
                sections.append({'name':l, 'startNote':i+1, 'endNote':[]})

        # get the section from the spaces in the lyrics line
        real_lyrics_idx = []
        for i, l in enumerate(lyrics):
            if '  ' in l:
                sections.append({'name':"LYRICS_SECTION", 'startNote':[], 'endNote':i+1})
            # note the actual lyrics from other information in the lyrics column
            if not (l in structure_labels or l in ['.', '', ' ']):
                real_lyrics_idx.append(i)

        # from lyrics_end estimate the end of the lyrics line
        startNotes = [s['startNote'] for s in sections]
        startNotes.append(len(lyrics)+1) # the last note + 1 to close the last section
        endNotes = [s['endNote'] for s in sections]
        endNotes.append(0) # the zeroth note 
        for se in reversed(sections): # start from the last lyrics section
            if se['name'] == 'LYRICS_SECTION':
                # find the next closest start
                # since we start from the end, the first lyrics section we check  
                # cannot be before another; hence the first section we will find
                # will not have an ambiguous/empy startNote
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
                    # The section starts on the first measure the lyrics start again
                    nextLyricsStart = min(x for x in real_lyrics_idx if x > prevClosestEnd)
                    nextLyricsOffset = floor(offset[nextLyricsStart-1])
                    # check if nextLyricsStart and prevClosestEnd are in the same 
                    # measure. Ideally it shouldn't happen
                    if floor(offset[nextLyricsStart-1]) == floor(offset[prevClosestEnd-1]):
                        print "    " + str(floor(offset[nextLyricsStart-1])) + ': ' + lyrics[prevClosestEnd] + ' and ' + lyrics[nextLyricsStart] + ' are in the same measure! Putting the start to the next measure...'
                        nextLyricsOffset = nextLyricsOffset + 1 
                elif prevClosestEnd < prevClosestStart:
                    # at this point only the non-vocal sections have a start
                    # thus the current lyrics section is next to one of these
                    # The section starts on the first measure the lyrics start again
                    nextLyricsStart = min(x for x in real_lyrics_idx if x > prevClosestStart)
                    nextLyricsOffset = floor(offset[nextLyricsStart-1])
                else:
                    print "    No section information is available in the score"
                    return []

                # do inexact integer matching
                dist = [abs(o - nextLyricsOffset) for o in offset]
                se['startNote'] = dist.index(min(dist)) + 1

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
            if s['startNote'] not in measure_start and s['name'] not in ['SAZ', 'KARAR']:
                print "    " + str(s['startNote']) + ', ' + s['name'] + ' does not start on a measure: ' + str(offset[s['startNote']-1])

        # sort the sections
        sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] for s in sections]), key=lambda x:x[1])]
        sections = [sections[s] for s in sortIdx]

    return sections

def extractSectionFromXML(scorefile):
    pass

def extractSectionFromMu2(scorefile):
    pass

def extractSectionFromMusicBrainz(scorefile):
    pass

def isFirstNote(offset):
    # the last note of each measure is an integer. Since integer check in
    # floating point math can be inexact, we accept +- 0.001 
    return abs(offset - round(offset)) * 1000.0 < 1.0

def refineSections(sections):
    # TODO
    return sections
