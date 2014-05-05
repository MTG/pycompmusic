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

"""Tools to download Articles and Images from Wikipedia"""
import requests
import json
import mwparserfromhell

def _make_wp_query(params):
    url = "http://en.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'CompMusic-bot (http://compmusic.upf.edu)'}
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

def _get_extract(page):
    params = {"action": "query", "prop": "extracts", "exintro": "1",
            "format": "json", "redirects": "1", "titles": page}
    extract = _make_wp_query(params)
    pages = extract.get("query", {}).get("pages", {})
    if pages:
        key = pages.keys()[0]
        if key == "-1":
            return None
        page = pages[key]
        return page.get("extract")
    return None

def download_image(imgname):
    """ Take the name of an image on Wikipedia and return the contents of the image """
    if imgname.startswith("http://"):
        imgurl = imgname
    else:
        args = {"format": "json", "action": "query", "prop": "imageinfo", "iiprop":"url", "titles": "File:%s" % imgname}
        data = _make_wp_query(args)
        imgurl = data["query"]["pages"].values()[0]
        if "imageinfo" in imgurl:
            imgurl = imgurl["imageinfo"][0]["url"]
        else:
            return None

    headers = {'User-Agent': 'CompMusic-bot (http://compmusic.upf.edu)'}
    resp = requests.get(imgurl, headers=headers)
    return resp.content

def load_article(title):
    """ Get the structure of a wikipedia article with this title """
    args = {"format": "json", "action": "query", "prop": "revisions", "rvprop": "content", "titles": title}
    data = _make_wp_query(args)
    article = data["query"]["pages"].values()[0]
    if "revisions" in article:
        text = article["revisions"][0]["*"]
        parsed = mwparserfromhell.parse(text)
        return parsed
    else:
        return None

def _get_image_from_tree(tree):
    """ See if a document tree (from `load_article`) has an infobox with an
        image defined in it, and return the contents of the image (or none).
        Only works on Musical artist infoboxes
    """
    for node in tree.nodes:
        if hasattr(node, "name"):
            name = node.name.strip()
            if name.startswith("Infobox musical artist"):
                img = node.get("image")
                if img:
                    return img.value.strip()
    return None

def get_artist_details(name):
    article = load_article(name)
    if not article:
        return None, None
    img_url = _get_image_from_tree(article)
    if img_url:
        img_contents = download_image(img_url)
    else:
        img_contents = None
    intro = _get_extract(name)
    return img_contents, intro

def search(title):
    """ Perform a title search and return the first matching page """
    args = {"format": "json", "action": "query", "list": "search", "srsearch": title}
    data = _make_wp_query(args)
    results = data["query"]["search"]
    if len(results):
        title = results[0]["title"]
        return title
    return None

