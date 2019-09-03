# One chat instance runs and detects a pre-determined port to see if
# it is open or not. If it is taken, it assumes that there's another
# chat application listening on that part and will start trying to
# talk with the other program through it. If it is free, then it
# claims the port and starts listening on it.
#
# The first program to claim the port acts like a server, I guess.
# Sort-of.

import socket
from my_socket import MySocket

sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('localhost', 10003))
listener.listen(5)

def with_socket(sock):
    with sock:
        while True:
            chunk = sock.recv(MSGLEN)
            if chunk == b'':
                print("Empty message received, connection must be closed.")
                break
            else:
                print(chunk.decode('utf-8'))


MSGLEN = 128

while True:
    print("Going to accept a connection...")
    (clientsocket, address) = listener.accept()
    print(clientsocket, address)
    with_socket(clientsocket)
    print("Accepted!")

listener.close()

# NOTES:
# - shutdown(1) is shutdown(socket.SHUT_WR), which should mean that
#   the socket will not send, but it will still listen.
# - When using telnet, telnet detects the server socket closing and
#   will then terminate itself. The server would detect when a client
#   socket closes by reading nothing, I guess. And the client would
#   detect a closed server by... what? How did telnet do that? Did it
#   try to read, too? I guess telnet allows for reading and writing
#   back and forth. Both parties read and write.
