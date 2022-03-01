import json
import sys
from socket import *

def readDataFiles():
    """Function which reads the 4 files and returns a list of the contents which have been
    formatted properly."""
    with open('days.txt') as daysFile:
        days = list(daysFile)
        for index, day in enumerate(days):
            if "\n" in day:
                days[index]=day[:-1]

    with open('rooms.txt') as roomsFile:
        rooms = list(roomsFile)
        for index, room in enumerate(rooms):
            if "\n" in room:
                rooms[index]=room[:-1]

    with open('timeslots.txt') as timesFile:
        times = list(timesFile)
        for index, time in enumerate(times):
            if "\n" in time:
                times[index]=time[:-1]

    with open('reservations.txt') as reservationFile:
        reservations = list(reservationFile)
        for index, reservation in enumerate(reservations):
            if "\n" in reservation:
                reservations[index]=reservation[:-1]
            reservations[index] = reservations[index].split(" ")

    return days, rooms, times, reservations

def writeReservationsBack(reservations):
    """When the program ends, write the reservations back into reservations.txt"""
    print("Saving reservations made to reservations.txt")
    with open('reservations.txt', 'w') as reservationFile:
        for reservation in reservations:
            reservationFile.write(f"{reservation[0]} {reservation[1]} {reservation[2]}\n")
def main():

    def getReservationsFromRoom(room: str):
        """Function which gets all reservations on a given room"""
        reservationsList = []
        if room not in rooms:
            return False, []
        for reservation in reservations:
            if reservation[0] == room:
                reservationsList.append(reservation)
        return True, reservationsList

    def reserveRoom(room:str, time:str, day:str):
        """Function which reserves a room at a time on a day."""
        if room not in rooms or day not in days or time not in times:
            return False
        for reservation in reservations:
            if room == reservation[0] and time == reservation[1] and day == reservation[2]:
                return False
            
        reservations.append([room, time, day])
        return True

    def unreserveRoom(room, time, day):
        """Function which deletes a specified reservation from the reservations list"""
        if room not in rooms or day not in days or time not in times:
            return False

        for reservation in reservations:
            if room == reservation[0] and time == reservation[1] and day == reservation[2]:
                reservations.remove(reservation)
                return True
        return False

    # Argument Validation section
    if len(sys.argv) != 2:
        print("Please enter a port number for the server to bind to. No other options are available.")
        return

    if not sys.argv[1].isnumeric():
        print("Please enter a port number for the server to bind to. No other options are available.")
        return 
    # Server socket section
    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(("", int(sys.argv[1])))

    # Reading data files section
    print(f"Server connected to port {sys.argv[1]}. Reading data now")
    days, rooms, times, reservations = readDataFiles()
    print(f"All data read, server is running.")
    quit = False
    # Main loop to wait for client to send.
    while not quit:
        # Wait to receive a command
        incomingPacket, addr = serverSocket.recvfrom(1024)
        print(incomingPacket)
        message = json.loads(incomingPacket.decode("utf-8"))
        # If the command is of valid format
        if "command" in message:
            # Choose a response based on the type of command requested.
            match message['command']:
                case 'days':
                    response = json.dumps({'success': True, 'data': days})
                case 'timeslots':
                    response = json.dumps({'success': True, 'data': times})
                case 'rooms':
                    response = json.dumps({'success': True, 'data': rooms})
                case 'check':
                    if 'room' in message:
                        success, reservationsList = getReservationsFromRoom(message['room'])
                        response = json.dumps({'success': success, 'data': reservationsList})
                case 'reserve':
                    if 'room' in message and 'timeslot' in message and 'day' in message:
                        success = reserveRoom(message['room'], message['timeslot'], message['day'])
                        response = json.dumps({'success': success})
                case 'delete':
                    if 'room' in message and 'timeslot' in message and 'day' in message:
                        success = unreserveRoom(message['room'], message['timeslot'], message['day'])
                        response = json.dumps({'success': success})
                case 'quit':
                    quit = True
                    response = json.dumps({'success': True})
                case _:
                    print("not recognized command")
                    response = json.dumps({'success': False})
            # Once the response is formulated, send the response to the client.
            serverSocket.sendto(response.encode("utf-8"), addr)
        else:
            print("Packet is invalid.")
    # Once the loop is exited, the server is shutting down, so the reservations made/deleted during this time need to be saved back.
    writeReservationsBack(reservations)
    print("Goodbye")
if __name__ == "__main__":
    main()