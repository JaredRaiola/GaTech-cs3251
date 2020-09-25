Trivial Twitter Application

Names: Thomas Slattery & Jared Raiola

DIVISION OF LABOR
- ttweetcli.py : Thomas
- ttweetser.py : Jared
- README.md : Thomas & Jared
- Bug Fixing & Commenting : Thomas & Jared

HIGH LEVEL DESCRIPTION

The client program takes in three arguments from the command line: the server IP address, the 
server port number, and the user's username. If the arguments are entered incorrectly, a useful
error message will be sent to the user and the client program will exit gracefully. The client 
then creates a socket and attempts to connect with the server using the given user inputs. If 
the connection is not successful, an error message is displayed to the user and the client exits. 
If successful, the client sends the username to the server to check if it is taken or available. 
If taken, an error message is displayed and the program exits gracefully. If available, the 
username is assigned to the client by the server. The client program now creates a 'listener' 
thread that will accept messages from the server to the client. The main thread will wait for 
user input at this point.  If any user input argument is entered incorrectly, the client will 
display a helpful message to the user and not send any data to the server. Once user input occurs 
the client will take the necessary actions based on the input keyword, which is the first argument 
entered by the user. Once this happens, the main thread again waits for another user input.

If the keyword 'tweet' is input, the client sends a keyword to the server denoting that a tweet 
will be sent to it. Then, the message and hashtag are sent consecutively to the server. If the 
keyword is 'subscribe' then the client will send a flag denoting a subscription request will be 
sent to the server. The hashtag is sent to the server for it to store for the user. The same 
method is used for the rest of the keywords: 'timeline', 'getusers', 'gettweets', and 'exit'. A 
flag is sent from the client to the server denoting the action request taken by the client's user. 
Any pertinent messages are then sent to the server after the keyword. Besides the 'exit' command, 
where the client program terminates itself, no other action is taken by the client in this main 
thread.

The listener thread in the client uses a separate socket connection with the server. It listens 
for any messages being sent to it from the server. The first message sent to it will contain a 
keyword corresponding to varying commands. If the keyword corresponds to a subscription request, 
the listener thread will receive an additional message that will contain information regarding 
the success of the subscription. If it was successful, a success message is displayed to the 
client's user. If not, the failed hashtag is received, and an error message is displayed. If the 
keyword corresponds to an unsubscription, the client waits to receive a success message and will 
display a message to the user, if so. If not, nothing happens. If the keyword is for a 'gettweets' 
command, the client waits for a message confirming the existence of the requested user. The listener 
thread will receive messages containing tweets from that user if they exist and display them to the 
user. If they don't exist, then an error message is displayed and the listener continues listening 
for a new keyword. If the keyword denotes any of a tweet, get user, or timeline command, then the 
listener thread continues receiving and printing the applicable messages from the server. Once all 
messages have been received, the server will send a message denoting that all messages have been 
sent and the listener thread will stop and continue waiting for a new keyword. The listener thread 
runs indefinitely or until the main thread is terminated.

The server program accepts a port number argument for the server to use. If invalid, the program 
sends an error message and quits. A socket is created and bound to the server's address and port. 
It will then wait for a client program to send it a username. Once received, the program checks 
the username for validity, sends a corresponding message to the client, and waits again. If valid, 
the username is added to a list of current users and two sockets, one for receiving from the client 
and another for sending to the client, and a thread are created for that user. In this thread, the 
server listens for keywords sent from the client's sending socket and takes an appropriate action. 
It will send, to the client's receiving socket, a corresponding keyword for it to take action. If 
a tweet command is sent to the server, it will receive the message and hashtags. It then will send 
the message to every client user subscribed to the hashtag(s). If it is a subscription keyword, the 
server will receive the hashtags to subscribe to the user. It will check that these hashtags haven't 
been subscribed to by the user already and that the user is able to subscribe to more hashtags. If 
the hashtags can be subscribed to, they are stored by the server for this user. If not, a message 
is sent to the client denoting failure. A similar method is employed for unsubscriptions, except the 
server is checking and then unassociating those hashtags from the user. For the timeline command, 
the server sends all tweets contained in the user's timeline to the client. For the get users command, 
the server sends the usernames of all connected users to the client. If the keyword corresponds to a 
get tweets command, the server receives the username of the requested user and sends back all tweets 
from that user if they exist. If not, an error message is sent back. If an exit command keyword is 
received by the server, the server deletes the user and all their data from memory.


PROGRAM REQUIREMENTS:

The following python libraries are required to run our application. 
- socket
- threading
- time
- sys

All four of these libraries are already included in pythons standard library.
If the program does not run because any of these aren't installed, you'll have to reinstall this library or python.


HOW TO RUN APPLICATION:

To start the application, first run the server program.  To do this, enter into the command line:

python3 ttweetser.py <PortNumber>

This will start the server, which is ready to accept clients.
To start a client application, enter the following into the command line:

python3 ttweetcli.py <ServerIP> <ServerPort> <Username>

All three arguments must be entered and if any are of an invalid format for the application, an error 
message will be sent to the user. The username must be unique, no other currently running client may 
have it, and alphanumeric. If the user is able to log into the server, a confirmation message will be sent 
to the user. 

When successful, the client program will now accept user inputs. The following user inputs are keywords and 
have associated functions:

Commands:
- tweet "<Message>" <TweetHashtag>
  - This command sends an input message to the server, forwarding it to every client that is subscribed to its hashtag(s).

- subscribe <Hashtag>
  - This command subscribes the user to the specified hashtag. The client, from this point forward, will receive all tweets associated with that hashtag. 'subscribe #ALL' will subscribe the user to all hashtags and the client will receive all new tweets.
 
- unsubscribe <Hashtag>
  - This command unsubscribes the client from the input  hashtag(s). #ALL serves the same purpose here: all hashtags are unsubscribed from.

- timeline
  - This command will output all tweets that have been sent to the client previously. If no tweets have been sent, nothing will be output.
 
- getusers
  - This command will output the usernames of all clients that are currently online, including the user sending the command.
  
- gettweets <Username>
  - This command will output all tweets that have been sent by the client with <Username>. If no tweets have been sent, nothing will be displayed. If no such <Username> exists, an error message will be printed. 
  
- exit
  - This command will remove the user from the server and close the client connection.

Key Information About Commands:
- <Message> must be in quotes and 150 characters or less
- All hashtags MUST begin with the # character
- <TweetHashtag> can contain multiple hashtags, but each hashtag must be more than 0 characters and all tags combined must be less than 15 characters INCLUDING # counting as a singular character every time it appears
- <Hashtag> can only contain one hashtag total
- <Username> cannot be 0 characters

An error message will be sent to the user if the user formatting of inputs is incorrect and the command will not be executed.

Run any command listed above and run the exit command when finished.
