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
import pdb

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

    score = readTxtScore(scorefile)
    measure_start_idx = getMeasureStartIdx(score['offset'])
    
    sections = []
    # Check lyrics information
    if all(l == '' for l in score['lyrics']):
        # empty lyrics field; we cannot really do anything wo symbolic analysis
        sections = []
    else:
        sections = getSections(score, struct_lbl, slugify=slugify)
        sections = completeSectionStartEnds(sections, score, all_labels, 
            measure_start_idx)

        # the refine section names according to the lyrics, pitch and durations
        sections = refineSections(sections)

    validateSections(sections, score, measure_start_idx, 
        set(all_labels)- set(struct_lbl))

    # map the python indices in startNote and endNote to SymbTr index
    for se in sections:
        se['startNote'] = score['index'][se['startNote']]
        se['endNote'] = score['index'][se['endNote']]

    return sections

def extractSectionFromXML(scorefile, slugify = True):
    pass

def extractSectionFromMu2(scorefile, slugify = True):
    pass

def extractSectionFromMusicBrainz(scorefile, slugify = True):
    pass

def readTxtScore(scorefile):
    with open(scorefile, "rb") as f:
        reader = csv.reader(f, delimiter='\t')

        header = next(reader, None)

        index_col = header.index('Sira')
        code_col = header.index('Kod')
        comma_col = header.index('Koma53')
        duration_col = header.index('Ms')
        lyrics_col = header.index('Soz1')
        offset_col = header.index('Offset')

        score = {'index': [], 'code': [], 'comma': [], 'duration': [],
                'lyrics': [], 'offset': []}
        for row in reader:
            score['index'].append(int(row[index_col]))
            score['code'].append(int(row[code_col]))
            score['comma'].append(int(row[comma_col]))
            score['duration'].append(int(row[duration_col]))
            score['lyrics'].append(row[lyrics_col].decode('utf-8'))
            score['offset'].append(float(row[offset_col]))

    # shift offset such that the first note of each measure has an integer offset
    score['offset'].insert(0, 0)
    score['offset'] = score['offset'][:-1]

    return score

def getMeasureStartIdx(offset):
    measure_start_idx = []

    tol = 0.001
    for int_offset in range(0, int(max(offset))+1):
        measure_start_idx.append(min(i for i, o in enumerate(offset) 
            if o > int_offset - tol))

    if not all(integerOffset(offset[i]) for i in measure_start_idx):
        print "    " + "Some measures are skipped by the offsets"
    
    return measure_start_idx

def integerOffset(offset):
    # The measure changes when the offset is an integer
    # (Note that offset was shifted by one earlier for asier processing )
    # Since integer check in floating point math can be inexact,
    # we accept +- 0.001 
    return abs(offset - round(offset)) * 1000.0 < 1.0

def getSections(score, struct_lbl, slugify=True):
    sections = []
    for i, l in enumerate(score['lyrics']):
        if l in struct_lbl: # note the explicit structures
            sections.append({'name':slugify_tr(l) if slugify else l, 
                'startNote':i, 'endNote':[]})
        elif '  ' in l: # lyrics end marker
            sections.append({'name':"LYRICS_SECTION", 'startNote':[], 
                'endNote':i})
    return sections
     
def getRealLyricsIdx(lyrics, all_labels, dur):
    # separate the actual lyrics from other information in the lyrics column
    real_lyrics_idx = []
    for i, l in enumerate(lyrics):  
        # annotation/control rows, embellishments (rows w dur = 0) are ignored
        if not (l in all_labels  or l in ['.', '', ' '] or dur[i] == 0):
            real_lyrics_idx.append(i)
    return real_lyrics_idx

