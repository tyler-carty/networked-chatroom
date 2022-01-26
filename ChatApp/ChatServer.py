import threading
import socket
import os
import ChatroomEncryption
from ChatroomEncryption import encryption
from ChatroomEncryption import decryption

# Host and Port information needed to start the server.

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 50000

# Randomized shift value from ChatroomEncryption.py
shift = ChatroomEncryption.random_shift


class Server(threading.Thread):

    """
    Creates instantiation of the server ready to take client connections and broadcast chatroom messages.
    Super allows for the parent class to access methods in the child classes
    """

    # Server is instantiated
    def __init__(self, serv_host, serv_port):
        super().__init__()
        self.connections = []
        self.host = serv_host
        self.port = serv_port

    def run(self):

        """
        Creates the listening socket. A server socket is created for each new client, with that socket
        then being added to an array
        """

        # Creates socket for server to listen
        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Sets socket option to allow reusing of the address
        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Socket is bound to a host/port
        listen_sock.bind((self.host, self.port))

        # Socket begins listening for data
        listen_sock.listen(1)
        print('Listening at', listen_sock.getsockname())

        # Constantly listens for new connections
        while True:

            # Accept the new client's connection
            server_conns, socket_name = listen_sock.accept()
            print('Accepted a new connection from {} to {}'.format(
                server_conns.getpeername(),
                server_conns.getsockname())
            )

            # Create new thread, Start new thread & add thread to active connections list
            client_thread = SocketToClient(server_conns, socket_name, self)
            client_thread.start()
            self.connections.append(client_thread)
            print('Ready to receive messages from', server_conns.getpeername())

            # Send cipher shift value to the client
            client_thread.send(shift)

    def broadcast(self, message, source):

        """
        Sends a message to all connected clients, except the source of the message.
        """

        # For each connection to the server
        for connection in self.connections:
            # If the message is not being sent to its origin client. send it
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):

        """
        Removes a thread from the connections list, therefore meaning no more messages will be sent to it.
        """

        # Removes connection from connection list
        self.connections.remove(connection)


class SocketToClient(threading.Thread):

    """
    Allows for communications with a specific client by creating a socket thread to that client.
    """

    # Creates new socket object
    def __init__(self, server_details, socket_name, active_server):
        super().__init__()
        self.sc = server_details
        self.sockname = socket_name
        self.server = active_server
        self.shift_sent = False

    def run(self):

        """
        Receives and broadcasts data from the client, if the client quits then the socket is closed
        and removed from the list of active connections
        """

        # Constantly checks the state of message receipts
        while True:

            # Tries to retrieve a message from the client
            try:
                message = self.sc.recv(1024).decode('ascii')
            # Breaks out of the message checking state
            except:
                break

            # If a blank message is received, we know that it isn't from the user
            # so break the loop and remove the connection
            if message == '':
                break

            # Decrypts the message that has been retrieved
            local_message = decryption(shift, message)

            # Broadcast message to clients
            print('{} says {!r}'.format(self.sockname, local_message))

            broad_message = encryption(shift, local_message)

            self.server.broadcast(broad_message, self.sockname)

        # Removes the thread from the Server's active connections list if loop broken
        Server.remove_connection(self.server, self)

    def send(self, message):

        """
        Sends a message across the connected server to all clients.
        """

        # Sends cipher across the server
        if not self.shift_sent:
            curr_message = encryption(0, message)
            self.sc.sendall(curr_message.encode('ascii'))
        # Sends message across the server to all clients
        else:
            curr_message = encryption(shift, message)
            self.sc.sendall(curr_message.encode('ascii'))


def exit_server(active_server):

    """
    Allows the server admin to close the server at will. Typing 'q' in the command line will close all
    active connections and exit the application.
    """

    # Constantly checks for server quit command
    while True:

        # Allows command input, checks if command is to quit
        serv_input = input('')
        if serv_input == 'q':

            # Closes all connections and alerts server admin
            print('Closing all connections...')
            for connection in active_server.connections:
                connection.sc.close()
            print('Shutting down the server...')

            # Exits the application
            os._exit(0)


if __name__ == '__main__':

    """
    Instantiates the server with the given host and port.
    """

    # Server object is created and started
    server = Server(host, port)
    server.start()

    # Starts exit server thread
    exit_server = threading.Thread(target=exit_server, args=(server,))
    exit_server.start()
