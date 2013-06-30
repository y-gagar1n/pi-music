import mpd
import pprint
import math

class play_stream:
	def __init__(self):
		self.client = mpd.MPDClient()
		self.client.connect("localhost", 6600)	
		self.clear()
		self.playlist = {}

	def addplay(self, stream_uri, artist, title, duration):		
		songid = self.client.addid(stream_uri)
		self.playlist[songid] = { "id" : songid, "uri" : stream_uri, "artist" : artist, "title" : title, "duration" : duration }
		self.client.playid(songid)
		return songid

	def addplayrange(self, list):		
		first = True
		songid = 0
		for item in list:			
			if(first):				
				self.addplay(item["href"], item["artist"], item["title"], item["duration"])
				first = False
			else:
				self.add(item["href"], item["artist"], item["title"], item["duration"])			

	def add(self, stream_uri, artist, title, duration):		
		songid = self.client.addid(stream_uri)
		self.playlist[songid] = { "id" : songid, "uri" : stream_uri, "artist" : artist, "title" : title, "duration" : duration }

	def play(self, songid):
		self.client.playid(songid)

	def is_playing(self):
		state = self.client.status()['state']		
		return state == "play"

	def clear(self):
		self.client.clear()

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
		result = []
		for item in playlistinfo:
			item_to_add = self.playlist[item["id"]]
			item_to_add["current"]	= (item_to_add["id"] == currentsonginfo["id"])
			result.append(item_to_add)
		return result

	def currentsong(self):
		songid = self.client.currentsong()["id"]		
		return self.playlist[songid]