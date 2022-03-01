from socket import *

# Message to send
msg = '\r\nI love computer networks!'
endmsg = '\r\n.\r\n'

# Choose a mail server and call it mailserver
mailserver = '127.0.0.1'

# Create socket called clientSocket and establish a TCP connection with mailserver

#Fill in start   
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, 5555))
#Fill in end 

recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
	print('220 reply not received from server.')

# Send HELO command and print server response.
heloCommand = 'HELO SYSC4502\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print("After HELO " + recv1)
if recv1[:3] != '250':
	print('250 reply not received from server.')

# Send MAIL FROM command and print server response.

#Fill in start   
mailFromCommand = 'MAIL FROM: <test@testing.com>\r\n'
clientSocket.send(mailFromCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print("After MAIL FROM " + recv1)
if recv1[:3] != '250':
	print('250 reply not received from server.')
#Fill in end 

# Send RCPT TO command and print server response. 

#Fill in start   
rcptToCommand = 'RCPT TO: <receipent@testing.com>\r\n'
clientSocket.send(rcptToCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print("After RCPT TO " + recv1)
if recv1[:3] != '250':
	print('250 reply not received from server.')
#Fill in end 

# Send DATA command and print server response. 

#Fill in start   
dataCommand = 'DATA \r\n'
clientSocket.send(dataCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print("After DATA " + recv1)
if recv1[:3] != '354':
	print('354 reply not received from server.')
#Fill in end 

# Send message data.

#Fill in start   
bodyCommand = 'SUBJECT: Greeting To you!\r\n'
clientSocket.send(bodyCommand.encode())
bodyCommand = 'test again'
clientSocket.send(bodyCommand.encode())
bodyCommand = msg
clientSocket.send(bodyCommand.encode())
#Fill in end 

# Message ends with a single period.

#Fill in start   
bodyCommand = endmsg
clientSocket.send(bodyCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
	print('354 reply not received from server.')
#Fill in end 

# Send QUIT command and get server response.

#Fill in start   
quitCommand = "QUIT\r\n"
clientSocket.send(quitCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(f"{recv1}")
if recv1[:3] != '221':
	print('221 reply not received from server.')
#Fill in end 
