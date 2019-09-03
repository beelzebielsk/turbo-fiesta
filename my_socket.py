import socket

MSGLEN = 128
def msg_prep(msg):
    """Takes msg as a utf-8 string (assumes msg will decode to 128 bytes or
    less) and turns it into a length 128 byte string."""
    return msg.encode('utf-8').ljust(MSGLEN, b'\0')

class MySocket:
    """Protocol:
    - First a server socket listens on the given host and port
    - Then a client socket connects to the given host and port
    - Huh... who sends messages and when, then?
    - Each message is prefixed with the message length: 5 ascii
      characters which spell out the length as a decimal number.
    """
    port = 10003
    host = 'localhost'
    num_bytes_prefix_len = 5
    def __init__(self, port=None, sock=None):
        """port here is the port that the socket's listener is going
        to listen on. I think there should be two ports because
        there's a possibility of both people sending a message at the
        same time.
        """
        if port is None and sock is None:
            raise RuntimeError("must pass in either port or socket!")
        elif sock is None:
            self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.port = port

    def __enter__(self):
        return self.sock

    def __exit__(self, type, value, traceback):
        print("Exit method called.")
        self.sock.close()

    def connect(self):
        self.sock.connect((self.host, self.port))

    def be_a_server(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

    def mysend(self, msg):
        MSGLEN = len(msg)
        # This should be no more than five characters.
        length_bytes = str(MSGLEN).encode("utf-8")
        sent = self.sock.send(length_bytes)
        if sent < self.num_bytes_prefix_len:
            raise RuntimeError(f"Sent too few length bytes. Actual are {length_bytes} and of these you sent {sent}")
        if sent > self.num_bytes_prefix_len:
            raise RuntimeError(f"Sent too many length bytes. Actual are {length_bytes} and of these you sent {sent}")

        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        length_bytes = self.sock.recv(self.num_bytes_prefix_len)
        if len(length_bytes) < self.num_bytes_prefix_len:
            raise RuntimeError(f"Read too few bytes for length. Read {len(length_bytes)}.")
        MSGLEN = int(length_bytes.decode("utf-8"))

        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)

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
