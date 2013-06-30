import urllib as ul
import httplib as hl
import config

API_KEY = config.last_fm['API_KEY']
API_SECRET = config.last_fm['API_SECRET']
LASTFM_URL = 'ws.audioscrobbler.com'


class lastfm_controller:

    def request(self, query):
        conn = hl.HTTPConnection(LASTFM_URL)

        conn.request('GET', '/2.0/?' + query)
        response = conn.getresponse()
        return response.read()
        conn.close()

    def get_album_info_query(self, artist, album):
        artist = ''.join(artist).encode('utf8')
        album = ''.join(album).encode('utf8')

        artist = ul.quote_plus(artist)
        album = ul.quote_plus(album)

        data = {"api_key": API_KEY, 'artist': artist, 'album':
                album, 'autocorrect': '1', 'method': 'album.getinfo', 'lang': 'ru'}
        return ul.unquote(ul.urlencode(data))

    def get_top_albums_query(self, artist):
        artist = ''.join(artist).encode('utf8')
        artist = ul.quote_plus(artist)

        data = {"api_key": API_KEY, 'artist': artist,
                'autocorrect': '1', 'method': 'artist.getTopAlbums', 'lang': 'ru'}
        return ul.unquote(ul.urlencode(data))

    def get_top_tracks_query(self, artist):
        artist = ''.join(artist).encode('utf8')
        artist = ul.quote_plus(artist)

        data = {"api_key": API_KEY, 'artist': artist,
                'autocorrect': '1', 'method': 'artist.getTopTracks', 'lang': 'ru'}
        return ul.unquote(ul.urlencode(data))

    def getalbuminfo(self, artist, album):
        query = self.get_album_info_query(artist, album)
        response = self.request(query)
        return response

    def gettopalbums(self, artist):
        query = self.get_top_albums_query(artist)
        response = self.request(query)
        return response

    def gettoptracks(self, artist):
        query = self.get_top_tracks_query(artist)
        response = self.request(query)
        return response
