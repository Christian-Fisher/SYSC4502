# Import socket module
from socket import *
import sys # In order to terminate the program

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)

serverSocket = socket(AF_INET, SOCK_STREAM)

#Fill in start 
serverSocket.bind(("", 7777))
serverSocket.listen(1)
#Fill in end 

# Server should be up and running and listening to the incoming connections

while True:
	print('The server is ready to receive')

	# Set up a new connection from the client
	connectionSocket, addr = serverSocket.accept()

	# If an exception occurs during the execution of try clause
	# the rest of the clause is skipped
	# If the exception type matches the word after except
	# the except clause is executed
	try:
		# Receives the request message from the client
		message = connectionSocket.recv(1024).decode() 
		
		# print complete message received from browser (for information purposes)
		print (message)
		# Extract the path of the requested object from the message
		# The path is the second part of HTTP header, identified by [1] (when splitting on whitespace)
		filename = message.split()[1]
		# Because the extracted path of the HTTP request includes 
		# a character '\', we read the path from the second character 
		f = open(filename[1:])
		
		# Store the entire content of the requested file in a temporary buffer
		outputdata = f.read() 

		# Send the HTTP response header line to the connection socket
		
		#Fill in start 
		header = f"HTTP/1.1 200 OK\n"
		for char in header:
			connectionSocket.send(char.encode())
		#Fill in end 
		
		# Send the content of the requested file to the connection socket
		for i in range(0, len(outputdata)):  
			connectionSocket.send(outputdata[i].encode())
		connectionSocket.send("\r\n".encode()) 
		
		# Close the client connection socket
		connectionSocket.close()

	except IOError:
		# Send HTTP response message for file not found
		
		#Fill in start 
		print("exception happened")
		header = f"HTTP/1.1 404 Not Found!!\n"
		for char in header:
			connectionSocket.send(char.encode())
		#Fill in end 
		
		# Close the client connection socket
		
		#Fill in start 
		connectionSocket.close()
		break
		#Fill in end 
serverSocket.close()  
sys.exit()#Terminate the program after sending the corresponding data
