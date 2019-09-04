import socket
from my_socket import MySocket, msg_prep, MSGLEN

# Multithreaded stuff
import queue
import threading

sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender.connect(('localhost', 10002))
message_queue = queue.Queue()

with sender:
    while True:
        line = input("> ")
        if line == "":
            print("Client ended communications.")
            break
        sender.send(msg_prep(line))
        chunk = sender.recv(MSGLEN)
        if chunk == b'':
            print("Empty msg: server ended communications.")
            break
        print("<", chunk.decode('utf-8'))
