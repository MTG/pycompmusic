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

'''
This script generates links for adding attributes to MB works, extracted from 
the recordings tags.
'''

import urllib2
import urllib
import json
import cookielib
import re
import sys

import compmusic
import musicbrainzngs as mb
mb.set_useragent("Dunya", "0.1")
mb.set_rate_limit(True)
mb.set_hostname("musicbrainz.org")

domain = "https://musicbrainz.org"
password = '####'
username = '####'
login_url = '/login'
work_url = '/work/%s/edit'

auth_token = "###"
symbtrmu2_url = 'http://dunya.compmusic.upf.edu/document/by-id/%s/symbtrmu2'
dunya_fuzzy_url = 'http://dunya.compmusic.upf.edu/api/makam/fuzzy'

mb_cache = {}
count_missing_mu2 = 0
count_matched_mu2 = 0
count_missing_dunya = 0


def get_symbtrmu2(work_mbid):
    # Get symbtrmu2 file and extract makam, form and usul
    global symbtrmu2_url
    file_url = symbtrmu2_url % work_mbid
    
    # 50 -> Makam
    # 51 -> Usul
    # 57 -> Form
    data = {"50": None, "51": None, "57": None}
    try:
        response = urllib2.urlopen(file_url)
        document = response.read()
        for line in document.splitlines():
            info = line.decode('iso8859-9').split("\t")
            if info[0] in data.keys():
                data[info[0]] = info[7]
    except:
        print("There is no mu2 file for work: %s" % work_mbid)
    return {"makam": data["50"], "usul": data["51"], "form": data["57"]}

def get_mb_recording(collection_mbid, output_file):
    global symbtrmu2_url, count_matched_mu2, count_missing_mu2, count_missing_dunya
    # Get the collection from musicbrainz and extract the recordings
    print("Retrieving information from mb collection: %s" % collection_mbid)
    res = {"mu2": [], "mb": []}

    rec_list = []
    collection = mb.get_releases_in_collection(collection_mbid)
    for rel in collection["collection"]["release-list"]:
        rel_mb =  mb.get_release_by_id(rel['id'], includes=["recordings"])
        for i in rel_mb["release"]["medium-list"]:
            for track in i["track-list"]:
                rec = track['recording']['id']
                if rec not in rec_list:
                    rec_list.append(rec)

    # Get the recording from musicbrainz and extract makam, form and usul
    for rec_mbid in rec_list:
        work_rels = mb.get_recording_by_id(rec_mbid, includes=["tags", "work-rels"])
        rec_tags = []
        if "tag-list" in work_rels["recording"]:
            rec_tags = work_rels["recording"]["tag-list"]

        works = []
        if "work-relation-list" in work_rels["recording"]:
            works = work_rels["recording"]["work-relation-list"]
        for w in works:
            print("Extracting work information from MB: %s" %  w["work"]["id"])
            
            work_tags = []
            work = mb.get_work_by_id(w["work"]["id"], includes=["tags", "artist-rels"])
            if "tag-list" in work["work"]:
                work_tags = work["work"]["tag-list"] 
            
            mu2 = get_symbtrmu2(work["work"]["id"])
            title = work["work"]["title"].encode("utf-8")

            # get alias for each tag 
            try:
                rec_makam, rec_usul, rec_form = get_tags(rec_tags)
                work_makam, work_usul, work_form = get_tags(work_tags)
                mu2_makam = get_fuzzy("makam", mu2["makam"])
                mu2_form = get_fuzzy("form", mu2["form"])
                mu2_usul = get_fuzzy("usul", mu2["usul"])

                # compare results of 3 sources
                makam, usul, form = (None, None, None)
                if mu2_makam and mu2_usul and mu2_form:
                    #There is mu2 file with makam usul and form
                    count_matched_mu2 += 1

                    if mu2_makam == rec_makam and mu2_usul == rec_usul and mu2_form == rec_form:
                        if work_makam == rec_makam and work_usul == rec_usul and work_form == rec_form:
                            makam = work_makam
                            usul = work_usul
                            form = work_form
                        elif not work_makam and not work_usul and not work_form:
                            # If mb work has no tag we only consider information from mu2 and mb recording
                            makam = rec_makam
                            usul = rec_usul
                            form = rec_form
                    else:
                        print("There's a difference between mu2 file and mb recording information.")
                        print("Recording form: %s usul: %s makam: %s" % (rec_form, rec_usul, rec_makam))
                        print("Mu2 form: %s usul: %s makam: %s" % (mu2_form, mu2_usul, mu2_makam))

                    if makam and usul and form:
                        try:
                            new_link = update_mb_work(work["work"]["id"], title, makam, form, usul, symbtrmu2_url % work["work"]["id"])
                            if new_link:
                                res['mu2'].append(new_link)
                        except ElementNotFoundException as e:
                            print("Couldn't generate link because element not present in MB")

                elif (not work_makam and not work_usul and not work_form) or \
                        (work_makam == rec_makam and work_usul == rec_usul and work_form == rec_form):
                    # If theres no mu2 file we only consider mb information
                    count_missing_mu2 += 1
                    if rec_makam and rec_usul and rec_form:
                        try:
                            new_link = update_mb_work(work["work"]["id"], title, rec_makam, rec_form, rec_usul, None)
                            res['mb'].append(new_link)
                        except ElementNotFoundException as e:
                            print("Couldn't generate link because element not present in MB")

            except AliasNotFoundException as e:
                count_missing_dunya += 1
                print("Skipping work because alias not found on Dunya")

    with open(output_file, "a+") as append_file:
        append_file.write("<h1> List of links generated from MU2 files information </h1>")
        for i in res['mu2']:
            append_file.write(i)
        append_file.write("<h1> List of links generated from recording tags </h1>")
        for i in res['mb']:
            append_file.write(i)

    print("Completed with missing mu2 files: %d, matched mu2 files: %d, missing on dunya: %d" % \
            (count_missing_mu2, count_matched_mu2, count_missing_dunya))

