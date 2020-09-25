# Trivial Tweet Server

import threading
import time
import sys
import socket

## Define users as a global dictionary.
## THIS IS A PSEUDO DATABASE. In a real implementation we would be using a config file and a database
users = {}

## Class for user objects, keep track of all values
class User():

	def __init__(self, username):
		self.username = username
		## All subscribed tweets RECEIVED
		self.timeline = []
		## All tweets send out
		self.tweets = []
		## List of subscriptions, MAX = 3
		self.subscriptions = []
		## Save user specific daemon thread
		self.userThread = None
		## Save user send socket and addr. 
		## This will be used to take input from the client side
		self.userSendSock = None
		self.userSendAddr = None
		## Save user receive socket and addr. 
		## This will be used to send input to the client side
		self.userReceiveSock = None
		self.userReceiveAddr = None
		## Used to check if the user has already received that specific tweet, 
		## we only want it to be sent once, 
		## EVEN if they've subscribed to multiple # that are in the tweet
		self.sentAlready = 0

	## setter marking if the tweet has been sent to the user or not
	def setSentAlready(self, num):
		self.sentAlready = num

	## set client send socket
	def setSendSocket(self, socket):
		self.userSendSock = socket

	## set client send addr
	def setSendAddr(self, addr):
		self.userSendAddr = addr

	## set client receive socket
	def setReceiveSocket(self, socket):
		self.userReceiveSock = socket

	## set client receive addr
	def setReceiveAddr(self, addr):
		self.userReceiveAddr = addr

	## set user specific thread
	def setThread(self, thread):
		self.userThread = thread

	## add tweet to user timeline
	def addTimeline(self, tweet):
		self.timeline.append(tweet)

	## add tweet to user sent tweets
	def addTweet(self, tweet):
		self.tweets.append(tweet)

	## add subscription to user subscriptions
	def addSub(self, sub):
		self.subscriptions.append(sub)

	## remove subscription from user subscriptions
	def removeSub(self, sub):
		self.subscriptions.remove(sub)

	## clear all subscriptions
	def clearSubs(self):
		self.subscriptions = []

## create a new client with the username paramter
def createNewClient(username):
	## set username taken flag to false
	taken = False
	## if username does exist
	if username in users.keys():
		taken = True

	##username isn't taken
	if not taken:
		## if there are 5 users
		if len(users.keys()) >= 5:
			taken = True

	## return if the username is taken or not
	return not taken

## listener waits for the user passed in to send a message through the
## send socket
## This exists in every user thread in order to 
## individually listen to each user
def listener(username):
	while True:
		## wait for keyword from the user
		message, addr = users[username].userSendSock.recvfrom(1024)
		keyword = message.decode()

		## keyword is tweet
		if keyword == "t":
			## wait for tweet message
			message, addr = users[username].userSendSock.recvfrom(1024)
			message = message.decode()

			## wait for hashtags
			hashtags, addr = users[username].userSendSock.recvfrom(1024)
			hashtags = hashtags.decode()

			## split hashtags
			tags = hashtags.split("#")
			tags = tags[1:]
			## format the tweet
			tweetString = "{} \"{}\" {}".format(username, message, hashtags)
			## for ever tag we check all users subscriptions
			for tag in tags:
				## for all users
				for u in users.keys():
					## if user hasn't received the tweet yet
					if users[u].sentAlready == 0:
						## check for sub
						if tag in users[u].subscriptions or "ALL" in users[u].subscriptions:
							## send tweet, add to timeline, flag user as already receiving
							users[u].userReceiveSock.sendto("t".encode(), users[u].userReceiveAddr)
							users[u].userReceiveSock.sendto(tweetString.encode(), users[u].userReceiveAddr)
							users[u].userReceiveSock.sendto("Done".encode(), users[u].userReceiveAddr)
							users[u].addTimeline(tweetString)
							users[u].setSentAlready(1)
			## reset all user sent already flags
			for u in users.keys():
				users[u].setSentAlready(0)
			## add tweet to tweets that this username has sent
			users[username].addTweet(tweetString)

		## subscriptions
		elif keyword == "sub":
			## wait for hashtag
			hashtag, addr = users[username].userSendSock.recvfrom(1024)
			hashtag = hashtag.decode()

			## tell client we're trying to subscribe
			users[username].userReceiveSock.sendto("sub".encode(), users[username].userReceiveAddr)

			## if we haven't already subbed and we dont have three already
			if hashtag[1:] not in users[username].subscriptions and len(users[username].subscriptions) < 3:
				## add sub and flag as success
				users[username].addSub(hashtag[1:])
				users[username].userReceiveSock.sendto("True".encode(), users[username].userReceiveAddr)
			else:
				## flag as false and send hashtag name back
				users[username].userReceiveSock.sendto("False".encode(), users[username].userReceiveAddr)
				users[username].userReceiveSock.sendto(hashtag.encode(), users[username].userReceiveAddr)
		##unsubscribe
		elif keyword == "unsub":
			## wait for hashtag
			hashtag, addr = users[username].userSendSock.recvfrom(1024)
			hashtag = hashtag.decode()
			## tell client we're trying to unsubscribe
			users[username].userReceiveSock.sendto("unsub".encode(), users[username].userReceiveAddr)
			## if ALL unsub from all
			if hashtag[1:] == "ALL":
				users[username].clearSubs()
				users[username].userReceiveSock.sendto("True".encode(), users[username].userReceiveAddr)
			else:
				try:
					## try to remove sub, if it works flag as success
					users[username].removeSub(hashtag[1:])
					users[username].userReceiveSock.sendto("True".encode(), users[username].userReceiveAddr)
				except:
					## flag as unsuccessful
					users[username].userReceiveSock.sendto("False".encode(), users[username].userReceiveAddr)
		## timeline
		elif keyword == "tl":
			## tell client to wait for timeline
			users[username].userReceiveSock.sendto("tl".encode(), users[username].userReceiveAddr)

			## init tString and loop through users timeline
			tString = ""
			for tweet in range(len(users[username].timeline)):
				## for every tweet, format and send to client
				parts = users[username].timeline[tweet].split("\"")
				tString = "{}: \"{}\" {}".format(parts[0].strip(),parts[1],parts[2].strip())
				users[username].userReceiveSock.sendto(tString.encode(), users[username].userReceiveAddr)
			## sent all tweets, send Done flag
			users[username].userReceiveSock.sendto("Done".encode(), users[username].userReceiveAddr)
		## get users
		elif keyword == "gu":
			## tell client to wait for users list
			users[username].userReceiveSock.sendto("gu".encode(), users[username].userReceiveAddr)
			## format user string, we can send this all as one message because it'll be a static-ish amount of bytes
			uString = ""
			for user in users.keys():
				uString += user + "\n"
			uString = uString[:len(uString)-1]
			## send users string
			users[username].userReceiveSock.sendto(uString.encode(), users[username].userReceiveAddr)
			## send Done flag
			users[username].userReceiveSock.sendto("Done".encode(), users[username].userReceiveAddr)
		## gettweets
		elif keyword == "gt":
			## wait for which username to get tweets for
			personOfInterest, addr = users[username].userSendSock.recvfrom(1024)
			personOfInterest = personOfInterest.decode()

			## tell request client to wait for tweets
			users[username].userReceiveSock.sendto("gt".encode(), users[username].userReceiveAddr)
			## if personOfInterest exists
			if personOfInterest in users.keys():
				## send True flag
				users[username].userReceiveSock.sendto("True".encode(), users[username].userReceiveAddr)

				## format tString and send each tweet individually
				tString = ""
				for tweet in range(len(users[personOfInterest].tweets)):
					parts = users[personOfInterest].tweets[tweet].split("\"")
					tString = "{}: \"{}\" {}".format(parts[0].strip(),parts[1],parts[2].strip())
					users[username].userReceiveSock.sendto(tString.encode(), users[username].userReceiveAddr)
				## send Done flag
				users[username].userReceiveSock.sendto("Done".encode(), users[username].userReceiveAddr)

			else:
				## else user doesn't exist, tell request client
				users[username].userReceiveSock.sendto("False".encode(), users[username].userReceiveAddr)
				users[username].userReceiveSock.sendto(personOfInterest.encode(), users[username].userReceiveAddr)

		## exit
		if keyword == "exit":
			## delete user, break thread
			del users[username]
			break

