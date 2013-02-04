from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
import time, sys, re
import cleverbot
import signal
import time
from threading import Lock

def reloadh(SIG, FRM):
	print "reloading..."
	reload(commands)
signal.signal(signal.SIGHUP, reloadh)

class MessageLogger:
	"""
	An independent logger class (because separation of application
	and protocol logic is a good thing).
	"""
	def __init__(self, file):
		self.file = file

	def log(self, message):
		"""Write a message to the file."""
		timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
		self.file.write('%s %s\n' % (timestamp, message))
		self.file.flush()

	def close(self):
		self.file.close()




class Bot(irc.IRCClient):
	nickname = "whe4tley"
	realname = "Wheatley"
	username = "Wheatley"
	versionName = "Wheatley 13.37"
	versionNum = "1337"
	versionEnv = "Aperture Science"
	nspassword = ""
	
	sessions = {
		
	}
	sessLock = Lock()

	def removeOldSessions(self):
		self.sessLock.acquire(True)
		try:
			for nick in self.sessions:
				if self.sessions[nick].lastTs < time.time()-(60*10):
					del self.sessions[nick]
		except RuntimeError:
			pass;
		self.sessLock.release()
	
	def handleMessage(self, user, msg):
		self.removeOldSessions()
		msg = msg.strip()
		self.sessLock.acquire(True)
#		if msg == "[delete sess]":
#			if user in self.sessions:
#				del self.sessions[user]
#			return
		if user not in self.sessions:
			self.sessions[user] = cleverbot.Session()
		reply = self.sessions[user].Ask(msg)
		self.sessLock.release()
		self.say(self.channel, user+": "+reply)

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)
		self.logger = MessageLogger(open(self.factory.filename, "a"))
		self.logger.log("[connected at %s]" % 
						time.asctime(time.localtime(time.time())))

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.log("[disconnected at %s]" % 
						time.asctime(time.localtime(time.time())))
		self.logger.close()

	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		self.msg("NickServ", "identify "+self.nspassword)
		self.join(self.factory.channel)

	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		self.logger.log("[I have joined %s]" % channel)
		self.channel = self.factory.channel
	
	def privmsg(self, user, channel, msg):
		"""This will get called when the bot receives a message."""
		user = user.split('!', 1)[0]
		self.logger.log("<%s> %s" % (user, msg))
		
		# Check to see if they're sending me a private message
		if channel == self.nickname:
			msg = "It isn't nice to whisper!  Play nice with the group."
			self.msg(user, msg)
			return

		# Otherwise check to see if it is a message directed at me
		if msg.startswith(self.nickname + ":"):
			self.handleMessage(user, msg.split(':',1)[1])
			self.logger.log("<%s> %s" % (self.nickname, msg))

	def action(self, user, channel, msg):
		"""This will get called when the bot sees someone do an action."""
		user = user.split('!', 1)[0]
		self.logger.log("* %s %s" % (user, msg))
	

	# irc callbacks

	def irc_NICK(self, prefix, params):
		"""Called when an IRC user changes their nickname."""
		old_nick = prefix.split('!')[0]
		new_nick = params[0]
		self.logger.log("%s is now known as %s" % (old_nick, new_nick))


	# For fun, override the method that determines how a nickname is changed on
	# collisions. The default method appends an underscore.
	def alterCollidedNick(self, nickname):
		"""
		Generate an altered version of a nickname that caused a collision in an
		effort to create an unused related name for subsequent registration.
		"""
		return nickname + '^'



class BotFactory(protocol.ClientFactory):
	def __init__(self, channel, filename):
		self.channel = channel
		self.filename = filename

	def buildProtocol(self, addr):
		p = Bot()
		p.factory = self
		import settings
		settings.loadSettings(p)
		return p

	def clientConnectionLost(self, connector, reason):
		"""If we get disconnected, reconnect to server."""
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()


if __name__ == '__main__':
	# initialize logging
	log.startLogging(sys.stdout)
	
	# create factory protocol and application
	f = BotFactory("#xomg", "./wheatley.log")

	# connect factory to this host and port
	reactor.connectTCP("2001:6b0:5:1688::200", 6667, f)

	# run bot
	reactor.run()
