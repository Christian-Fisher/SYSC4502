import json
import sys
import threading
from socket import *
import struct
import random
import time
from typing import List

class heartbeatSender(threading.Thread):
    def __init__(self, myAddr, myPort, serverID, currentCoord: List) -> None:
        threading.Thread.__init__(self)
        self.heartbeatSocket = socket(AF_INET, SOCK_DGRAM)
        self.heartbeatSocket.settimeout(1)
        self.toServerGroup = (myAddr, int(myPort))
        self.serverID = serverID   
        self.currentCoord = currentCoord

    def run(self):
        heartbeat = {"command": "heartbeat", "commandID": self.serverID}
        heartbeatJSON = json.dumps(heartbeat)
        # Only sends a heartbeat if the current server is the leader. Else do nothing
        while True:
            if self.currentCoord[0] == self.serverID and self.currentCoord[0] != 0:
                time.sleep(2)
                self.heartbeatSocket.sendto(heartbeatJSON.encode(), self.toServerGroup)
            else:
                time.sleep(1)
            
class heartbeatReceiver(threading.Thread):
    def __init__(self, myAddr, myPort, serverID, currentCoord: List) -> None:
        threading.Thread.__init__(self)

        # Server socket section
        self.heartbeatRecevierSocket = socket(AF_INET, SOCK_DGRAM) 
        self.heartbeatRecevierSocket.bind(("", int(myPort)))
        # Adding the server to the multicast group
        group = inet_aton(myAddr)
        mreq = struct.pack('4sL', group, INADDR_ANY)
        self.heartbeatRecevierSocket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        self.serverID = serverID   
        self.responseSocket = socket(AF_INET, SOCK_DGRAM)
        self.heartbeatRecevierSocket.settimeout(3)
        self.currentCoord = currentCoord
        self.toServerGroup = (myAddr, int(myPort))


    def run(self):
        Election = {"command": "election", "commandID": self.serverID}
        electionJSON = json.dumps(Election)
        electionIsHappening = False
        waitingForOtherVictory = False
        # If this server just started up, call for an election
        if self.currentCoord[0] == 0:
            self.responseSocket.sendto(electionJSON.encode("utf-8"), self.toServerGroup)
            self.currentCoord[0] = 0
            print(f"Server {self.serverID} called an election")
            electionIsHappening = True

        while True:
            try:
                # Receive messages
                heartbeat = self.heartbeatRecevierSocket.recv(1024)
                heartbeatMessage = json.loads(heartbeat.decode("utf-8"))
                # If its a heartbeat ignore it and continue
                if heartbeatMessage["command"] == "heartbeat":
                        pass
                # If its a heartbeat but we are in an election, ignore it as well
                elif heartbeatMessage["command"] == "heartbeat" and waitingForOtherVictory:
                    raise Exception("We are the coordinator now")
                # If the message is an election message, not from itself, send back an election message if this server should be the leader
                elif heartbeatMessage["command"] == "election" and heartbeatMessage["commandID"] != self.serverID:
                    print(f"Server {heartbeatMessage['commandID']} called an election")
                    electionIsHappening = True
                    self.currentCoord[0] = 0
                    if self.serverID < heartbeatMessage["commandID"]:
                        self.responseSocket.sendto(electionJSON.encode("utf-8"), self.toServerGroup )
                    else:
                        waitingForOtherVictory = True
                # If a server wins, send a victory message to all servers
                elif heartbeatMessage["command"] == "newCoord" and heartbeatMessage["commandID"] != self.serverID:
                    self.currentCoord[0] = heartbeatMessage["commandID"]
                    # Swap leaders to this leader
                    print(f"Leader is now {self.currentCoord[0]}") 
                    waitingForOtherVictory = False
                    electionIsHappening = False

            except Exception as s:
                # This server won, and it should send a message to all other servers telling them it won
                if electionIsHappening and not waitingForOtherVictory:
                    gotElected = {"command": "newCoord", "commandID": self.serverID}
                    newCoordJSON = json.dumps(gotElected)
                    self.responseSocket.sendto(newCoordJSON.encode(), self.toServerGroup)
                    self.currentCoord[0] = self.serverID
                    print(f"Leader is now {self.currentCoord[0]}")
                    waitingForOtherVictory = False
                    electionIsHappening = False
                # Send a election message since the heartbeat stopped.
                elif not waitingForOtherVictory:
                    self.responseSocket.sendto(electionJSON.encode("utf-8"), self.toServerGroup)
                    electionIsHappening = True

            time.sleep(random.random())
class serverThread (threading.Thread):
    """A class which handles a server interaction. The state of the server is passed to this class when a request is received.
    If changes are made, these are written back to the file before the thread the class is running in is done."""
    def __init__(self, days, rooms, times, reservations, message, addr, lock, currentCoord, serverID) -> None:
        threading.Thread.__init__(self)
        self.days: List = days
        self.rooms: List = rooms
        self.times: List = times
        self.reservations: List = reservations
        self.message = message
        self.addr = addr
        self.lock = lock
        self.currentCoord = currentCoord
        self.serverID = serverID
    
    def writeReservationsBack(self, reservations):
        """When the program ends, write the reservations back into reservations.txt"""
        print("     Saving reservations changes to reservations.txt")
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
            print(reservation)
            if room == reservation[0] and time == reservation[1] and day == reservation[2]:
                self.lock.release()
                return False
        self.reservations.append([room, time, day])
        self.writeReservationsBack(self.reservations)
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
            print(f"Handing request {self.message}")
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
            # Simulating processing time with a random wait between 5 and 10 seconds.
            time.sleep(random.randint(5, 10))
            if self.currentCoord == self.serverID:
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
    if len(sys.argv) < 3:
        print("Please enter a multicast address and port number for the server to bind to.")
        print("Server.py <multicast IP> <port>")
        return

    if not sys.argv[2].isnumeric():
        print("Ensure the port number is actually a number")
        return 

    # Server socket section
    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(("", int(sys.argv[2])))
    # Adding the server to the multicast group
    group = inet_aton(sys.argv[1])
    mreq = struct.pack('4sL', group, INADDR_ANY)
    serverSocket.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
    # Start the server with a random or preset ID
    if len(sys.argv) == 4:
        serverID = int(sys.argv[3])
    else:
        serverID = random.randint(-10000, 0)
    currentCoord = [0]
    # Reading data files section
    print(f"Server connected to address {sys.argv[1]} on port {sys.argv[2]}.")
    print(f"{serverID=}")
    # Start up heartbeats
    heartbeatSender(sys.argv[1], 12234, int(serverID), currentCoord).start()
    heartbeatReceiver(sys.argv[1], 12234, int(serverID), currentCoord).start()
    
    # Main loop to wait for client to send.
    i=0
    while True:
        i+=1
        # Wait to receive a command
        incomingPacket, addr = serverSocket.recvfrom(1024)
        message = json.loads(incomingPacket.decode("utf-8"))
        # Once there is a request, create a new thread to handle it.
        try:
            days, rooms, times, reservations = readDataFiles()
            threadList.append(serverThread(days, rooms, times, reservations, message, addr, threadLock, serverID, currentCoord[0]))
            threadList[-1].start()
        except Exception as e:
            print(e)
        for thread in threadList:
            if not thread.is_alive():
                # Remove threads that are no longer being used.
                threadList.remove(thread)
if __name__ == "__main__":
    main()