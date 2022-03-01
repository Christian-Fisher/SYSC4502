from socket import *
import sys

# Get the server hostname and port as command line arguments
argv = sys.argv                      
if len(argv ) != 3:
    print("Incorrect number of command-line arguments")
    print("Invoke client with: python", argv[0], "<ServerIP> <port>")
    exit()

host = argv[1]
port = int(argv[2])

clientSocket = socket(AF_INET, SOCK_DGRAM)
# Set socket timeout as 1 second
clientSocket.settimeout(1)

while True:

    message = input("Next command:")

    try:
        clientSocket.sendto(message.encode(), (host, port))
        reply, serverAddress = clientSocket.recvfrom(2048)
        reply = reply.decode()
        print(reply)
        if message == "quit":
            break
    except:
        print("Message to server timed out, please retry")

# once we break out of the loop, close socket and terminate
clientSocket.close()
