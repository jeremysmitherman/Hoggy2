from sqlalchemy import Column, Integer, String, Text
import Hoggy2.meta as meta
from sqlalchemy.orm import sessionmaker
import re

class TwitchStream(meta.base):
	__tablename__="twitch_streams"
	id = Column(Integer, primary_key=True)
	owner = Column(String(20))
	streamurl = Column(String(200))

	def __repr__(self):
		return "Twitch Stream { owner: " + str(self.owner) + " url: " + str(self.streamurl) + " }"

class TwitchDAO():
	from Hoggy2.meta import engine

	Session = sessionmaker(bind=engine)
	session = Session()

	def add_stream_for_user(self, user, streamurl):
		if not re.search(r'http(s)?://(www\.)?twitch.tv/.+',streamurl):
		    raise Exception("Add in the format http://www.twitch.tv/<stream>")
		new_stream = TwitchStream()
		new_stream.owner = user
		new_stream.streamurl = streamurl
		self.session.add(new_stream)
		self.session.commit()
		return "Added stream for {0}".format(user)


	def get_stream_for_user(self, user):
		try:
			return self.session.query(TwitchStream).filter_by(owner=user).one()
		except:
			return None

	def remove_stream_for_user(self,user):
		self.session.query(TwitchStream).filter_by(owner=user).delete()
		self.session.commit()


	def get_all_streams(self):
		return self.session.query(TwitchStream).all()