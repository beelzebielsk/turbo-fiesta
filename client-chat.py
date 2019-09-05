import socket
from my_socket import *
import os
import os.path

# Multithreaded stuff
import threading

port, convo_file = get_args()
print("\n----------", file=convo_file)
sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender.connect(('localhost', port))
message_queue = queue.Queue()
sender = MySocket(sender)

with sender, convo_file:
    x = threading.Thread(target=take_user_messages,
            args=(message_queue,))
    y = threading.Thread(target=get_and_send_messages,
            args=(sender, message_queue, convo_file))
    x.start()
    y.start()
    x.join()
    y.join()
