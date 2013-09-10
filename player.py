import math
import string
import time
import urllib as ul
import json

from BeautifulSoup import BeautifulStoneSoup
import HTMLParser
import config
from flask import Flask, render_template, request, Response
from lastfm import lastfm_controller
from mpd_client import play_stream
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
import thread
import vk_api


app = Flask(__name__)
player = play_stream()
lastfm = lastfm_controller()

PODCASTS = {
    "Aerostat": "http://aerostat.rpod.ru/rss.xml",
    "Radio-T": "http://feeds.rucast.net/radio-t",
    "THE BIG PODCAST": "http://vasilysweekend.rpod.ru/rss.xml",
    "Radio Grinch": "http://radiogrinch.podfm.ru/rss/rss.xml"
}


@app.route("/")
def hello():
    try:
        return render_template("index.html", current_song=current_song_title())
    except Exception as e:
        print e


@app.route("/search")
def search():
    try:
        query = request.args.get('q')
        vk_response = getMp3Link(query)
        result = render_template(
            "list.html", list=vk_response, current_song=current_song_title())
        return result
    except Exception as e:
        print e


@app.route("/search_album")
def search_album():
    try:
        artist = request.args.get('artist')
        album = request.args.get('album')
        response = lastfm.getalbuminfo(artist, album)
        soup = BeautifulStoneSoup(''.join(response))
        album_artist = soup.lfm.album.artist.string
        tracklist = soup.lfm.album.tracks
        query_list = []
        for track in tracklist.findAll("track"):
            query = {'artist': album_artist, 'title': track.find(
                name="name").string, 'duration': track.duration.string}
            query_list.append(query)

        find_play_range(query_list)
        return fetch_playlist()
    except Exception as e:
        return e


def find_play_range(query_list):
    thread.start_new_thread(find_play_range_worker, (query_list,))


def find_play_range_worker(query_list):
    first = True
    for query in query_list:
        item = get_single_song(query[
                               "artist"], query["title"], query["duration"])
        if(item):
            if first:
                player.addplay(item["url"], item[
                               "artist"], item["title"], item["duration"])
            else:
                player.add(item["url"], item[
                           "artist"], item["title"], item["duration"])
        first = False


@app.route("/artist")
def search_artist():
    try:
        artist = request.args.get('artist')
        response = lastfm.gettopalbums(artist)
        soup = BeautifulStoneSoup(''.join(response))
        corrected_artist = soup.lfm.topalbums['artist']
        albumlist = soup.lfm.topalbums
        album_search_results = []
        for album in albumlist.findAll("album"):
            album_entity = {
                'title': album.find(name="name").string,
                'image': album.find('image', size="large").string
            }
            album_search_results.append(album_entity)

        result = render_template("albumlist.html", list=album_search_results,
                                 artist=corrected_artist, current_song=current_song_title())
        return result
    except Exception as e:
        return e


@app.route("/top")
def top():
    try:
        artist = request.args.get('artist')
        response = lastfm.gettoptracks(artist)
        soup = BeautifulStoneSoup(''.join(response))
        corrected_artist = soup.lfm.toptracks['artist']
        tracklist = soup.lfm.toptracks
        query_list = []
        for track in tracklist.findAll("track"):
            query = {'artist': corrected_artist, 'title': track.find(
                name="name").string, 'duration': track.duration.string}
            query_list.append(query)
        find_play_range(query_list)
        return fetch_playlist()
    except Exception as e:
        return e


@app.route("/podcast_list")
def podcasts_list():
    try:
        podcast_names = PODCASTS.keys()
        return render_template("podcastlist.html", list=podcast_names, current_song=current_song_title())
    except Exception as e:
        return e


@app.route("/podcast")
def podcast():
    try:
        title = request.args.get('title')
        mode = request.args.get('m')

        rss_url = PODCASTS[title]
        response = ul.urlopen(rss_url).read()

        soup = BeautifulStoneSoup(''.join(response))
        channel = soup.rss.channel
        if mode == "latest":
            item = channel.find("item")
            p = parse_podcast(item)
            player.addplay(p['url'], p['artist'], p['title'], p['duration'])
            return "success"

        if mode == "list":
            list = []
            for item in channel.findAll("item"):
                p = parse_podcast(item)
                if p:
                    list.append(p)
            result = render_template(
                "list.html", list=list, current_song=current_song_title())
            return result
    except Exception as e:
        return e


