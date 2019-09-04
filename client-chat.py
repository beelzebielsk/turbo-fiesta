import socket
from my_socket import *

# Multithreaded stuff
import threading

port = get_port()
sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender.connect(('localhost', port))
message_queue = queue.Queue()
sender = MySocket(sender)

with sender:
    x = threading.Thread(target=take_user_messages,
            args=(message_queue,))
    y = threading.Thread(target=get_and_send_messages,
            args=(sender, message_queue))
    x.start()
    y.start()
    x.join()
    y.join()
