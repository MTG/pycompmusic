# -*- coding: utf-8 -*-
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
import urllib2
import urllib
import cookielib
import json
from musicbrainzngs import compat
from musicbrainzngs import musicbrainz

domain = 'http://reosarevok.mbsandbox.org'
retrieve_url = '/ws/js/release/%s?inc=rels'
edit_url = '/ws/js/edit/create'
medium_url = '/ws/js/medium/%d?inc=recordings%%2Brels'
login_uri = "/login"
username = 'Reosarevok'
password = 'mb'

def update_lenghts(release_mbid, lengths_dic):
    global domain, retrieve_url, medium_url, login_uri
    release_url = retrieve_url % release_mbid
    
    print "****        Update Process started        *****"
    print ""
    print "**** Getting release information from MB  *****"

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    opener.addheaders = [('Accept', 'application/json, text/javascript')]
    response = opener.open(domain + release_url)
    response_json = response.read()

    print ""
    print "**** Getting mediums information from MB  *****"
    
    release = json.loads(response_json)
    edits = []
    for m in release['mediums']:
        response = opener.open(domain + (medium_url % m['id']))
        medium = json.loads(response.read())
        
        tracks = []
        for t in medium['tracks']:
            length = None
            if t['recording']['gid'] in lengths_dic:
                length = lengths_dic[t['recording']['gid']]
            artists = []
            for a in t['artistCredit']:
                artists.append({
                    'artist': { 
                        'gid': a['artist']['gid'],
                        'id': a['artist']['id'],
                        'name': a['artist']['name']
                    },
                    'join_phrase': a['joinPhrase'],
                    'name': a['artist']['name']
                })
            tracks.append({
                'artist_credit': { 
                    'names': artists
                },
                'id': t['id'],
                'is_data_track': t['isDataTrack'],
                'length': length,
                'name': t['name'],
                'number': t['number'],
                'position': t['position'],
                'recording_gid': t['recording']['gid'] 
            })
        edits.append({"edit_type": 52, "to_edit": m['id'], "tracklist": tracks})
    
    print ""
    print "********  Getting session Id from MB   ********"
    
    session = get_session_id()
    
    # make update
    data = {"editNote": "", "edits": edits, "makeVotable": False} 

    request = urllib2.Request(domain + edit_url, data=json.dumps(data) )
    request.add_header("Content-Type",'application/json')
    request.add_header("Cookie",'musicbrainz_server_session=' + session)
    
    try: 
        print ""
        print "*******       Editting MB lengths      ********"

        res = opener.open(request)
        print res.read()

        print ""
        print "**********   Successfully edited   ************"
        print ""
    except urllib2.HTTPError as e:
        error_message = e.read()
        print error_message
        raise e

def get_session_id():
    global username, password
    
    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
    ]
    opener_cookies = urllib2.build_opener(*handlers)
    data = {'username': username, 'password': password}
    u = urllib2.Request(domain + login_uri, urllib.urlencode(data))
    c= opener_cookies.open(u)
    for cookie in cookies:
        if cookie.name == "musicbrainz_server_session":
            return cookie.value
    return ""

if __name__ == "__main__":
    # invoke update_length method with release mbid and dict of tracks and lengths
    update_lenghts('c901447d-f986-489e-9a2b-1d42958aa05a', {'887b01f3-3b1d-473e-b334-cd5c38c69684':1000})
