import time
import sys
from socket import * 


# Create a UDP socket  
# Notice the use of SOCK_DGRAM for UDP packets 
clientSocket = socket(AF_INET, SOCK_DGRAM) 

# Assign IP address and port number to socket 
clientSocket.bind(('', 12001)) 
# Set the timeout to 1 second.
clientSocket.settimeout(1)

# Get the IP and port from the command line.
serverIP = str(sys.argv[1])
serverPort = int(sys.argv[2])

for i in range(10):
    # Send the message
    sendMessage = "Test"
    clientSocket.sendto(str.encode(sendMessage), (serverIP, serverPort))
    print(f"Sent: {sendMessage}")
    # Save the time of sending for RTT Calculated
    sentTime = time.time()

    # Wait to receive a response.
    try:
        # Wait for a response for timeout seconds.
        message, address = clientSocket.recvfrom(1024)
        # If a response is found, save the time it was recevied
        receviedTime = time.time()
    except:
        # If no response is received in 1 second, the packet is lost.
        print("Request timed out.\n")
        continue

    # Print the reply info and RTT calculation.
    print(f"Reply from: {address[0]}: {message.decode()} {time.ctime(receviedTime)}")
    print(f"RTT = {(receviedTime-sentTime):.2f}\n")
