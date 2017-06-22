from __future__ import print_function
import xml.etree.ElementTree

class GnQuery(object):

    # Client ID
    #   Required to register and fetch the user id
    clientId = None

    # User ID
    #   Required to query Gracenote API
    userId = None

    def __init__(self, clientId=None, userId=None):
        self.root = xml.etree.ElementTree.Element('QUERIES')
        xml.etree.ElementTree.SubElement(self.root, 'QUERY')

        if clientId is not None and userId is not None:
            self.authenticate(clientId, userId)

    def toString(self):
        return xml.etree.ElementTree.tostring(self.root)

    def register(self, clientId):
        query = self.root.find('QUERY')
        query.attrib['CMD'] = 'REGISTER'
        client = xml.etree.ElementTree.SubElement(query, 'CLIENT')
        client.text = clientID

    def authenticate(self, clientId, userId):
        auth = xml.etree.ElementTree.SubElement(self.root, 'AUTH')
        client = xml.etree.ElementTree.SubElement(auth, 'CLIENT')
        client.text = clientId
        user = xml.etree.ElementTree.SubElement(auth, 'USER')
        user.text = userId

    def search(self, track=None, artist=None, album=None):
        query = self.root.find('QUERY')
        query.attrib['CMD'] = 'ALBUM_SEARCH'

        if track is not None:
            self.searchTrack(track)
        if artist is not None:
            self.searchArtist(artist)
        if album is not None:
            self.searchAlbum(album)

    def searchArtist(self, value):
        query = self.root.find('QUERY')
        text = xml.etree.ElementTree.SubElement(query, 'TEXT')
        text.attrib['TYPE'] = 'ARTIST'
        text.text = value

    def searchAlbum(self, value):
        query = self.root.find('QUERY')
        text = xml.etree.ElementTree.SubElement(query, 'TEXT')
        text.attrib['TYPE'] = 'ALBUM_TITLE'
        text.text = value

    def searchTrack(self, value):
        query = self.root.find('QUERY')
        text = xml.etree.ElementTree.SubElement(query, 'TEXT')
        text.attrib['TYPE'] = 'TRACK_TITLE'
        text.text = value

    def range(self, start, end):
        query = self.root.find('QUERY')
        r = xml.etree.ElementTree.SubElement(query, 'RANGE')
        s = xml.etree.ElementTree.SubElement(r, 'START')
        s.text = str(start)
        e = xml.etree.ElementTree.SubElement(r, 'END')
        e.text = str(end)

    def selectExtended(self, value='COVER,REVIEW,ARTIST_BIOGRAPHY,ARTIST_IMAGE,ARTIST_OET,MOOD,TEMPO'):
        query = self.root.find('QUERY')
        option = xml.etree.ElementTree.SubElement(query, 'OPTION')
        parameter = xml.etree.ElementTree.SubElement(option, 'PARAMETER')
        parameter.text = 'SELECT_EXTENDED'
        valueElem = xml.etree.ElementTree.SubElement(option, 'VALUE')
        valueElem.text = value

    def selectDetail(self, value='GENRE:3LEVEL,MOOD:2LEVEL,TEMPO:3LEVEL,ARTIST_ORIGIN:4LEVEL,ARTIST_ERA:2LEVEL,ARTIST_TYPE:2LEVEL'):
        query = self.root.find('QUERY')
        option = xml.etree.ElementTree.SubElement(query, 'OPTION')
        parameter = xml.etree.ElementTree.SubElement(option, 'PARAMETER')
        parameter.text = 'SELECT_DETAIL'
        valueElem = xml.etree.ElementTree.SubElement(option, 'VALUE')
        valueElem.text = value
