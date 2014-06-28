import sys
sys.path.append("..")
import irc_bot, Hoggy2
from twisted.internet import reactor

def main():
    Hoggy2.log.info("Hello! - Starting IRC Bot!")
    # create factory protocol and application
    f = irc_bot.HoggyBotFactory(Hoggy2.config, Hoggy2.log)
    # connect factory to this host and port
    reactor.connectTCP(Hoggy2.config.get('irc', 'host'), int(Hoggy2.config.get('irc', 'port')), f)   
    # run bot
    reactor.run()

if __name__ == "__main__":
    main()
