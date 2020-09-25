import socket
import sys

## Error Messages

SERVER_STARTUP_FAILURE = """Invoke Server:
\tpython ttweetser.py <ServerPort>\n
***Please do not forget to remove <> characters when typing ServerPort***"""

## Main Body of Server

## If server was booted with correct # of arguments
if len(sys.argv) == 2:
	## Get IP addr of host to print out for clients to connect to.
	HOST_NAME = socket.gethostname()
	SERVER_IP = socket.gethostbyname(HOST_NAME)

	## Check to see if port is a valid int
	try:
		SERVER_PORT = int(sys.argv[1])
	except:
		print("Invalid port: {}. Exiting...".format(sys.argv[3]))
		sys.exit(0)

	## Set message to default "Empty Message"
	UPLOADED_MESSAGE = "Empty Message"

	## Print port and ip for client to connect to
	print("Please have client connect to IP: {} and PORT: {}".format(SERVER_IP, SERVER_PORT))


	## Connect to socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	## Bind IP address ("" means any address) and port to the socket
	s.bind(("",SERVER_PORT))

	## Server runs forever
	while True:
		try:
			## Receive initial communication from client: "-u" OR "-d"
			message, clientAddr = s.recvfrom(150)
			decodedMessage = message.decode()

			## If client has selected upload mode
			if decodedMessage.lower() == "-u":
				## Receive clients message
				newMessage, clientAddr = s.recvfrom(150)
				UPLOADED_MESSAGE = newMessage.decode()
				print("Message Received And Stored.")
				## Send acknowledgement to client
				s.sendto("ACK".encode(), clientAddr)

			## If client has selected download mode
			elif decodedMessage.lower() == "-d":
				## Send stored message to client
				s.sendto(UPLOADED_MESSAGE.encode(), clientAddr)
				print("Message Sent To Client.")

				## acknowledge
				returnMessage, clientAddr = s.recvfrom(150)
				if returnMessage.decode() == "ACK":
					print("Client Received Message.")
		## CTRL-C, shutdown server
		except KeyboardInterrupt:
			print("Keyboard Interrupt detected. Exiting...")
			sys.exit(0)
		except:
			print("Server crash detected. Exiting...")
			sys.exit(0)

## Incorrect # of arguments for boot, exit
else:
	print("\nYou've entered an incorrect of number arguments.\n")
	print(SERVER_STARTUP_FAILURE)
	sys.exit(0)