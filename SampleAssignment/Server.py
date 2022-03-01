from socket import *
import sys

# read in information one textfile, store and return as one long string
def readTextfile(filename):
    result = ""
    try:
        f = open(filename)
    except:
        print("File ", filename, " does not exist")
        return ""
    for line in f:
        result = result + line
    return result

# write reservations textfile
def writeTextfile(filename, input):
    try:
        f = open(filename, "w")
    except:
        print("File ", filename, " could not be opened for writing")
        return
    for line in input:
        f.write(line + "\n")

# check format of RESERVE and DELETE commands
def checkFormat(cmd_components):
    # check for sufficient fields
    if len(cmd_components) != 4:
        return "Inaccurate number of parameters"
    # check for valid input fields
    if cmd_components[1] not in rooms:
        return cmd_components[1] + " not a valid room"
    if cmd_components[2] not in timeslots:
        return cmd_components[2] + " not a valid timeslot"
    if cmd_components[3] not in days:
        return cmd_components[3] + " not a valid day"
    # if we are here, everything worked out, return okay
    return "okay"

# process a single user command, returning either the result or an appropriate error message
def processCommand(cmd):
    global res
    if cmd == "days":
        return days
    if cmd == "rooms":
        return rooms
    if cmd == "timeslots":
        return timeslots
    if cmd[:5] == "check":
        specific_room = message[6:]
        if specific_room not in rooms:
            return "Room " + specific_room + " not a valid room"
        results = ""
        for r in res:
            components = r.split()
            if components[0] == specific_room:
                if not results == "":
                    results = results + "\n"
                results = results + r 
        if results == "":
            results = "No room reservation found"
        return results
    if cmd[:7] == "reserve":
        cmd_components = cmd.split()
        check_results = checkFormat(cmd_components)
        if not check_results == "okay":
            return check_results

	# check whether reservation already exists
        found = False
        for r in res:
            components = r.split()
            if components[0] == cmd_components[1] and components[1] == cmd_components[2] and components[2] == cmd_components[3]:
                found = True
        if found:
            return "Reservation already exists"
        
        # once we are here, add reservation and return confirmation
        new_res = cmd_components[1] + " " + cmd_components[2] + " " + cmd_components[3]
        res.append(new_res)
        return "Reservation confirmed"
    if cmd[:6] == "delete":
        cmd_components = cmd.split()
        check_results = checkFormat(cmd_components)
        if not check_results == "okay":
            return check_results

        # iterate over all reservations, copy all the ones that are not involved to new_reservations
        found = False
        new_res = []
        for r in res:
            components = r.split()
            if components[0] == cmd_components[1] and components[1] == cmd_components[2] and components[2] == cmd_components[3]:
                found = True
            else:
                new_res.append(r)
        if not found:
            return "Reservation did not exist"

        # we had a proper deletion request, store this as the new set and return a deletion confirmation
        res = new_res
        return "Deletion confirmed"
    if cmd == "quit":
        return "bye"
    # if we get here, the command is unknown, simply return error message
    return cmd + ": Command unknown"

# Get the server port as command line argument and set up server socket
argv = sys.argv
if len(argv ) != 2:
    print("Incorrect number of command-line arguments")
    print("Invoke server with: python", argv[0], "<port>")
    exit()
                     
serverPort = int(argv[1])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

# read in the information in the four input textfiles
rooms = readTextfile("rooms.txt")
days = readTextfile("days.txt")
timeslots = readTextfile("timeslots.txt")
reservations = readTextfile("reservations.txt")
# split reservations into a list for easier handling later
res = reservations.splitlines()

print ("The server is ready to receive")

# main server loop: receive a single datagram with a message/command and act on it
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    message = message.decode()
    answer = processCommand(message)
    serverSocket.sendto(answer.encode(), clientAddress)
 
    # special processing for quit: save back set of reservations and break out of loop
    if message == "quit":
        writeTextfile("reservations.txt", res)
        break

# once we break out of the loop, close socket and terminate
serverSocket.close()
print ("Shutting the server down")
