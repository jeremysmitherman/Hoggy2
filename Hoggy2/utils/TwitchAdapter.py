import threading
import requests
import json
import logging
import Hoggy2.models.twitchstream as twitchstream

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('twitch_adapter.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)

log.addHandler(fh)

class TwitchAdapter(threading.Thread):
	twitch_api_url = 'https://api.twitch.tv/kraken/streams/'
	stop_event = threading.Event()

	def __init__(self, client, channel):
		log.info("Twitch Adapter Init")
		threading.Thread.__init__(self)
		self.daemon = True
		self.isRunning = True
		self.client = client
		self.channel = channel
		self.session = requests.session()
		self.live_streams = []
		self.dao = twitchstream.TwitchDAO()

	def run(self):
		log.info("Beginning processing")
		while self.isRunning:
			self.check_streams()
			if self.stop_event.wait(60) == True:
				self.isRunning = False
			

	def check_streams(self):
		streams = self.dao.get_all_streams()
		if (len(streams) == 0):
			return
		for stream in streams:
			stream_url = stream.streamurl
			owner = stream.owner
			twitch_user = stream_url.split('/')[-1]
			req_url = self.twitch_api_url + twitch_user
			headers = {"Client-ID":"hoggy-the hoggit irc bot"}
			req = self.session.get(req_url)
			if req.status_code != 200:
				log.warn ("Didn't get correct response back from twitch api for user {0}: {1}".format(twitch_user, req))
				return
			data = json.loads(req.text)
			#print "data['stream'] is " + str(data['stream'])
			if data['stream'] == None:
				#Offline, remove it from the live list.
				if stream_url in self.live_streams:
					log.info("Marking {0}s stream as offline".format(owner))
					self.live_streams.remove(stream_url)
			else:
				#Online? If it's in the livestream list, don't do anything				
				if stream_url not in self.live_streams:
					self.live_streams.append(stream_url)
					log.info("Marking {0}s stream as live".format(owner))
					if data['stream']['game'] != None:
						game = data['stream']['game']
						self.client.msg(self.channel, "{0} is streaming {1} at {2}".format(owner, game,stream_url))	
					else:
						self.client.msg(self.channel, "{0}'s Twitch stream just went live at {1}".format(owner,stream_url))



					

