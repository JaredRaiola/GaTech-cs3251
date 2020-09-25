# Trivial Twitter Client

from socket import *
import sys
import threading


## Error class used to force quit client
class Exit(Exception):
	pass

## Client listener connection
## Acts as a channel for the client to always be able to receive messages from the server
def listener(clientReceiveSocket):
	while True:
		try:
			## Receive keyword describing the operation
			message, serverAddr = clientReceiveSocket.recvfrom(1024)
			keyword = message.decode()

			##Subscription
			if keyword == "sub":
				message, serverAddr = clientReceiveSocket.recvfrom(1024)
				word = message.decode()
				##If successfully subscribed
				if word == "True":
					print('operation success')
				else:
					##If unsuccessful
					message, serverAddr = clientReceiveSocket.recvfrom(1024)
					hashtag = message.decode()
					print('operation failed: sub {} failed, already exists or exceeds 3 limitation'.format(hashtag))
			##Unsubscribe
			elif keyword == "unsub":
				message, serverAddr = clientReceiveSocket.recvfrom(1024)
				word = message.decode()
				##If successful
				if word == "True":
					print('operation success')
				##Else do nothing

			##Get tweets
			elif keyword == "gt":
				message, serverAddr = clientReceiveSocket.recvfrom(1024)
				word = message.decode()
				##If succcessful, loop through until server Done flag
				if word == "True":
					done = False
					while not done:
						message, serverAddr = clientReceiveSocket.recvfrom(1024)
						if message.decode() == "Done":
							done = True
						else:
							print(message.decode())
				else:
					## Else, user doesn't exist
					name, serverAddr = clientReceiveSocket.recvfrom(1024)
					print("no user {} in the system".format(name.decode()))

			## Tweet, Get users, timeline
			elif keyword == "t" or keyword == "gu" or keyword == "tl":
				done = False
				## Receive messages until Done flag
				while not done:
					message, serverAddr = clientReceiveSocket.recvfrom(1024)
					if message.decode() == "Done":
						done = True
					else:
						print(message.decode())
		except:
			pass