## newSock creates new send and receive threads for the new client.
## This is done to make the user switch from the welcome socket to the new socket, otherwise we can't tell between each user
def newSock(s, username, clientAddr):
	## set send socket in user class
	users[username].setSendSocket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
	## bind the send socket
	users[username].userSendSock.bind(("",0))
	## give the send socket to the client
	s.sendto(str(users[username].userSendSock.getsockname()[1]).encode(), clientAddr)

	## if it inits correctly, set the send addr, otherwise exit
	message, addr = users[username].userSendSock.recvfrom(1024)
	if message.decode() == "init":
		users[username].setSendAddr(addr)
	else:
		sys.exit(0)

	## set receive socket in user class
	users[username].setReceiveSocket(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
	## bind receive socket
	users[username].userReceiveSock.bind(("",0))
	## send receive socket to client
	s.sendto(str(users[username].userReceiveSock.getsockname()[1]).encode(), clientAddr)

	## if it inits correctly, set receive addr, otherwise exit
	message, addr = users[username].userReceiveSock.recvfrom(1024)
	if message.decode() == "init":
		users[username].setReceiveAddr(addr)
	else:
		sys.exit(0)



## invoke is the welcome mat of the program. It waits for a new client connection. If the client connection happens, create a thread for the client, create a new user, and give them new sockets
def invoke():
	if len(sys.argv) == 2:
		## Get IP addr of host to print out for clients to connect to.
		HOST_NAME = socket.gethostname()
		SERVER_IP = socket.gethostbyname(HOST_NAME)

		## Check to see if port is a valid int
		try:
			SERVER_PORT = int(sys.argv[1])
			if (SERVER_PORT < 1024):
				raise Exception
			if SERVER_PORT > 65535:
				raise Exception
		except Exception:
			print('error: server port invalid, connection refused.')
			sys.exit(0)


		## Connect to socket
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		## Bind IP address ("" means any address) and port to the socket
		try:
			s.bind(("",SERVER_PORT))
		except:
			print('error: server port invalid, connection refused.')
			sys.exit(0)

		## Server runs forever
		while True:
			try:
				## Receive initial communication from client: username
				message, clientAddr = s.recvfrom(1024)
				keyword = message.decode()

				## receive a new username
				if keyword == "user":
					message, clientAddr = s.recvfrom(1024)
					username = message.decode()
					## check to see if username is valid
					if not createNewClient(username):
						s.sendto("False".encode(), clientAddr)
					else:
						s.sendto("True".encode(), clientAddr)
						## make new user object
						users[username] = User(username)
						## give user object new sockets
						newSock(s, username, clientAddr)

						## make user thread as daemon so it will quit if server crashes
						users[username].setThread(threading.Thread(target=listener, args=(username,), daemon=True))
						users[username].userThread.start()
					

			## CTRL-C, shutdown server
			except KeyboardInterrupt:
				sys.exit(0)
			except:
				sys.exit(0)

	## Incorrect # of arguments for boot, exit
	else:
		sys.exit(0)

if __name__ == "__main__":
	invoke()
