import pip, logging, sys, ConfigParser

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("setup.log")
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
fh.setFormatter(formatter)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)

log.addHandler(sh)
log.addHandler(fh)

log.info("Installing dependencies...")
packages = [
    "praw",
    "flask",
    "sqlalchemy",
    "twisted",
    "pytest",
    "mock"
]

for package in packages:
    try:
        pip.main(['install', package])
    except:
        log.error("error installing %s, ensure you have python devel installed, it is needed for Twisted in particular" % package)
        sys.exit()

log.info("Finished installing dependencies.")

while True:
    dbtype = raw_input("\r\nDatabase type? (\"mysql\" or \"sqlite\"): ")
    if dbtype == "sqlite":
        filename = raw_input("\r\nSqlite file name (Static or relative file path ok): ")
        break
    elif dbtype == "mysql":
        log.error("Not yet supported")
        sys,exit()
    else:
        continue

irc_server = raw_input("\r\nIRC Server: ")
irc_port = raw_input("\r\nIRC Port: ")
irc_port = int(irc_port)
irc_nick = raw_input("\r\nIRC Nick for bot: ")
irc_pass = raw_input("\r\nIRC Password for bot (blank for none): ")
irc_channel = raw_input("\r\nIRC Channel to join: ")
reddit_user = raw_input("\r\nReddit username (needed to monitor for new posts, blank to disable): ")
if reddit_user:
    reddit_pass = raw_input("\r\nReddit password: ")
    reddit_sub = raw_input("\r\nSubreddit to monitor (Without the /r/ please): ")

config_file = open("config.ini", 'w')
config = ConfigParser.ConfigParser();
config.add_section("hoggy")
config.set("hoggy", "logfile", "hoggy.log")
config.set("hoggy", "dbtype", dbtype)
config.set("hoggy", "dbfile", filename)

config.add_section("irc")
config.set("irc", "nick", irc_nick)
config.set("irc", "password", irc_pass)
config.set("irc", "channel", irc_channel)
config.set("irc", "host", irc_server)
config.set("irc", "port", irc_port)

if reddit_user:
    config.add_section("reddit")
    config.set("reddit", "subreddit", reddit_sub)
    config.set("reddit", "username", reddit_user)
    config.set("reddit", "password", reddit_pass)

config.write(config_file)
config_file.close()

log.info("Config.ini created!\r\nBootstrapping environment...")

import Hoggy2
import Hoggy2.meta as meta

import Hoggy2.models.quote as quote
import Hoggy2.models.time as time
import Hoggy2.models.twitchstream as twitchstream

try:
    quote.Quote.__table__.create(bind=meta.engine)
except:
    # probably already created
    pass

try:
    time.Time.__table__.create(bind=meta.engine)
except:
    pass

try:
    twitchstream.TwitchStream.__table__.create(bind=meta.engine)
except:
    pass