## Used to boot up the client side of the server
## Asks the server for sockets
## Allows for user to send commands to the server side and sets up a thread to listen to the server
def invokeClient():
	## Command line arguments must be formatted correctly
	if len(sys.argv) != 4:
		print("error: args should contain <ServerIP>   <ServerPort>   <Username>")
		sys.exit(0)
	try: 
		## Check server arg
		serverIP = sys.argv[1]
		## Checks if values are between 0-255
		inet_aton(serverIP)
		## Checks if IP is in the correct format
		if serverIP.count(".") != 3:
			raise Exception
	except Exception:
		print('error: server ip invalid, connection refused.')
		sys.exit(0)
	# Server Port Input
	try:
		serverPort = int(sys.argv[2])
		## Check to see if server port is in the valid range
		## 1024-65535 was listed in a Piazza post
		if (serverPort < 1024):
			raise Exception
		if serverPort > 65535:
			raise Exception
	except Exception:
		print('error: server port invalid, connection refused.')
		sys.exit(0)
	# Username input    
	try:
		username = sys.argv[3]
	except:
		print('error: username has wrong format, connection refused.')
		sys.exit(0)

	# Check for valid username
	if not(username.isalnum()):
		print('error: username has wrong format, connection refused.')
		sys.exit(0)

	# Create TCP socket
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	# Connect socket to server port
	serverAddr = (serverIP, serverPort)
	try: 
		##Try connection to server
		clientSocket.connect_ex(serverAddr)
	except:
		print('connection error, please check your server: Connection refused')
		sys.exit(0)

	# Check username
	clientSocket.send('user'.encode()) # send username flag to server
	clientSocket.send(username.encode()) # send username to server
	try:
		## Wait for server response
		newMessage, serverAddr = clientSocket.recvfrom(1024)
	except:
		print('connection error, please check your server: Connection refused')
		sys.exit(0)
	## If username is not taken and there are less than 5 clients currently
	if newMessage.decode() == "True":
		##Wait for server to send first new socket. This will be available for the client to send messages to the server listener
		newMessage, serverAddr = clientSocket.recvfrom(1024)
		decodedMessage = newMessage.decode()

		## Establish client send socket with server side listener
		clientSendSocket = socket(AF_INET, SOCK_DGRAM)
		clientSendSocket.connect_ex((serverIP, int(decodedMessage)))
		clientSendSocket.send("init".encode())

		## Wait for the server to send the second new socket. This will be available for the client to receive messages from
		newMessage, serverAddr = clientSocket.recvfrom(1024)
		decodedMessage = newMessage.decode()

		# Establish client receive socket with the server
		clientReceiveSocket = socket(AF_INET, SOCK_DGRAM)
		clientReceiveSocket.connect_ex((serverIP, int(decodedMessage)))
		clientReceiveSocket.send("init".encode())

		## Create client listener thread as a daemon so it will close when the client side closes
		clientThread = threading.Thread(target=listener, args=(clientReceiveSocket,), daemon=True)
		clientThread.start()

		## Username is legal and everything is setup
		print("username legal, connection established.")

		## Client side, listen to user input
		while(True):
			try:
				# User Input
				userInput = input() # allow keyboard input from user
				if userInput == "":
					continue
				inputList = userInput.split() # list of "arguments"
				keyword = inputList[0]
				# tweet
				if keyword == 'tweet':
					## Check formatting
					## Two "" must be in the input
					if userInput.count("\"") != 2:
						print("message format illegal.")
						continue
					## Remove the flag tweet and the first quote
					userInput = userInput.replace("tweet \"", "")
					##Split the rest of the message at the second quote
					message, hashtag = userInput.split("\"")
					## Remove extra whitespace
					hashtag = hashtag.strip()
					##Check message length
					if (len(message) > 150):
						print('message length illegal, connection refused.')
						continue
					if (len(message) <= 0 or message == None):
						print("message format illegal.")
						continue

					## Check hashtag length
					if len(hashtag) > 15:
						print('hashtag illegal format, connection refused.')
						continue
					## Split into separate hashtags
					hashtagCheck = hashtag.split('#')
					hashtagCheck = hashtagCheck[1:]
					# check hashtag format
					# make sure "ALL" isn't a tweet hashtag.
					# make sure a hashtag isn't of length 0
					for h in hashtagCheck:
						if len(h) == 0 or h == "ALL":
							print("hashtag illegal format, connection refused.")
							continue
						for i in h:
							if not(i.isalnum()):
								print('hashtag illegal format, connection refused.')
								continue

					# tell server it's a tweet
					clientSendSocket.send('t'.encode())
					# send tweet
					clientSendSocket.send(message.encode())
					# send hashtag
					clientSendSocket.send(hashtag.encode())

				# (un)subscribe
				elif keyword == 'subscribe' or keyword == 'unsubscribe':
					hashtag = inputList[1]
					## check hashtag formatting, error if there is more than one hashtag or formatted incorrectly
					if not(hashtag[1:].isalnum()) or hashtag[0] != '#' or hashtag.count('#') != 1 or " " in hashtag:
						print('hashtag illegal format, connection refused.')
						continue
					
					# send correct flag to server
					if keyword == 'subscribe':
						clientSendSocket.send('sub'.encode())
						clientSendSocket.send(hashtag.encode())
					else:
						clientSendSocket.send('unsub'.encode())
						# send hashtag to server
						clientSendSocket.send(hashtag.encode())  

				# timeline
				elif keyword == 'timeline':
					# send timeline flag to server
					clientSendSocket.send('tl'.encode())

				# getusers
				elif keyword == 'getusers':
					# send getusers flag to server
					clientSendSocket.send('gu'.encode())

				# gettweets
				elif keyword == 'gettweets':
					# send gettweets flag to server
					clientSendSocket.send('gt'.encode())
					## send gettweets username to the server
					clientSendSocket.send(inputList[1].encode())

				# exit
				elif keyword == 'exit':
					# send exit flag to server
					clientSendSocket.send('exit'.encode())
					print('bye bye')
					raise Exit
			## Except blocks to handle all exiting, tell server to delete user and exit
			except KeyboardInterrupt:
				clientSendSocket.send('exit'.encode())
				sys.exit(0)
			except Exit:
				clientSendSocket.send('exit'.encode())
				sys.exit(0)
			except:
				clientSendSocket.send('exit'.encode())
				sys.exit(0)
	else:
		print("username illegal, connection refused.")
		sys.exit(0)


## Run invoke client when program is launched
if __name__ == "__main__":
	invokeClient()
