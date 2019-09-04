# One chat instance runs and detects a pre-determined port to see if
# it is open or not. If it is taken, it assumes that there's another
# chat application listening on that part and will start trying to
# talk with the other program through it. If it is free, then it
# claims the port and starts listening on it.
#
# The first program to claim the port acts like a server, I guess.
# Sort-of.

import socket
from my_socket import MySocket, msg_prep, MSGLEN

# Multithreaded stuff
import queue
import threading

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('localhost', 10002))
listener.listen(5)
message_queue = queue.Queue()

def take_user_messages():
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

def get_and_send_messages(sock):
    with sock:
        while True:
            # print("Before recv...")
            chunk = sock.recv(MSGLEN)
            # print("After recv...")
            if chunk == b'':
                print("Empty msg: client ended communications.")
                return
            print("<", chunk.decode('utf-8'))
            line = message_queue.get()
            if line is None:
                print("Server ended communications.")
                message_queue.task_done()
                return
            sock.send(msg_prep(line))
            message_queue.task_done()

with listener:
    print("Going to accept a connection...")
    (clientsocket, address) = listener.accept()
    print("Accepted!")
    print(clientsocket, address)
    x = threading.Thread(target=take_user_messages)
    y = threading.Thread(target=get_and_send_messages,
            args=(clientsocket,))
    x.start()
    y.start()
    x.join()
    y.join()
