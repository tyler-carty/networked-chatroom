import threading
import socket
import os
import tkinter as tk
from ChatroomEncryption import encryption
from ChatroomEncryption import decryption

# Host and Port information needed to start the server.
host = input("Enter the host IP address: ")
port = 50000


class Receive(threading.Thread):

    """
    An instance of this sending thread class is created, listening for incoming messages from
    the server. Super() allows access to the child classes from the parent class and reduces redundancy
    """

    # instantiation of receiving thread
    def __init__(self, recv_sock, recv_name):
        super().__init__()
        self.sock = recv_sock
        self.name = recv_name
        self.messages = None

    def run(self):

        """
        Receives data from the server and displays it in the TKINTER GUI. This will always listen for
        incoming data until either the client or server has closed the socket. This listen includes all
        messages including ones from the server directly or from other clients that is being relayed
        """

        # Constantly checks for messages
        while True:

            try:
                # Receives and decrypts the message
                message = self.sock.recv(1024).decode('ascii')
            except:
                break

            local_message = decryption(Client.shift, message)

            # Save message in the messages array
            if self.messages:
                self.messages.insert(tk.END, local_message + "\n")


class Client:

    """
    This class allows integration of the client/server communication with the GUI created using TKINTER
    which means that a much more user-friendly experience is created, rather than constantly using a command
    line interface
    """

    # Declares shift variable
    shift = 0

    # Creates instance of client
    def __init__(self, client_host, client_port):
        self.host = client_host
        self.port = client_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None

    def start(self):

        """
        Establishes the client-server connection and asks the user to input their choice for
        the username, then it creates and starts the Send and Receive threads, and notifies other
        connected clients of the new user. Connection feedback is printed directly to the CMD to
        allow the user to check connection status without the GUI being cluttered by connection status messages.
        """

        # Attempts connection to server
        print()
        print('Attempting connection to {} : {}...'.format(self.host, self.port))

        # Times out after 5 seconds if connection is not found
        self.sock.settimeout(5)

        try:
            self.sock.connect((self.host, self.port))
        # If connection fails, tries again
        except:
            print('Could not establish connection to {} : {} \n'.format(self.host, self.port))

            host = input("Enter the host IP address: ")
            port = 50000
            client_gui(host, port)

        # Times out after 240 seconds if messages are not sent
        self.sock.settimeout(240)

        # Acknowledges connection
        print('Successfully connected to {} : {}'.format(self.host, self.port))

        # Receive, decode and decrypt shift value for use in future
        shift_recv = self.sock.recv(1024)
        Client.shift = shift_recv.decode("ascii")
        Client.shift = decryption(0, Client.shift)

        # Prompts user for name
        print()
        self.name = input('Enter your name: ')

        # Acknowledges user choice
        print()
        print('Hello, {}! Starting Chatroom Now...'.format(self.name))

        # Create receive thread.
        # Uses the correct socket for this client as well as the name the user chose.
        receive = Receive(self.sock, self.name)

        # Start receive thread
        receive.start()

        # Notify server that someone has joined the chatroom
        curr_message = ('Server: {} has joined the chatroom!'.format(self.name))
        curr_message = encryption(Client.shift, curr_message)
        self.sock.sendall(curr_message.encode('ascii'))

        # Returns the reception thread to be used in the GUI
        return receive

    def send(self, text_input):

        """
        Sends text data from the GUI entry box. This method is bound to the send button.
        """

        # Gets text entry from the box, then empties the box
        message = text_input.get()
        text_input.delete(0, tk.END)

        # Stops empty messages
        if message != '':

            # Inserts message, with the correct format for display, into a messages array
            self.messages.insert(tk.END, '{}: {}'.format(self.name, message + "\n"))

            # Send message to server for broadcasting
            curr_message = ('{}: {}'.format(self.name, message))
            curr_message = encryption(Client.shift, curr_message)
            self.sock.sendall(curr_message.encode('ascii'))

    def quit(self):

        """
        Quits chatroom using GUI button. The server then sends a message to every client to
        let them know who has left the server. The client socket is closed.
        """

        # Server is told that this client has left the chatroom
        curr_message = ('Server: {} has left the chatroom!'.format(self.name))
        curr_message = encryption(Client.shift, curr_message)
        self.sock.sendall(curr_message.encode('ascii'))

        # Socket is closed for this client
        self.sock.close()
        print("Disconnecting from server...")

        # Application is quit
        os._exit(0)


