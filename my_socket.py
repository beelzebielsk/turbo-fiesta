import socket

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
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

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