def parse_podcast(item):
    if(item.enclosure):
        url = item.enclosure["url"]
        url = url[0: string.rfind(url, ".mp3") + 4]

        artist_xml = item.find("itunes:author")
        artist = artist_xml.string if artist_xml else item.author.string

        title_xml = item.find("itunes:title")
        title = title_xml.string if title_xml else item.title.string

        duration_xml = item.find("itunes:duration")
        duration = 0
        if(duration_xml):
            duration = duration_xml.string
        elif item.duration:
            duration = item.duration.string

        return {'url': url, 'artist': artist, 'title': title, 'duration': duration}
    else:
        return None


@app.route("/addplay")
def addplay_song():
    try:
        url = request.args.get('url')
        artist = request.args.get('artist')
        title = request.args.get('title')
        duration = request.args.get('duration')
        player.addplay(url, artist, title, duration)
        return "success"
    except Exception as e:
        print e


@app.route("/play")
def play_song():
    try:
        id = request.args.get('id')
        player.play(id)
        return "success"
    except Exception as e:
        print e


@app.route("/addplayrange")
def add_play_songs_range():
    try:
        songs = json.loads(request.args.get('songs'))
        player.addplayrange(songs)
        return "success"
    except Exception as e:
        print e


@app.route("/clear")
def clear_songs():
    try:
        player.clear()
        return "success"
    except Exception as e:
        print e


@app.route("/add")
def add_song():
    try:
        url = request.args.get('url')
        artist = request.args.get('artist')
        title = request.args.get('title')
        duration = request.args.get('duration')
        player.add(url, artist, title, duration)
        return "success"
    except Exception as e:
        print e


@app.route("/addrange")
def add_songs_range():
    try:
        songs = json.loads(request.args.get('songs'))
        print songs
        print len(songs)
        player.addrange(songs)
        return "success"
    except Exception as e:
        print e


@app.route("/pause")
def pause_song():
    player.pause()
    return "success"


@app.route("/volume_minus")
def volume_minus():
    player.addvolume(-10)
    return "success"


@app.route("/volume_plus")
def volume_plus():
    player.addvolume(10)
    return "success"


@app.route("/next")
def next_song():
    player.next()
    return "success"


@app.route("/previous")
def previous_song():
    player.previous()
    return "success"


@app.route("/playlist")
def fetch_playlist():
    try:
        playlistinfo = player.getplaylistinfo()
        result = render_template("playlist.html", list=playlistinfo)
        return result
    except Exception as e:
        print e


def get_single_song(artist, title, duration):
    h = HTMLParser.HTMLParser()
    query = h.unescape("%s %s" % (artist, title))
    response = vk_search(query)

    artist = artist.strip().lower()
    title = title.strip().lower()

    if(len(response) > 1):
        for item in response[1:]:
            song = parseOne(item)
            if(not duration or math.fabs(item["duration"] - int(str(duration.string))) < 10):
                return song
    return None


def getMp3Link(query, count=0):
    try:
        response = vk_search(query, count)
        if(len(response) > 1):
            return parseList(response[1:])
        else:
            return None
    except Exception as e:
        print e


def vk_search(query, count=0):
    try:
        login = config.vk['login']
        password = config.vk['password']

        vk = vk_api.VkApi(login, password)
        values = {'q': query}
        if(count):
            values['count'] = count
        response = vk.method('audio.search', values)

        return response
    except Exception as e:
        print e


def getcurrentsong_url():
    if player.is_playing():
        song = player.currentsong()
        url = song["uri"]
        return url
    else:
        return ""


def parseList(list):
    return map(parseOne, list)


def parseOne(x):
    return {
        "url": x["url"],
        "artist": x["artist"],
        "title": x["title"],
        "duration": parseDuration(x["duration"])
    }


def parseDuration(durationstr):
    duration = int(durationstr)
    return "%(min)d:%(sec)02d" % {'min': duration / 60, 'sec': duration % 60}


def current_song_title():
    if(player.is_playing()):
        song = player.currentsong()
        return "%s - %s" % (song["artist"], song["title"])
    return ""


class PlayerNamespace(BaseNamespace):

    def initialize(self):
        last_url = getcurrentsong_url()
        current_url = last_url
        while True:
            if not current_url == "" and not current_url == last_url:
                self.emit("song_changed", {"title" : current_song_title(), "url" : current_url })
                last_url = current_url
            current_url = getcurrentsong_url()

            if player.playlist_updated():
                self.emit("playlist_updated")

            time.sleep(0.5)


@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'/player': PlayerNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
    return Response()

if __name__ == "__main__":
    app.run(host="0.0.0.0")
