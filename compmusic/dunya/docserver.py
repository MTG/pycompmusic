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

import os

import compmusic.dunya.conn


def get_collections():
    """Get a list of all collections in the server."""
    path = "document/collections"
    return compmusic.dunya.conn._get_paged_json(path)


def get_collection(slug):
    """Get the documents (recordings) in a collection.

    :param slug: the name of the collection

    """
    path = "document/%s" % slug
    return compmusic.dunya.conn._dunya_query_json(path)


def document(recordingid):
    """Get the available source filetypes for a Musicbrainz recording.

    :param recordingid: Musicbrainz recording ID
    :returns: a list of filetypes in the database for this recording

    """
    path = "document/by-id/%s" % recordingid
    recording = compmusic.dunya.conn._dunya_query_json(path)
    return recording


def create_document(collection, document, title=None):
    """Create a specific document inside a collection

    :param collection: Name of the collection
    :param document: Musicbrainz recording ID of the specific document
    :returns: The contents of the most recent version of the derived file

    """
    path = "/document/by-id/%s" % document
    data = {"collection": collection}
    if title:
        data["title"] = title
    url = compmusic.dunya.conn._make_url(path)
    req = compmusic.dunya.conn._dunya_post(url, data=data)
    return req.json()


def update_document(collection, document, title=None):
    """Update a specific document inside a collection

    :param collection: Name of the collection
    :param document: Musicbrainz recording ID of the specific document
    :param title: Name of the required document
    :returns: The contents of the most recent version of the derived file

    """
    path = "/document/by-id/%s" % document
    data = {"collection": collection}
    if title:
        data["title"] = title
    url = compmusic.dunya.conn._make_url(path)
    req = compmusic.dunya.conn._dunya_post(url, data=data)
    return req.json()


def update_sourcetype(document, filetype, file):
    """Update a specific document considered sourcetype

    :param document: Musicbrainz recording ID of the specific document
    :param filetype: Name of the sourcetype
    :param file: Path to the new file that will update the sourcetype
    :returns: The contents of the most recent version of the derived file

    """
    return add_sourcetype(document, filetype, file)


def add_sourcetype(document, filetype, file):
    """ Add a new file to the sourcetype.If file is a string and refers to a 
    file on disk, the contents of the file is read and send, otherwise it is sent as-is 

    :param document: Musicbrainz recording ID of the specific document
    :param filetype: Name of the sourcetype
    :param file: Path to the new file that will update the sourcetype
    :returns: The contents of the most recent version of the derived file

    """
    path = "/document/by-id/%s/add/%s" % (document, filetype)
    if isinstance(file, str) and os.path.exists(file):
        f = open(file, "rb")
    else:
        f = file
    files = {"file": f}
    url = compmusic.dunya.conn._make_url(path)
    req = compmusic.dunya.conn._dunya_post(url, files=files)
    return req.json()


def create_and_upload_document(collection, document, title, filetype, file):
    """ Create and upload a new file to the sourcetype

    :param collection: Name of the collection
    :param document: Musicbrainz recording ID of the specific document
    :param title: Title of the document
    :param filetype: Name of the sourcetype
    :param file: Path to the new file that will update the sourcetype
    :returns: The contents of the most recent version of the derived file

    """
    create_document(collection, document, title)
    add_sourcetype(document, filetype, file)


def file_for_document(recordingid, thetype, subtype=None, part=None, version=None):
    """Get the most recent derived file given a filetype.

    :param recordingid: Musicbrainz recording ID
    :param thetype: the computed filetype
    :param subtype: a subtype if the module has one
    :param part: the file part if the module has one
    :param version: a specific version, otherwise the most recent one will be used
    :returns: The contents of the most recent version of the derived file

    """
    path = "document/by-id/%s/%s" % (recordingid, thetype)
    args = {}
    if subtype:
        args["subtype"] = subtype
    if part:
        args["part"] = part
    if version:
        args["v"] = version
    return compmusic.dunya.conn._dunya_query_file(path, **args)


def get_mp3(recordingid):
    """Get a mp3 from a specific mbid
    
    :param recordingid: Musicbrainz recording ID

    """
    return file_for_document(recordingid, "mp3")


def get_document_as_json(recordingid, thetype, subtype=None, part=None, version=None):
    """ Get a derived filetype and load it as json.

    :param recordingid: Musicbrainz recording ID
    :param thetype: the computed filetype
    :param subtype: a subtype if the module has one
    :param part: the file part if the module has one
    :param version: a specific version, otherwise the most recent one will be used
    :returns: The contents of the most recent version of the derived file

    """

    path = "document/by-id/%s/%s" % (recordingid, thetype)
    args = {}
    if subtype:
        args["subtype"] = subtype
    if part:
        args["part"] = part
    if version:
        args["v"] = version
    return compmusic.dunya.conn._dunya_query_json(path, **args)
