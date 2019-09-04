import socket
import sys
import select
import queue

MSGLEN = 128
def msg_prep(msg):
    """Takes msg as a utf-8 string (assumes msg will decode to 128 bytes or
    less) and turns it into a length 128 byte string."""
    return msg.encode('utf-8').ljust(MSGLEN, b'\0')

class MySocket:
    """
    This is just for sockets that send messages through each other.
    Not for setting up connections.
    Protocol:
    - First a server program listens on the given host and port
    - Then a client program connects to the server's socket.
    - Client then creates it's own socket bound on another host and
      port.
    - Client sends message 'ready' to the server.
    - The server then connects to the client's port.
    - Now... there needs to be a way for each program to concurrently
      take user messages to send and get the other program's messages
      and display all of these on the screen.
    - Each message is prefixed with the message length: 5 ascii
      characters which spell out the length as a decimal number.
    """
    def __init__(self, sock):
        """port here is the port that the socket's listener is going
        to listen on. I think there should be two ports because
        there's a possibility of both people sending a message at the
        same time.
        """
        self.sock = sock

    def __enter__(self):
        return self.sock

    def __exit__(self, type, value, traceback):
        print("Exit method called.")
        self.sock.close()

    def fileno(self):
        return self.sock.fileno()

    def mysend(self, msg):
        msg_bytes = msg_prep(msg)
        self.sock.send(msg_bytes)

    def myreceive(self):
        msg_bytes = self.sock.recv(MSGLEN)
        if msg_bytes == b'':
            raise RuntimeError("socket connection broken")
        return msg_bytes.decode('utf-8')

def get_port():
    if len(sys.argv) < 2:
        port = int(10000)
    else:
        port = int(sys.argv[1])
    return port

def take_user_messages(message_queue):
    while True:
        # Doing this right requires moving away from just printing. If
        # anything else prints, it prints right where the prompt left
        # off which is confusing.
        line = input("> ")
        if line == "":
            message_queue.put(None)
            return
        else:
            message_queue.put(line)

def get_and_send_messages(sock, message_queue):
    with sock:
        while True:
            readers = [sock]
            writers = [sock]
            #errs = [sock]
            timeout = 2.0 # seconds
            readers, writers, _ = select.select(
                    readers, writers, [], timeout)
            if len(readers) > 0: 
                msg = sock.myreceive()
                if msg == b'':
                    print("Empty msg: client ended communications.")
                    return
                print("<", msg)
            if len(writers) > 0:
                try:
                    line = message_queue.get_nowait()
                    if line is None:
                        print("Server ended communications.")
                        message_queue.task_done()
                        return
                    sock.mysend(line)
                    message_queue.task_done()
                except queue.Empty:
                    pass

# Protocol:
# - One person starts up.
# - 2nd person starts up.
# - From here on in, either person should be able to send a message
#   1st. There is no determined 1st sender, nor is there a back+forth
#   send+reply scheme. Just two people sending messages back and
#   forth.

# Protocol:
# - One person starts up. The create a socket that's bound to a port
#   so that they can listen for incoming messages. They create a
#   socket that will connect to another port so that they can speak to
#   another person.
# - 2nd person starts up. Does the same things that the first person
#   does.
# - From here on in, either person should be able to send a message
#   1st. There is no determined 1st sender, nor is there a back+forth
#   send+reply scheme. Just two people sending messages back and
#   forth.
#
# Questions: 
# - Aren't accepting connections and making a conncetion blocking
#   operations? At the very least, isn't accepting blocking? 
# - I don't think I can do this without some threading. Part of the
#   program has to listen to the user and send messages, the other
#   part has to listen for messages from the other user and display
#   them.
#
