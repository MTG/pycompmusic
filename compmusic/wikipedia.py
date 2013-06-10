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
    if imgname.startswith("http://"):
        imgurl = imgname
    else:
        args = {"format": "json", "action": "query", "prop": "imageinfo", "iiprop":"url", "titles": "File:%s" % imgname}
        data = _make_wp_query(args)
        imgurl = data["query"]["pages"]["-1"]
        if "imageinfo" in imgurl:
            imgurl = ["imageinfo"][0]["url"]
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

def _get_introduction_from_tree(tree):
    """ Get the text of the first section of an article """
    return tree.get_sections()[0].strip_code()

def get_artist_details(name):
    article = load_article(name)
    if not article:
        return None, None, None
    img = _get_image_from_tree(article)
    if img:
        img_contents = download_image(img)
    else:
        img_contents = None
    intro = _get_introduction_from_tree(article)
    url = "http://en.wikipedia.org/wiki/%s" % name.replace(" ", "_")
    return img_contents, intro, url

def search(title):
    """ Perform a title search and return the first matching page """
    args = {"format": "json", "action": "query", "list": "search", "srsearch": title}
    data = _make_wp_query(args)
    results = data["query"]["search"]
    if len(results):
        title = results[0]["title"]
        return title
    return None

