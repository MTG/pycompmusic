"""Tools to download Articles and Images from Wikipedia"""
import requests
import json
import mwparserfromhell

def _make_wp_query(params):
    url = "http://en.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'CompMusic-bot (http://compmusic.upf.edu)'}
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.text)

def download_image(imgname):
    """ Take the name of an image on Wikipedia and return the contents of the image """
    args = {"format": "json", "action": "query", "prop": "imageinfo", "iiprop":"url", "titles": "File:%s" % imgname}
    data = _make_wp_query(args)
    imgurl = ["query"]["pages"]["-1"]["imageinfo"][0]["url"]

    headers = {'User-Agent': 'CompMusic-bot (http://compmusic.upf.edu)'}
    resp = requests.get(imgurl, headers=headers)
    return resp.text

def load_article(title):
    """ Get the structure of a wikipedia article with this title """
    args = {"format": "json", "action": "query", "prop": "revisions", "rvprop": "content", "titles": title}
    data = _make_wp_query(args)
    text = data["query"]["pages"].values()[0]["revisions"][0]["*"]
    parsed = mwparserfromhell.parse(text)
    return parsed

def get_image(tree):
    """ See if a document tree (from `load_article`) has an infobox with an
        image defined in it, and return the contents of the image (or none).
        Only works on Musical artist or Instrument infoboxes
    """
    for node in tree.nodes:
        if hasattr(node, "name"):
            if node.name.strip() in ("Infobox musical artist", "Infobox instrument"):
                img = node.get("image")
                if img:
                    return img.value.strip()
    return None

def get_introduction(tree):
    """ Get the text of the first section of an article """
    return tree.get_sections()[0].strip_code()

def search(title):
    """ Perform a title search and return the first matching page """
    args = {"format": "json", "action": "query", "list": "search", "srsearch": title}
    data = _make_wp_query(args)
    results = data["query"]["search"]
    if len(results):
        title = results[0]["title"]
        return title
    return None