def completeSectionStartEnds(sections, score, struct_lbl, measure_start_idx):
    real_lyrics_idx = getRealLyricsIdx(score['lyrics'], struct_lbl, score['duration'])

    startNoteIdx = [s['startNote'] for s in sections] + [len(score['lyrics'])]
    endNoteIdx = [-1] + [s['endNote'] for s in sections]
    for se in reversed(sections): # start from the last section
        #print se['name'] + ' ' + str(se['startNote']) + ' ' + str(se['endNote'])

        if se['name'] == 'LYRICS_SECTION':
            # carry the 'endNote' to the next closest start
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['endNote']) - 1
            
            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

            # estimate the start of the lyrics sections
            try: # find the previous closest start
                prevClosestStartInd = max(x for x in startNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no section label in lyrics columns
                prevClosestStartInd = -1

            try: # find the previous closest end
                prevClosestEndInd = max(x for x in endNoteIdx 
                    if x < se['endNote'])
            except ValueError: # no vocal sections
                prevClosestEndInd = -1

            # find where the lyrics of this section starts
            chkInd = max([prevClosestEndInd, prevClosestStartInd])
            nextLyricsStartInd = min(x for x in real_lyrics_idx if x > chkInd)
            nextLyricsOffset = floor(score['offset'][nextLyricsStartInd])

            # check if nextLyricsStartInd and prevClosestEndInd are in the 
            # same measure. Ideally they should be in different measures
            if nextLyricsOffset == floor(score['offset'][prevClosestEndInd]):
                print ("    " + str(nextLyricsOffset) + ':'
                ' ' + score['lyrics'][prevClosestEndInd] + ' and' 
                ' ' + score['lyrics'][nextLyricsStartInd] + ' '
                'are in the same measure!')

                se['startNote'] = nextLyricsStartInd
            else: # The section starts on the first measure the lyrics start
                se['startNote'] = getOffsetStartIdx(nextLyricsOffset, 
                    score['offset'], measure_start_idx)

            # update startNoteIdx
            startNoteIdx = ([s['startNote'] for s in sections] + 
                [len(score['lyrics'])])
        else:  # instrumental
            se['endNote'] = min(x for x in startNoteIdx 
                if x > se['startNote']) - 1

            # update endNoteIdx
            endNoteIdx = [-1] + [s['endNote'] for s in sections]

    # if the first note is not the startNote of a section
    # add an initial instrumental section
    if sections and not any(s['startNote'] == 0 for s in sections):
        sections.append({'name': 'INSTRUMENTAL_SECTION','startNote': 0, 
            'endNote': min([s['startNote'] for s in sections])-1})

        #print(' ' + se['name'] + ' ' + str(se['startNote']) + ' '
        #    '' + str(se['endNote']))
    return sortSections(sections)

def getOffsetStartIdx(offsetIdx, offsets, measure_start_idx):
    measure_start_offsets = [offsets[m] for m in measure_start_idx]
    # do inexact integer matching
    dist = [abs(o - offsetIdx) for o in measure_start_offsets]
    return measure_start_idx[dist.index(min(dist))]

def sortSections(sections):
    # sort the sections
    sortIdx = [i[0] for i in sorted(enumerate([s['startNote'] 
        for s in sections]),  key=lambda x:x[1])]
    return [sections[s] for s in sortIdx]

def validateSections(sections, score, measure_start_idx, ignoreLabels):
    if not sections: # check section presence
        print "    Missing section info in lyrics."
    else: # check section continuity
        ends = [-1] + [s['endNote'] for s in sections]
        starts = [s['startNote'] for s in sections] + [len(score['offset'])]
        for s, e in zip(starts, ends):
            if not s - e == 1:
                print("    " + str(e) + '->' + str(s) + ', '
                    'Gap between the sections')

    for s in sections:
        # check whether section starts on the measure or not
        if (s['startNote'] not in measure_start_idx and 
            s['name'] not in ignoreLabels):
            print("    " + str(s['startNote']) + ', ' + s['name'] + ' '
                'does not start on a measure: ' + 
                str(score['offset'][s['startNote']]))
        # check if the end of a section somehow got earlier than its start
        if s['startNote'] > s['endNote']:
            print("    " + str(s['startNote']) + '->'
                '' + str(s['endNote']) + ', ' + s['name'] + ' '
                'ends before it starts: ' + 
                str(score['offset'][s['startNote']]))

def slugify_tr(value):  
    value_slug = value.replace(u'\u0131', 'i')
    value_slug = unicodedata.normalize('NFKD', 
        value_slug).encode('ascii', 'ignore').decode('ascii')
    value_slug = re.sub('[^\w\s-]', '', value_slug).strip()
    
    return re.sub('[-\s]+', '-', value_slug)

def refineSections(sections):
    # TODO
    return sections
