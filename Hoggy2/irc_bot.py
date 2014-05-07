from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
import time, re
import Hoggy2.core_actions as core
import Hoggy2.utils.TwitchAdapter as twitch_adapter

class GrabberException(Exception):
    pass

class Grabber(object):
    buffer = []

    def stack(self, user, line):
        self.buffer.append((user, line))
        while len(self.buffer) > 100:
            del self.buffer[0]

    def grab(self, user, lines=1):
        quote_lines = []
        for x in reversed(self.buffer):
            if len(quote_lines) == lines:
                break

            if user == x[0]:
                quote_lines.append(x[1])

        if len(quote_lines):
            quote = ""
            quote_lines.reverse()
            quote += " ".join(quote_lines)
            quote += " --" + user
            return quote
        else:
            raise GrabberException('No quotes found for user in last 100 lines.')

class HoggyBot(irc.IRCClient):
    lineRate = 1
    
    def __init__(self, config, log, *args, **kwargs):
        self.nickname = config.get("irc", "nick")
        self.password = config.get("irc", "password")
        self.log = log
        self.config = config
        self.grabber = Grabber()
        self.twitch_adapter = twitch_adapter.TwitchAdapter(self, self.config.get("irc","channel"))
        

        # assign the quote action to be !<name_of_bot>
        core.Action.actions["!%s" % config.get('irc','nick')] = core.hoggy
        core.Action.actions["!%s" % config.get('irc','nick').lower()] = core.hoggy

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.log.info("Connected at %s" % time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.log.info("Disconnected at %s" % time.asctime(time.localtime(time.time())))

    # callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.log.debug("Joining %s" % self.config.get("irc", "channel"))
        self.join(self.config.get("irc", "channel"))

    def joined(self, channel):
        if self.password:
            self.log.debug("Logging in with password.")
            self.msg('NickServ', 'IDENTIFY %s' % self.password)
        self.twitch_adapter.start()

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        # lazy backwards compatibility with HOggy1
        message = msg

        response = None

        # This is a hoggy action, supposedly.  Lets split it up into command + args
        if msg.startswith('!'):
            command_array = msg.split(' ')
            command = command_array[0]
            args = command_array[1:]

            # Make an instance of the requested action's class
            # Only reason I'm doing this instead of the old hoggy's 
            # classactions is because 2.7 can't do abstract classactions
            try:
                response = core.Action.actions.get(command)().execute(self, user, channel, args)
            except TypeError, ex:
                self.log.error(str(ex))
                response = "I don't know the command \"%s\". You can add it though! http://github.com/jeremysmitherman/Hoggy2" % command
            except core.ActionException, ex:
                response = str(ex)
            except Exception, ex:
                response = "Hoozin'ed it up: unexpected exception: {0}".format(str(ex))
            
        else:
            if ' r/' in message or '/r/' in message:
                obj = re.search(r'[/]?r/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                response = "http://reddit.com/%s" % sub

            if  ' u/' in message or '/u/' in message:
                obj = re.search(r'[/]?u/[^\s\n]*',message)
                sub = obj.group()
                if sub.startswith('/'):
                    sub = sub[1:]
                response = "http://reddit.com/%s" % sub

        self.grabber.stack(user, msg)

        if response is not None:
            if channel == self.nickname:
                self.msg(user, response.encode('utf-8'))
            else:
                self.msg(channel, response.encode('utf-8'))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

class HoggyBotFactory(protocol.ClientFactory):
    """A factory for HoggyBots.
    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, config, log):
        self.config = config
        self.log = log
        self.channel = config.get("irc","channel")

    def buildProtocol(self, addr):
        p = HoggyBot(self.config, self.log)
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()