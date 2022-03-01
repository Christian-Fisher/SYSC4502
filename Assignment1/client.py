import sys
import socket
import json
def main():

    # Argument Validation section
    if len(sys.argv) != 3:
        print("Please enter a port number for the client to bind to, and a host name to send to.")
        return

    if not sys.argv[2].isnumeric():
        print("Please enter a port number for the server to bind to. No other options are available.")
        return
     
    # Creating the socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.settimeout(5)
    try:
        # Attempting to resolve the name given by the user. If this fails, then the name is unknown
        socket.gethostbyname(sys.argv[1])
    except:
        print("Host name given was not valid.")
        return
    # Bind the socket to the port given
    clientSocket.bind(("", int(sys.argv[2])))
    
    # Main loop for the UI
    while True:
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

        # Based on the input formulate a message to send to the server
        match inputCommand:
            case "1":
                message = {"command": "days"}
            case "2":
                message = {"command": "rooms"}
            case "3":
                message = {"command": "timeslots"}
            case "4":
                room = input("Enter room name to check: ")
                message = {"command": "check", "room": room}
            case "5":
                room = input("Enter room name to reserve: ")
                timeslot = input("Enter timeslot to reserve: ")
                day = input("Enter which day to reserve on: ")
                message = {"command": "reserve", "room": room, "timeslot": timeslot, "day": day}
            case "6":
                room = input("Enter room name to delete reservation: ")
                timeslot = input("Enter timeslot to delete reservation: ")
                day = input("Enter which day to delete reservation on: ")
                message = {"command": "delete", "room": room, "timeslot": timeslot, "day": day}
            case "7":
                message = {"command": "quit"}
            case _:
                    print("not recognized command")
                    continue

        jsonMessage = json.dumps(message) 
        # Send the message to the server
        clientSocket.sendto(jsonMessage.encode("utf-8"), (sys.argv[1], 1200))
        # Wait to see a response. If it times out the server didnt respond correctly.
        try:
            response, addr = clientSocket.recvfrom(1024)
        except:
            input("No response received from server. Please check server or try again")
            continue
        returnResponse = json.loads(response.decode("utf-8"))
        # If there is a success field in the response, a valid response was received. From here any returned data can be displayed.
        if 'success' in returnResponse:
            if not returnResponse['success']:
                input("Command failed")
                continue
            if message['command'] == "quit":
                break
            if 'data' in returnResponse:
                for entry in returnResponse['data']:
                    print(entry)
                input("Command Successful")
        else:
            print("Command failed")
    print("Goodbye")        
if __name__ == "__main__":
    main()