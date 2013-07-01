import mpd


class play_stream:

    def __init__(self):
        self.client = mpd.MPDClient()
        self.client.connect("localhost", 6600)
        self.clear()
        self.playlist = {}
        self._playlist_updated = False

    def addplay(self, stream_uri, artist, title, duration):
        songid = self.client.addid(stream_uri)
        self.playlist[songid] = {"id": songid,
                                 "uri": stream_uri, "artist": artist, "title": title, "duration": duration}
        self.client.playid(songid)
        self._playlist_updated = True
        return songid

    def addplayrange(self, list):
        first = True
        for item in list:
            if(first):
                self.addplay(item["url"], item[
                             "artist"], item["title"], item["duration"])
                first = False
            else:
                self.add(item["url"], item[
                         "artist"], item["title"], item["duration"])
        self._playlist_updated = True

    def addrange(self, list):
        for item in list:
            self.add(item["url"], item[
                     "artist"], item["title"], item["duration"])
        self._playlist_updated = True

    def add(self, stream_uri, artist, title, duration):
        songid = self.client.addid(stream_uri)
        self.playlist[songid] = {"id": songid, "uri": stream_uri,
                                 "artist": artist, "title": title, "duration": duration}
        self._playlist_updated = True

    def play(self, songid):
        self.client.playid(songid)

    def is_playing(self):
        state = self.client.status()['state']
        return state == "play"

    def clear(self):
        self.client.clear()
        self._playlist_updated = True

    def pause(self):
        state = self.client.status()['state']
        pause = 1 if state != 'pause' else 0
        self.client.pause(pause)

    def previous(self):
        self.client.prevoius()

    def next(self):
        self.client.next()

    def addvolume(self, vol):
        old_volume = int(self.client.status()["volume"])
        new_volume = old_volume + vol

        if new_volume < 0:
            new_volume = 0
        if new_volume > 100:
            new_volume = 100
        try:
            self.client.setvol(new_volume)
        except Exception as e:
            print e

    def getplaylistinfo(self):
        playlistinfo = self.client.playlistinfo()
        currentsonginfo = self.client.currentsong()
        print currentsonginfo

        result = []
        print self.playlist
        for item in playlistinfo:
            item_to_add = self.playlist[item["id"]]
            if(currentsonginfo):
                item_to_add["current"] = (item_to_add["id"] == currentsonginfo["id"])
            result.append(item_to_add)
        return result

    def currentsong(self):
        songid = self.client.currentsong()["id"]
        return self.playlist[songid]

    def playlist_updated(self):
        if self._playlist_updated:
            self._playlist_updated = False
            return True
        return False
