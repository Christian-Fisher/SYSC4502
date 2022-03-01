import json
import sys
import threading
from socket import *
import struct
import random
import time
from typing import Tuple, List

class serverThread (threading.Thread):
    def __init__(self, days, rooms, times, reservations, message, addr, lock) -> None:
        threading.Thread.__init__(self)
        self.days: List = days
        self.rooms: List = rooms
        self.times: List = times
        self.reservations: List = reservations
        self.message = message
        self.addr = addr
        self.lock = lock
    
    def writeReservationsBack(self, reservations):
        """When the program ends, write the reservations back into reservations.txt"""
        print("Saving reservations made to reservations.txt")
        with open('reservations.txt', 'w') as reservationFile:
            for reservation in reservations:
                reservationFile.write(f"{reservation[0]} {reservation[1]} {reservation[2]}\n")

    def getReservationsFromRoom(self, room: str):
        """Function which gets all reservations on a given room"""
        reservationsList = []
        if room not in self.rooms:
            return False, []
        for reservation in self.reservations:
            if reservation[0] == room:
                reservationsList.append(reservation)
        return True, reservationsList

    def reserveRoom(self, room:str, time:str, day:str):
        """Function which reserves a room at a time on a day."""
        self.lock.acquire()
        if room not in self.rooms or day not in self.days or time not in self.times:
            self.lock.release()
            return False
        for reservation in self.reservations:
            if room == reservation[0] and time == reservation[1] and day == reservation[2]:
                self.lock.release()
                return False
        self.writeReservationsBack(self.reservations)
        self.reservations.append([room, time, day])
        self.lock.release()
        return True

    def unreserveRoom(self, room, time, day):
        """Function which deletes a specified reservation from the reservations list"""
        self.lock.acquire()
        if room not in self.rooms or day not in self.days or time not in self.times:
            self.lock.release()
            return False

        for reservation in self.reservations:
            if room == reservation[0] and time == reservation[1] and day == reservation[2]:
                self.reservations.remove(reservation)
                self.writeReservationsBack(self.reservations)
                self.lock.release()
                return True
        self.lock.release()
        return False

    def run(self):
        responseSocket = socket(AF_INET, SOCK_DGRAM)
        # If the command is of valid format
        if "command" in self.message and "commandID" in self.message:
            response = {"commandID": self.message["commandID"]}
            data = ""
            # Choose a response based on the type of command requested.
            match self.message['command']:
                case 'days':
                    success = True
                    data = self.days
                case 'timeslots':
                    success = True
                    data = self.times
                case 'rooms':
                    success = True
                    data = self.rooms
                case 'check':
                    if 'room' in self.message:
                        success, data = self.getReservationsFromRoom(self.message['room'])
                case 'reserve':
                    if 'room' in self.message and 'timeslot' in self.message and 'day' in self.message:
                        success = self.reserveRoom(self.message['room'], self.message['timeslot'], self.message['day'])
                case 'delete':
                    if 'room' in self.message and 'timeslot' in self.message and 'day' in self.message:
                        success = self.unreserveRoom(self.message['room'], self.message['timeslot'], self.message['day'])
                case 'quit':
                    success = True
                case _:
                    print("not recognized command")
                    response = json.dumps({'success': False})
            # Once the response is formulated, send the response to the client.
            response["success"] = success
            response["data"] = data
            response = json.dumps(response)
            time.sleep(random.randint(5, 10))
            responseSocket.sendto(response.encode("utf-8"), self.addr)


        else:
            print("Packet is invalid.")

def main():
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

    threadList = []
    threadLock = threading.Lock()
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
    group = inet_aton("235.1.1.1")
    mreq = struct.pack('4sL', group, INADDR_ANY)
    serverSocket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
    # Reading data files section
    print(f"Server connected to port {sys.argv[1]}. Reading data now")
    days, rooms, times, reservations = readDataFiles()
    print(f"All data read, server is running.")
    quit = False
    # Main loop to wait for client to send.
    i=0
    while not quit:
        i+=1
        # Wait to receive a command
        incomingPacket, addr = serverSocket.recvfrom(1024)
        message = json.loads(incomingPacket.decode("utf-8"))

        # CREATE NEW THREAD, AND EVERYTHING FROM HERE IS IN IT.
        try:
            days, rooms, times, reservations = readDataFiles()
            threadList.append(serverThread(days, rooms, times, reservations, message, addr, threadLock))
            threadList[-1].start()
        except Exception as e:
            print(e)
        for thread in threadList:
            if not thread.is_alive():
                threadList.remove(thread)
        print(threadList)
    # Once the loop is exited, the server is shutting down, so the reservations made/deleted during this time need to be saved back.
    print("Goodbye")
if __name__ == "__main__":
    main()