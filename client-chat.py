import socket
from my_socket import MySocket, msg_prep, MSGLEN

# Sends fixed-length messages

thing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thing.connect(('localhost', 10000))

with thing:
    while True:
        line = input("> ")
        if line == "":
            print("Client ended communications.")
            break
        thing.send(msg_prep(line))
        chunk = thing.recv(MSGLEN)
        if chunk == b'':
            print("Empty msg: server ended communications.")
            break
        print("<", chunk.decode('utf-8'))

