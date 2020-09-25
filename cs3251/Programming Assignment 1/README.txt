Jared Raiola -- jraiola33@gatech.edu

CS3251 Computer Networks
Programming Assignment 1
2/12/2020

===============================================================================

FILES:
- Sample.txt: This file contains sample output from the program. This output 
	was tested on the shuttle.

- README.txt: This file contains information about the author of the code and
	various information on how to run the code, along with information on the other files and limitations of the program.

- ttweetcli.py: This file contains the client side program. It is heavily 
	commented. The general design structure of this file is a program that takes in output from the commandline and uses the socket library of python to allow a client side to communicate with a server side through the use of a socket. The input is split into two categories, download and upload.
			Download: This encompasses contacting the server to receive the stored message. The arguments include (in order):
				python3 ttweetcli.py -d <ServerIP> <ServerPort>
			Upload: This encompasses contacting the server with a message that is under 150 characters and asking the server to store that message. The arguments include (in order):
				python3 ttweetcli.py -u <ServerIP> <ServerPort> "message"

- ttweetser.py: This file contains the server side program. It is heavily 
	commented. The general design structure of this file is a program that takes in command line input to contact a specified socket on a host address in order to allow the client side to send and receive messages through that socket. The server runs infinitely and iteratively, in order to only deal with a single client at a time and also to give it the ability to store messages without having to input and output to a file.

===============================================================================

HOW TO COMPILE/RUN:
- cd to the correct directory in one terminal

Run:
- python3 ttweetser.py <ServerPort>
	(My server side automatically chooses a host to run on and will print out it's IP for you)

- open another terminal and cd to the correct directory

Run:
- python3 ttweetcli.py -u (or -d) <ServerIP> <ServerPort> "message" (if -u)

- repeat by running the above command with different parameters

===============================================================================

OUTPUT SAMPLE FOR SERVER:
	
	On a boot:
		- Please have client connect to IP: <IP> and PORT: <ServerPort>.

	On incorrect arguments:
		- You've entered an incorrect number of arguments.
		- Invoke Server:
			. python ttweetser.py <ServerPort>
				***Please do not forget to remove <> characters when typing ServerPort***
	
	On an upload:
		- Message Received and Stored.
			. (After printing this message, the server side sends an ACK to the client side)

	On a download:
		- Message Sent To Client.
			. (Client sends ACK to server)
		- Client Received Message.

	On CTRL-C Press:
		- Keyboard Interrupt Detected. Exiting...

	On an improper port:
		- Invalid port: <ServerPort>. Exiting...

	On a server crash:
		- Server crash detected. Exiting...

===============================================================================

PROTOCOL DESCRIPTION: This TCP is an application that allows a client side to pass messages through a socket to a server side which then stores these messages for future use.

My TCP is split into client side and server side.

CLIENT SIDE:
	
	On an upload:
	 	- Input has already been received from the user.
	 	1. The program checks for either 4 or 5 arguments.
	 	2. The program checks for a valid server port integer.
	 	3. The program checks for a valid server IP format.
	 	4. The program checks for 5 arguments passed in.
	 	5. The program checks for -u argument.
	 	6. The program called uploadMode helper.
	 	7. The program checks if length of message exceeds 150 characters.
	 	8. The program sets up the socket and creates a socket timeout.
	 	9. The program checks to see if the port is busy.
	 	10. The program sends -u to the server to put the server into upload mode.
	 	11. The program sends the message to the server.
	 	12. The program receives an ACK from the server.
	 	13. The program closes the socket.

	On a download:
		- Input has already been received from the user.
	 	1. The program checks for either 4 or 5 arguments.
	 	2. The program checks for a valid server port integer.
	 	3. The program checks for a valid server IP format.
	 	4. The program checks for 4 arguments passed in.
	 	5. The program checks for -d argument.
	 	6. The program called downloadMode helper.
	 	7. The program sets up the socket and creates a socket timeout.
	 	8. The program checks to see if the port is busy.
	 	9. The program sends -d to the server to put the server into download mode.
	 	10. The program receives the message from the server.
	 	11. The program sends an ACK to the server.
	 	12. The program closes the socket.

SERVER SIDE:

	On an upload:
		- Input has been received from the user.
		1. The program checks for 2 arguments.
		2. The program calculates the localhost IP to be printed.
		3. The program checks for a valid server port integer.
		4. The program prints out the server IP and PORT.
		5. The program sets up the socket.
		6. The program binds the server to the socket.
		7. The program receives the initial message from the client. In uploads case this is a -u.
		8. The server receives the message from the client.
		9. The server stores the message and sends an ACK.
		10. The server keeps looping until a crash or CTRL-C.

	On a download:
		- Input has been received from the user.
		1. The program checks for 2 arguments.
		2. The program calculates the localhost IP to be printed.
		3. The program checks for a valid server port integer.
		4. The program prints out the server IP and PORT.
		5. The program sets up the socket.
		6. The program binds the server to the socket.
		7. The program receives the initial message from the client. In downloads case this is a -d.
		8. The server sends the message to the client.
		9. The server receives an ACK from the client.
		10. The server keeps looping until a crash or CTRL-C.

===============================================================================

BUGS/LIMITATIONS:
- A major limitation of my program is the inability to allow for multiple
	messages to be sent at the same time and multiple messages to be downloaded at the same time.

- Another major limitation of my program is the inability to direct connect 
	from the client to the server and vice versa, without taking in the IP address and PORT as inputs. In future iterations of this project, something like this would be done dynamically, allowing for address caching for quick 
	connections and dynamically assigning ports to avoiding running into one that is already labeled as "busy".

- A final limitation of my project is the ability to only receive the last
	message that was sent to the server. This could easily be fixed by storing all of the messages in a data structure, but the prompt did not call for that and it would require the client to specify which message in the data structure that they want to receive.

- Potential bugs in my program include: incorrect error handling (in the sense
	of not outputting proper error messages pertaining to the issue), not proper character storage as special ascii character (such as emojis) may not be treated as more than one byte when they potentially should be, and the inability to accept strings that include extra quotations e.g. ""Inside quotes"".