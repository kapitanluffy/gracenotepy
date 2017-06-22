from __future__ import print_function
import xml.etree.ElementTree, json
from .gnquery import GnQuery

try:
    import urllib.request as urllib_request
    import urllib.parse   as urllib_parse
except ImportError:
    import urllib2 as urllib_request
    import urllib as urllib_parse

class GnClient(object):

    # Client ID
    #   Required to register and fetch the user id
    clientId = None

    # User ID
    #   Required to query Gracenote API
    userId = None

    # Gracenote Query object
    gnquery = None

    # Gracenote API url
    apiUrl = None

    def __init__(self, clientId=None, userId=None):
        if clientId is not None:
            self.clientId = clientId
            prefix = clientId.split('-')[0]
            self.apiUrl = 'https://c' + prefix + '.web.cddbp.net/webapi/xml/1.0/'
        if userId is not None:
            self.userId = userId
            self.gnquery = GnQuery(self.clientId, self.userId)

    def query(self):
        if self.gnquery is None:
            self.gnquery = GnQuery(self.clientId, self.userId)

        return self.gnquery

    def register(self):
        query = self.query()
        query.register(self.clientId)
        return self.request()

    def search(self, track=None, artist=None, album=None):
        query = self.query()
        query.search(track=track, artist=artist, album=album)
        query.selectExtended('COVER,REVIEW,ARTIST_BIOGRAPHY,ARTIST_IMAGE')
        query.coverSize('xlarge')
        response = self.request()

        albumsXml = response.findall('ALBUM')
        tracks = []

        for albumXml in albumsXml:
            track = GnTrack(albumXml)
            tracks.append(track)

        # range
        rangeXml = response.find('RANGE')
        resultsRange = {}
        resultsRange['total'] = rangeXml.findtext('COUNT', '0')
        resultsRange['start'] = rangeXml.findtext('START', '1')
        resultsRange['end'] = rangeXml.findtext('END', '10')

        return tracks

    def page(self, page, limit=20):
        query = self.query()
        end = int(page) * int(limit)
        start = int(end) - ( int(limit) - 1 )
        query.range(start, end)

        return self

    def request(self):
        queryXml = self.query().toString()
        response = urllib_request.urlopen(self.apiUrl, queryXml)
        responseXml = response.read()
        responseTree = xml.etree.ElementTree.fromstring(responseXml)
        resp = responseTree.find('RESPONSE')

        # reset query
        self.query = None

        if resp.attrib['STATUS'] == 'ERROR':
            message = responseTree.find('MESSAGE')
            raise Exception(message.text)

        return resp

class GnTrack(dict):
    def __init__(self, albumXml):
        trackXml = albumXml.find('TRACK')
        self['title'] = self.__normalizeText('TITLE', trackXml)
        self['track_num'] = self.__normalizeText('TRACK_NUM', trackXml)
        self['track_genre'] = self.__normalizeText('GENRE', trackXml)
        self['artist'] = self.__normalizeText('ARTIST', albumXml)
        self['album'] = self.__normalizeText('TITLE', albumXml)
        self['album_track_count'] = self.__normalizeText('TRACK_COUNT', albumXml)
        self['album_genre'] = self.__normalizeText('GENRE', albumXml)
        self['year'] = self.__normalizeText('DATE', albumXml)
        self['artist_image'] = {'width': 0, 'height': 0, 'url': None}
        self['album_cover'] = {'width': 0, 'height': 0, 'url': None}

        urlsXml = albumXml.findall('URL')
        for urlXml in urlsXml:
            if urlXml.attrib['TYPE'] == 'ARTIST_IMAGE':
                key = 'artist_image'
            if urlXml.attrib['TYPE'] == 'COVERART':
                key = 'album_cover'

            self[key]['width'] = urlXml.attrib['WIDTH']
            self[key]['height'] = urlXml.attrib['HEIGHT']
            self[key]['url'] = urlXml.text

        # Gracenote ids
        self['gn_meta'] = {}
        self['gn_meta']['track_gn_id'] = self.__normalizeText('GN_ID', trackXml)
        self['gn_meta']['album_gn_id'] = self.__normalizeText('GN_ID', albumXml)

    def __normalizeText(self, name, _xml, unquote = True):
        t = _xml.findtext(name, None)
        if t is not None and unquote is True:
            t = urllib_parse.unquote(t)
        return t