def client_gui(host, port):

    """
    Initializes and runs the GUI application ready for message entries from the user.
    """

    # Create and start a client thread
    client = Client(host, port)
    receive = client.start()

    # Create a new Tkinter window with geometry for a suitable size
    window = tk.Tk()
    window.configure(bg="#1EA1A1")
    window.geometry("500x430")
    window.minsize(500, 430)
    window.title('Chatroom')

    # Label for the title of the chatroom
    lbl_title = tk.Label(
        master=window,
        text="Welcome to the Chatroom, " + client.name,
        bg="#1EA1A1",
        fg="#FFFFFF",
        font=("Courier", 18)
    )
    lbl_title.grid(row=0, column=0, columnspan=3, sticky="nsew")

    # Create new frame for message handling, child to the window
    frm_messages = tk.Frame(master=window)
    frm_messages.grid(pady=20, padx=20)

    # Create a scrollbar for message navigation, child to the message frame
    scrollbar = tk.Scrollbar(master=frm_messages)

    # Create a text object to hold the messages sent between the clients and server, bound to the scroll bar
    # Makes sure the text object cannot be altered by the users' keypress
    messages = tk.Text(master=frm_messages, yscrollcommand=scrollbar.set, wrap='word')
    messages.bind("<Key>", lambda e: "break")

    # Packs the scrollbar and text to the left and right of the frame, to hold their place
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Retrieves the collection of messages from the client thread
    client.messages = messages
    receive.messages = messages

    # Creates a grid in the message frame to make way for the buttons, entry box etc...
    frm_messages.grid(row=1, column=0, columnspan=2, sticky="nsew")

    # Creates the entry frame, home to the text message input which is bound to the enter key for sending to the server
    frm_entry = tk.Frame(master=window)
    text_input = tk.Entry(master=frm_entry, font=("Courier", 10))
    text_input.pack(fill=tk.BOTH, expand=True)
    text_input.bind("<Return>", lambda x: client.send(text_input))
    text_input.insert(0, "Your message here. Cannot be empty.")

    # Buttons to send the text input and to leave the server/quit the client
    btn_send = tk.Button(
        master=window,
        text='Send',
        command=lambda: client.send(text_input),
        font="Courier"
    )
    btn_quit = tk.Button(
        master=window,
        text='Quit',
        command=lambda: client.quit(),
        font="Courier"
    )

    # Sets the location of the text entry and buttons in relation to the frame grid
    frm_entry.grid(row=2, column=0, rowspan=2, padx=10, sticky="ew")
    btn_send.grid(row=2, column=1, padx=15, sticky="ew")
    btn_quit.grid(row=3, column=1, padx=15, sticky="ew")

    # Configures the rows and columns of the grid
    window.rowconfigure(0, minsize=50, weight=0)
    window.rowconfigure(1, minsize=300, weight=1)
    window.rowconfigure(2, minsize=30, weight=0)
    window.rowconfigure(3, minsize=30, weight=0)
    window.rowconfigure(4, minsize=20, weight=0)
    window.columnconfigure(0, minsize=300, weight=1)
    window.columnconfigure(1, minsize=150, weight=0)

    window.protocol('WM_DELETE_WINDOW', lambda: client.quit())
    window.mainloop()


if __name__ == '__main__':

    """
    Instantiates the client with the given host and port.
    """

    client_gui(host, port)
