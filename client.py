"""
    CS594 - Internet Relay Chat Application
    Authors: Shrikrishna Bhat, Vishrut Sharma
    This is the Client Program to connect to the server
"""

import select
import socket
import sys
import util_chat

"""

1) The select() module provides access to platform-specific I/O monitoring functions. Python’s select() function is a 
direct interface to the underlying operating system implementation. It monitors sockets, open files, and pipes until 
they become readable or writable, or a communication error occurs. select() makes it easier to monitor multiple 
connections at the same time, and is more efficient than writing a polling loop in Python using socket timeouts, 
because the monitoring happens in the operating system network layer, instead of the interpreter.

2) Socket programming is started by importing the socket library and making a simple socket. 

3) The python sys module provides functions and variables which are used to manipulate different parts of the Python 
Runtime Environment. It lets us access system-specific parameters and functions. 

"""

READ_BUFFER = 1000

# Creating the socket here
server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_connection.connect(('127.0.0.1', 5005))  # We are connecting to the server here

print("Successfully Connected to the Server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_connection]


def prompt():
    sys.stdout.write('<Me>')
    sys.stdout.flush()


class Error(Exception):
    """
    Base class for exceptions
    """
    pass


class ServerNotAvailableError(Error):
    """
    Error raised when server not available
    """
    pass


try:
    while True:
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for s in read_sockets:

            if s is server_connection:  # Getting the messages
                msg = s.recv(READ_BUFFER)
                if not msg:
                    # print("Oops, Server is down Right Now !!!")
                    raise ServerNotAvailableError
                    # sys.exit(2)
                else:
                    if msg == util_chat.QUIT_STRING.encode():
                        # Incoming message from server
                        sys.stdout.write('Exiting the Server\n')  # Exiting the server
                        sys.exit(2)
                    else:
                        sys.stdout.write(msg.decode())
                        if 'Enter your Name' in msg.decode():
                            msg_prefix = 'name: '  # Name Identifier
                        else:
                            msg_prefix = ''
                        prompt()

            else:
                msg = msg_prefix + sys.stdin.readline()
                server_connection.sendall(msg.encode())

except ServerNotAvailableError:
    # print("In the exception")
    print("Oops, Server is down Right Now !!!")
    sys.exit(2)

finally:
    sys.exit(2)
