import socket
import sys

## Error Messages
MODE_ERROR = False


MODE_HELP_MESSAGE = """Upload Mode:
\tpython ttweetcli.py - u <ServerIP> <ServerPort> \"message\"
Download Mode:
\tpython ttweetcli.py -d <ServerIP> <ServerPort>\n
***Please do not forget to remove <> characters when typing ServerIP and ServerPort and keep quotations around your message***"""


CHAR_LIMIT_VIOLATION = """You have exceeded the 150 character limit. Please shorten your message by {} character{}."""


## Function Definitions.

## If the server times out
def timeoutHandler():
	print("Socket timed out. Perhaps your IP does not match up with the server...")
	sys.exit(0)

## Upload message to server
##
## ip: the IP of the server being accessed
## port: port of server we are trying to access
## message: client-side user message being uploaded
def uploadMode(ip, port, message):
	## If message does not exceed 150 characters, continue
  if len(message) <= 150:
  	try:
			## Connect to socket
  		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  		## Set socket to timeout after 15 seconds
  		s.settimeout(15)

  		## Check if port is open
  		if s.connect_ex((ip, port)) != 0:
  			print("Port is busy, please enter a different port. Exiting...")
  			sys.exit(0)

  		## Send "-u" as upload signal to socket for server to take specific actions
  		s.sendto("-u".encode(),(ip, port))

  		## Send user message to be stored
  		s.sendto(message.encode(),(ip, port))
  		print("Message Sent.")

  		## Receive acknowledgement from server that message has arrived.
  		newMessage, serverAddr = s.recvfrom(150)
  		decodedMessage = newMessage.decode()
  		if decodedMessage == "ACK":
  			print("Message Stored On Server.")

  		## Close socket
  		s.close()
  	except socket.timeout:
  		timeoutHandler()
  	except ConnectionResetError:
  		print("Server Not Found. Exiting...")
  		sys.exit(0)
  	except:
  		print("Server Not Found. Exiting...")
  		sys.exit(0)

  ## Message has exceeded 150 characters. Print error statement and exit.
  else:
  	plural = ""
  	if len(message) - 150 > 1:
  		plural = "s"
  	print(CHAR_LIMIT_VIOLATION.format(len(message) - 150, plural))
  	sys.exit(0)


def downloadMode(ip, port):
	try:
		## Connect to server via socket
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		## Set socket to timeout after 15 seconds
		s.settimeout(15)

		## Check if port is open
		if s.connect_ex((ip, port)) != 0:
			print("Port is busy, please enter a different port. Exiting...")
			sys.exit(0)

		## Send server signal "-d" for download
		s.sendto("-d".encode(),(ip, port))

		## Receive message from server and print message
		newMessage, serverAddr = s.recvfrom(150)
		decodedMessage = newMessage.decode()
		print("Message Downloaded.")
		print("Message: \"{}\"".format(decodedMessage))
		s.sendto("ACK".encode(),(ip, port))
	except socket.timeout:
		timeoutHandler()
	except ConnectionResetError:
		print("Server Not Found. Exiting...")
		sys.exit(0)
	except:
		print("Server Not Found. Exiting...")
		sys.exit(0)



## Main Program Body

## Check for correct client side argument length. 4 for download, 5 for upload
if len(sys.argv) < 4 or len(sys.argv) > 5:
    print("\nYou've entered an incorrect amount of arguments.\n")
    print(MODE_HELP_MESSAGE)

## Correct # of arguments, proceed
else:
    
  ## Set globals
  SERVER_IP = sys.argv[2]
  ## Check for invalid port
  try:
  	SERVER_PORT = int(sys.argv[3])
  except:
  	print("Invalid port: {}. Exiting...".format(sys.argv[3]))
  	sys.exit(0)

  ## Check for invalid IP
  try:
  	## Checks if values are between 0-255
  	socket.inet_aton(SERVER_IP)
  	## Checks if IP is in the correct format
  	if SERVER_IP.count(".") != 3:
  		raise Exception
  ## Invalid IP, exit
  except Exception:
  	print("Invalid IP: {}. Exiting...".format(SERVER_IP))
  	sys.exit(0)


  ## Upload Mode
  if len(sys.argv) == 5:
    
    ## Check to see client specified upload mode
    if sys.argv[1].lower() == "-u":
    	## Message is the fourth argument
      USER_MESSAGE = sys.argv[4]
      ## Access upload helper function
      uploadMode(SERVER_IP, SERVER_PORT, USER_MESSAGE)
    
    ## Upload mode was not specified with 5 arguments
    else:
      MODE_ERROR = True
  
  ## Download mode
  elif len(sys.argv) == 4:
    
    ## Check to see client specified download mode
    if sys.argv[1].lower() == "-d":
      downloadMode(SERVER_IP, SERVER_PORT)

    ## Download mode was not specified with 4 arguments
    else:
      MODE_ERROR = True
  
  ## Wrong mode was entered. This catches any incorrect second arguments.
  ## Print help message for formatting  
  if MODE_ERROR:
    print("\nYou have chosen the incorrect mode.\n")
    print(MODE_HELP_MESSAGE)