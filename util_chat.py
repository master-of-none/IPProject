"""
    CS594 - Internet Relay Chat Application
    Authors: Shrikrishna Bhat, Vishrut Sharma
    This is the main interface which handles the connection between client and server.
"""

import socket

MAX_CLIENTS = 30
QUIT_STRING = '<$quit$>'


class Error(Exception):
    """
    Base class for exceptions
    """
    pass


class userNotAvailableError(Error):
    """
    Error raised when user not available
    """
    pass


class noActiveRoomError(Error):
    """
    Error raised when no active rooms available
    """
    pass

def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Server is now listening at: ", address)
    return s


"""
    Here we have defined the class which handles member names and class names
    It also contains various user defined functions to handle the IRC application
"""


class ChatHall:
    def __init__(self):
        self.rooms = {}  # {room_name: Room}
        self.room_member_map = {}  # {memberName-roomName: roomName}
        self.members_map = {}  # {memberName : member}

    # Function to welcome the new client when connected to the server
    @staticmethod
    def welcome_new(new_member):
        new_member.socket.sendall(b'Welcome to the Internet Relay Chat Application.\nEnter your Name:\n')

    # Function to handle the messages
    def msg_handler(self, member, msg):

        # These are the instructions which helps the client how the application works
        instructions = b'Instructions:\n' \
                       + b'[<list>] To list all the available rooms\n' \
                       + b'[<join> room_name] To join/create/switch to a room\n' \
                       + b'[<personal> member_name] To chat Personally with specific user\n' \
                       + b'[<manual>] To show Instructions\n' \
                       + b'[<switch> room_name] To switch a Room\n' \
                       + b'[<leave> room_name] To leave a Room\n' \
                       + b'[<quit>] To Quit from the chat application\n' \
                       + b'Or start typing and Enjoy!' \
                       + b'\n'

        print(member.name + " says: " + msg)
        if "name:" in msg:
            name = msg.split()[1]
            member.name = name
            print("We have a new connection from: ", member.name)
            self.members_map[member.name] = member
            member.socket.sendall(instructions)

        elif "<join>" in msg:
            same_room = False
            if len(msg.split()) >= 2:  # error check
                room_name = msg.split()[1]
                member.currentRoomName = room_name
                if member.name + "-" + room_name in self.room_member_map:  # switching?
                    if self.room_member_map[member.name + "-" + room_name] == room_name:
                        member.socket.sendall(b'You are already present in the room: ' + room_name.encode())
                        same_room = True
                    else:  # switch
                        old_room = self.room_member_map[member.name + "-" + room_name]
                    # self.rooms[old_room].remove_member(member)
                if not same_room:
                    if not room_name in self.rooms:  # new room:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].members.append(member)
                    self.rooms[room_name].welcome_new(member)
                    self.room_member_map[member.name + "-" + room_name] = room_name
                    # if member.name+"-"+member.currentRoomName in self.room_member_map:
                    # print (member.currentRoomName)
                    # sys.stdout.write(member.currentRoomName)
                    # sys.stdout.flush()
                    # print (room_name)
                    # sys.stdout.write(room_name)
                    # sys.stdout.flush()
                    # self.room_member_map.pop(member.name+"-"+member.currentRoomName)
                    # member.currentRoomName = room_name
            else:
                member.socket.sendall(instructions)

        elif "<list>" in msg:
            print(self.rooms)
            print(self.room_member_map)
            self.list_rooms(member)

        elif "<manual>" in msg:
            member.socket.sendall(instructions)

        elif "<leave>" in msg:

            if len(msg.split()) >= 2:  # Checking Error
                leaveRoomName = msg.split()[1]

                if member.name + "-" + leaveRoomName in self.room_member_map:
                    del self.room_member_map[member.name + "-" + member.currentRoomName]
                    self.rooms[leaveRoomName].remove_member(member)
                    print("User: " + member.name + "has left the " + leaveRoomName + "\n")
                    if len(self.rooms[leaveRoomName].members) == 0:
                        del self.rooms[leaveRoomName]
                else:
                    msg = "Oops, You have entered the wrong room name. Please try again.\n"
                    member.socket.sendall(msg.encode())
            else:
                member.socket.sendall(instructions)

        elif "<quit>" in msg:
            member.socket.sendall(QUIT_STRING.encode())
            self.remove_member(member)

        elif "<switch>" in msg:
            if len(msg.split()) >= 2:
                switchRoomName = msg.split()[1]
                #   isRoom = self.room_member_map[member.name+"-"+switchRoomName]
                #   if isRoom == switchRoomName :
                if member.name + "-" + switchRoomName in self.room_member_map:

                    member.currentRoomName = switchRoomName

                else:
                    msg = "You are not in the entered room, Please join using <join> \n"
                    member.socket.sendall(msg.encode())
            else:
                member.socket.sendall(instructions)

        elif "<personal>" in msg:
            if len(msg.split()) >= 2:
                memberName = msg.split()[1]
                try:
                    if memberName in self.members_map:
                        newMember = self.members_map[memberName]
                        personal_room = Room("personal-" + member.name + "-" + memberName)
                        self.rooms["personal-" + member.name + "-" + memberName] = personal_room
                        self.rooms["personal-" + member.name + "-" + memberName].members.append(member)
                        self.rooms["personal-" + member.name + "-" + memberName].members.append(newMember)
                        self.room_member_map[
                            member.name + "-" + "personal-" + member.name + "-" + memberName] = "personal-" + member.name + "-" + memberName
                        # self.rooms[room_name].welcome_new(member)
                        self.room_member_map[
                            memberName + "-" + "personal-" + member.name + "-" + memberName] = "personal-" + member.name + "-" + memberName
                        member.currentRoomName = "personal-" + member.name + "-" + memberName
                        newMember.currentRoomName = "personal-" + member.name + "-" + memberName

                    else:
                        raise userNotAvailableError
                except userNotAvailableError:
                    print("User defined exception here")
                    msg = "Entered user does not exist!!\n"
                    member.socket.sendall(msg.encode())
            else:
                member.socket.sendall(instructions)

        elif not msg:
            self.remove_member(member)

        else:
            # check if in a room or not first
            if member.name + "-" + member.currentRoomName in self.room_member_map:
                self.rooms[self.room_member_map[member.name + "-" + member.currentRoomName]].broadcast(member,
                                                                                                       msg.encode())
            else:
                msg = 'You are currently not present in any room! \n' \
                      + 'Please use [<list>] to see all the available rooms! \n' \
                      + 'Use [<join> room_name] to join a room! \n'
                member.socket.sendall(msg.encode())

    # Function to list all the rooms available
    def list_rooms(self, member):
        try:
            if len(self.rooms) == 0:
                raise noActiveRoomError
            else:
                msg = 'All the rooms available are : \n'
                for room in self.rooms:
                    if 'personal' not in room:
                        print(self.rooms[room].members)

                        msg += room + ": " + str(len(self.rooms[room].members)) + " member(s)\n"
                        for member1 in self.rooms[room].members:
                            msg += member1.name + "\n"
                member.socket.sendall(msg.encode())

        except noActiveRoomError:
            print("User defined no room")
            msg = 'Oops, There are no active rooms available now. Please create your own room.\n' \
                  + 'Use [<join> room_name] to create a room.\n'
            member.socket.sendall(msg.encode())

    def remove_member(self, member):
        if member.name + "-" + member.currentRoomName in self.room_member_map:
            self.rooms[self.room_member_map[member.name + "-" + member.currentRoomName]].remove_member(member)
            del self.room_member_map[member.name + "-" + member.currentRoomName]
        print("ChatMember: " + member.name + " has left\n")


class Room:
    def __init__(self, name):
        self.members = []  # a list of sockets
        self.name = name

    def welcome_new(self, from_member):
        msg = self.name + " welcomes: " + from_member.name + '\n'
        for member in self.members:
            member.socket.sendall(msg.encode())

    def broadcast(self, from_member, msg):
        msg = from_member.name.encode() + b":" + msg
        for member in self.members:
            member.socket.sendall(msg)

    def remove_member(self, member):
        self.members.remove(member)
        leave_msg = member.name.encode() + b"has left the room\n"
        self.broadcast(member, leave_msg)


class ChatMember:
    def __init__(self, socket, name="new", currentRoomName="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.currentRoomName = currentRoomName

    def fileno(self):
        return self.socket.fileno()

