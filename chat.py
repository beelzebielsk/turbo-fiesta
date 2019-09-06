import socket
from my_socket import *
import os
import os.path

# Multithreaded stuff
import queue
import threading

port, convo_file = get_args()
print("\n----------", file=convo_file)
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('localhost', port))
listener.listen(5)
message_queue = queue.Queue()

with listener, convo_file:
    print("Going to accept a connection...")
    (clientsocket, address) = listener.accept()
    print("Accepted!")
    print(clientsocket, address)
    clientsocket = MySocket(clientsocket)
    x = threading.Thread(target=take_user_messages,
            args=(message_queue,))
    y = threading.Thread(target=get_and_send_messages,
            args=(clientsocket, message_queue, convo_file))
    x.start()
    y.start()
    x.join()
    y.join()
