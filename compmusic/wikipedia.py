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
import functools32

def _make_wp_query(params):
    url = "http://en.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'CompMusic-bot (http://compmusic.upf.edu)'}
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

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
        Only works on Musical artist or Instrument infoboxes
    """
    for node in tree.nodes:
        if hasattr(node, "name"):
            name = node.name.strip()
            if name.startswith("Infobox musical artist") or \
                    name.startswith("Infobox instrument"):
                img = node.get("image")
                if img:
                    return img.value.strip()
    return None

def parse_node(node):
    """ Parse a node. If it's a template that's a language, return
    the language. Otherwise remove the template.
    Also remove <tags> and [[]] from links.
    """
    if isinstance(node, mwparserfromhell.nodes.template.Template):
        if node.name.startswith("lang"):
            return str(node.get(1))
        else:
            return ""
    elif isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
        if node.title.startswith("File:") or node.title.startswith("Image:"):
            return ""
        return str(node.title)
    else:
        return str(node)

def _get_introduction_from_tree(tree):
    """ Get the text of the first section of an article """
    nodes = [parse_node(n) for n in tree.get_sections()[0].nodes]
    return "".join(nodes).strip()

@functools32.lru_cache(100)
def get_artist_details(name):
    article = load_article(name)
    if not article:
        return None, None, None, None
    img = _get_image_from_tree(article)
    if img:
        img_contents = download_image(img)
    else:
        img_contents = None
    intro = _get_introduction_from_tree(article)
    url = "http://en.wikipedia.org/wiki/%s" % name.replace(" ", "_")
    return img_contents, img, intro, url

def search(title):
    """ Perform a title search and return the first matching page """
    args = {"format": "json", "action": "query", "list": "search", "srsearch": title}
    data = _make_wp_query(args)
    results = data["query"]["search"]
    if len(results):
        title = results[0]["title"]
        return title
    return None

