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

import requests
import bs4
import re

def search_artist(name):
    """ Search for an artist name.
    Return a map of matching results -> artist id
    remove spaces between initials, e.g., M. S. Subbulakshmi -> M.S. Subbulakshmi
    """
    # Replace a single letter + space to letter. space
    name = re.sub(r"\b([A-Za-z]) ", r"\1. ", name)
    # Every time there's an initial, remove the space between it
    # and the next initial. Don't remove the space before the
    # last word
    name = re.sub("((?<=[A-Za-z]\.)) ([A-Za-z]\.)", r"\1\2", name)
    url = "http://kutcheris.com/directory_art.php?search=%s" % name
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.text)
    # If the search we did resulted in an exact match, Kutcheris
    # doesn't display results, but instead puts a js redirect
    # to the artist id.
    for script in b.find_all("script"):
        text = script.get_text()
        if text.startswith("window.location"):
            id = re.search(r"id=(\d+)", text)
            if id:
                return {name: id.group(1)}
    directory = b.find("div", id="directory_area")
    ret = {}
    for link in directory.find_all("a"):
        name = link.get_text()
        url = link.get("href")
        id = url.replace("artist.php?id=", "")
        ret[name] = id
    return ret

def get_artist_details(artistid):
    url = "http://kutcheris.com/artist.php?id=%s" % artistid
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.text)
    profile = b.find("div", id="profile")
    img = profile.find("img")
    imgurl = img.get("src")
    if "temp.gif" in imgurl:
        imgurl = None
        imagecontents = None
    else:
        imgurl = "http://kutcheris.com/%s" % imgurl
        imagecontents = requests.get(imgurl).content

    text = profile.find("div", id="right")
    wplink = text.find("a", href=re.compile(r".*?wikipedia\.org.*?"))
    if wplink:
        wikipedia = wplink.get("href")
    else:
        wikipedia = None
    bio = text.get_text()
    if "Read more on wikipedia." in bio:
        bio = bio.replace("Read more on wikipedia.", "")
    if "There is no profile information available" in bio:
        bio = None

    return imagecontents, bio, wikipedia

