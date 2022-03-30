from os import times
import sys
import socket
import json
import random
import struct

def readDataFiles():
        """Function which reads the 3 files and returns a list of the contents which have been
        formatted properly."""
        with open('cache_days.txt') as daysFile:
            days = list(daysFile)
            for index, day in enumerate(days):
                if "\n" in day:
                    days[index]=day[:-1]

        with open('cache_rooms.txt') as roomsFile:
            rooms = list(roomsFile)
            for index, room in enumerate(rooms):
                if "\n" in room:
                    rooms[index]=room[:-1]

        with open('cache_timeslots.txt') as timesFile:
            times = list(timesFile)
            for index, time in enumerate(times):
                if "\n" in time:
                    times[index]=time[:-1]

        return days, rooms, times

def writeDaysBack(days):
    with open("cache_days.txt", 'w') as daysFile:
        for day in days:
            daysFile.write(f"{day}\n")

def writeRoomsBack(rooms):
    with open("cache_rooms.txt", 'w') as roomsFile:
        for room in rooms:
            roomsFile.write(f"{room}\n")

def writeTimesBack(times):
    with open("cache_timeslots.txt", 'w') as timesFile:
        for time in times:
            timesFile.write(f"{time}\n")
def main():

    # Argument Validation section
    if len(sys.argv) != 3:
        print("Please enter a mutlicast host name to send to and port number for the client to bind to.")
        print("Client.py <multicast IP> <port>")
        return

    if not sys.argv[2].isnumeric():
        print("Ensure the port number is actually a number")
        return
     
    # Creating the socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to join the multicast group.
    ttl = struct.pack('b', 1)
    clientSocket.settimeout(15)
    clientSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    try:
        # Attempting to resolve the name given by the user. If this fails, then the name is unknown
        socket.gethostbyname(sys.argv[1])
    except:
        print("Host name given was not valid.")
        return

    # Cache management booleans.
    daysInvalid = True
    roomsInvalid = True
    timesInvalid = True
    # Main loop for the UI
    while True:
        invalidCache = False
        # This print statement clears the terminal screen (Dont ask me how, something to do with \codes)
        print("\033[H\033[J") 
        # Ask the user for a input
        inputCommand = input("""Enter the corresponding number to select a command: 
            1 - Days 
            2 - Rooms
            3 - Timeslots
            4 - Check
            5 - Reserve
            6 - Delete
            7 - Quit\n""")
        commandID = random.randint(0, 100000)
        message = {"commandID": commandID}
        # Based on the input formulate a message to send to the server
        match inputCommand:
            case "1":
                message["command"] = "days"
            case "2":
                message["command"] = "rooms"
            case "3":
                message["command"] = "timeslots"
            case "4":
                room = input("Enter room name to check: ")
                message["command"] = "check"
                message["room"] = room
            case "5":
                room = input("Enter room name to reserve: ")
                timeslot = input("Enter timeslot to reserve: ")
                day = input("Enter which day to reserve on: ")
                message["command"] = "reserve"
                message["room"] = room
                message["day"] = day
                message["timeslot"] = timeslot
                daysInvalid = True
                roomsInvalid = True
                timesInvalid = True
                
            case "6":
                room = input("Enter room name to delete reservation: ")
                timeslot = input("Enter timeslot to delete reservation: ")
                day = input("Enter which day to delete reservation on: ")
                message["command"] = "delete"
                message["room"] = room
                message["day"] = day
                message["timeslot"] = timeslot    
                daysInvalid = True
                roomsInvalid = True
                timesInvalid = True      
            case "7":
                message["command"] = "quit"
            case _:
                    print("not recognized command")
                    continue
        if message["command"] in ["reserve", "delete", "check"]:
            infoInvalid = True
        else:
            infoInvalid = ((message["command"] == "days" and daysInvalid) or (message["command"] == "rooms" and roomsInvalid) or (message["command"] == "timeslots" and timesInvalid))

        if infoInvalid:
            print("Obtaining Info from server")
            jsonMessage = json.dumps(message) 
            # Send the message to the server
            clientSocket.sendto(jsonMessage.encode("utf-8"), (sys.argv[1], int(sys.argv[2])))
        # Wait to see a response. If it times out the server didnt respond correctly.
        
        # The receive is done in a while loop to ensure all server's responses are received. 
        # Once a response with the correct commandID is received, the other responses from servers are irrelevant so they can be ignored.
        waitingForResponse = True
        while(waitingForResponse):
            # If the cache cant help this call, ask the server
            if infoInvalid:
                try:
                    response, addr = clientSocket.recvfrom(1024)
                except:
                    input("No response received from server. Please check server or try again")
                    continue
                returnResponse = json.loads(response.decode("utf-8"))

            else:
                # Get the info from the cache
                if message["command"] != "quit":
                    print("Obtaining Info from cache")
                days, rooms, times = readDataFiles()
                match message['command']:
                    case 'days':
                        success = True
                        data = days
                    case 'timeslots':
                        success = True
                        data = times
                    case 'rooms':
                        success = True
                        data = rooms
                    case 'quit':
                        success = True
                returnResponse = {"commandID": message["commandID"]}
                returnResponse["success"] = success
                returnResponse["data"] = data
            if 'commandID' in returnResponse:
                if returnResponse["commandID"] == commandID:
                    waitingForResponse = False
                    # If there is a success field in the response, a valid response was received. From here any returned data can be displayed.
                    if 'success' in returnResponse:
                        if not returnResponse['success']:
                            input("Command failed")
                            continue
                        if message['command'] == "quit":
                            print("Goodbye")
                            quit()
                        if 'data' in returnResponse:
                            # Read the information from the server response and write it to cache if needed.
                            if message["command"] == "days" and daysInvalid == True:
                                writeDaysBack(returnResponse['data'])
                                daysInvalid = False
                            elif message["command"] == "rooms" and roomsInvalid == True:
                                writeRoomsBack(returnResponse['data'])
                                roomsInvalid = False
                            elif message["command"] == "timeslots" and timesInvalid == True:
                                writeTimesBack(returnResponse["data"])
                                timesInvalid = False
                            for entry in returnResponse['data']:
                                print(entry)
                                        
                            input("Command Successful")
                    else:
                        print("Command failed")
        print("Goodbye")        
if __name__ == "__main__":
    main()