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
        return self.request()

    def page(self, page):
        query = self.query()
        end = page*10
        start = end-9
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

        return responseXml
