from socket import *
import sys
import traceback

if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
	sys.exit(2)
	
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(("", 11234))
tcpSerSock.listen(1)

while 1:
	# Start receiving data from the client
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('Received a connection from:', addr)
	message = tcpCliSock.recv(1024).decode()
	# suppress processing of requests for favicon
	if message.split()[1] == "/favicon.ico":
		print("Suppress request for favicon")
		continue
	filename = message.split()[1].partition("/")[2]
	fileExist = "false"
	filetouse = "/" + filename.replace("/","-")
	print("File to use " + filetouse)
	try:
		# Check wether the file exist in the cache
		f = open(filetouse[1:], "r")                      
		outputdata = f.readlines()                        
		fileExist = "true"
		print("Service file from cache")
		# ProxyServer finds a cache hit and generates a response message
		tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())            
		tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())

		# Send the content of the requested file to the connection socket
		for i in range(0, len(outputdata)):  
			tcpCliSock.send(outputdata[i].encode())
		tcpCliSock.send("\r\n".encode())


	# Error handling for file not found in cache
	except IOError:
		if fileExist == "false": 
			# Create a socket on the proxyserver
			c = socket(AF_INET, SOCK_STREAM)
			hostn = filename.split("/")[0].replace("www.","",1)         
			print("Host " + hostn)                                   
			try:
				# Connect to the socket to port 80
				c.connect((gethostbyname(hostn), 80))
				message = "GET "+"http://" + filename + " HTTP/1.0\r\n\r\n"
				c.send(message.encode())  
				# Read the response into buffer
				buffer = c.recv(1024).decode()
				# Create a new file in the cache for the requested file. Also send the response in the buffer to client socket and the corresponding file in the cache
				tmpFile = open("./" + filetouse,"w")
				tmpFile.write(buffer)
				tmpFile.close()
				tcpCliSock.send(buffer.encode())
				
			except:
				print("Illegal request")
				traceback.print_exc()                                              
		else:
			# HTTP response message for file not found
			# Send HTTP response message for file not found
			print("File not found")
			c.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
			c.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
			# Close the client connection socket
			c.close()

	
	# Close the client and the server sockets    
	tcpCliSock.close() 

# Fill in start

# Fill in end