def get_tags(tags):
    makam, usul, form = (None, None, None)
    for t in tags:
        name = t["name"].lower()
        if compmusic.tags.has_makam(name):
             makam = compmusic.tags.parse_makam(name)
             if makam:
                 makam = makam[1]
        elif compmusic.tags.has_usul(name):
             usul = compmusic.tags.parse_usul(name)
             if usul:
                 usul = usul[1]
        elif compmusic.tags.has_makam_form(name):
             form = compmusic.tags.parse_makam_form(name)
             if form:
                 form = form[1]
    return get_fuzzy("makam", makam), get_fuzzy("usul", usul), get_fuzzy("form", form)

def get_fuzzy(key, value):
    global dunya_fuzzy_url, auth_token
    if not value:
        return None
    return query_dunya_api(dunya_fuzzy_url, {key: value.encode("utf-8")}, auth_token, 'name')

def query_dunya_api(url, params, auth_token, retrieve_attr):
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [("Authorization", "Token " + auth_token)]
        response = opener.open(url + "?"+urllib.urlencode(params))
        res = json.loads(response.read())
        return res[retrieve_attr].encode('utf-8')
    except Exception as e:
        print('ERROR retrieving dunya information:')
        print(url + "?"+urllib.urlencode(params))
        raise AliasNotFoundException()

def get_session_id():
    global username, password, domain, login_url
    
    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
    ]
    opener_cookies = urllib2.build_opener(*handlers)
    data = {'username': username, 'password': password}
    u = urllib2.Request(domain + login_url, urllib.urlencode(data))
    c= opener_cookies.open(u)
    for cookie in cookies:
        if cookie.name == "musicbrainz_server_session":
            return cookie.value
    return ""

def update_mb_work(work_mbid, work_name, makam, form, usul, mu2_file):
    global domain, work_url, mb_cache, auth_token
    
    if len(mb_cache) == 0:
        print("Updating MB work %s, generating session id" % work_mbid)
        session = get_session_id()

        print("Retrieving id of makam, form and usul by parsing html ")
        request = urllib2.Request(domain + (work_url % work_mbid))
        request.add_header("Cookie",'musicbrainz_server_session=' + session)
        opener = urllib2.build_opener()
        res = opener.open(request)
        html = res.read()

        match_obj = re.search(r'.*allowedValues: (.*),\n', html)
        res_json = match_obj.group(1)
        values = json.loads(res_json)

        for i in values['children']:
            mb_cache[i['value'].encode("utf-8")] = i['id']

    makam_id, form_id, usul_id = (None, None, None)
    if makam in mb_cache:
        makam_id = mb_cache[makam]
    if form in mb_cache:
        form_id = mb_cache[form]
    if usul in mb_cache:
        usul_id = mb_cache[usul]

    if not makam_id:
        raise ElementNotFoundException("Makam %s not present in Musicbrainz" % makam)
    elif not form_id:
        raise ElementNotFoundException("Form %s not present in Musicbrainz" % form)
    elif not usul_id:
        raise ElementNotFoundException("Usul %s not present in Musicbrainz" % usul)

    # 15 -> Makam
    # 16 -> Form
    # 17 -> Usul
    data = {
        "edit-work.attributes.0.type_id": 15,
        "edit-work.attributes.0.value": makam_id,
        "edit-work.attributes.1.type_id": 16,
        "edit-work.attributes.1.value": form_id,
        "edit-work.attributes.2.type_id": 17,
        "edit-work.attributes.2.value": usul_id,
        }

    if mu2_file:
        symbtr_name = query_dunya_api(mu2_file.replace("/symbtrmu2", ""), {}, auth_token, 'title')
        data['edit-work.edit_note'] = "Makam, Form and Usul added from symbtr %s" % symbtr_name
    
    # Generate update link
    
    link_html = '<div><a href="%s">%s</a>'
    mu2_html = '<a href="%s">Mu2 file</a>'
    end_html = '</div>\n'
    gen_url = domain + (work_url % work_mbid) + "?" + urllib.urlencode(data) 
    
    print("New mb work edition link generated")
    ret = link_html % (gen_url, work_name)
    if mu2_file:
        ret = ret + mu2_html % ( mu2_file)
    ret = ret + end_html
    return ret

class AliasNotFoundException(Exception):
    pass

class ElementNotFoundException(Exception):
    pass

if __name__ == "__main__":
    coll = "544f7aec-dba6-440c-943f-103cf344efbb"
    output_file = "/tmp/generated_links.txt" 
    if len(sys.argv) > 2:
        coll = sys.argv[1]
        output_file = sys.argv[2]
    get_mb_recording(coll, output_file)
