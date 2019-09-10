import socket
from my_socket import *
import os
import os.path
from uuid import uuid4 as rand_uuid

# Multithreaded stuff
import threading

port, convo_file = get_args()
print("\n----------", file=convo_file)
sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender.connect(('localhost', port))
message_queue = queue.Queue()
sender = MySocket(sender)
my_id = rand_uuid()

with sender, convo_file:
    sender.mysend(my_id.hex)
    # NOTE: Keep the two messages spaced apart by slow user IO for
    # now. I think this causes bugs to appear in the server.
    nick = input("nickname: ")
    print(f"Going to connect with id '{my_id.hex}' and nick '{nick}'")
    sender.mysend(nick)
    x = threading.Thread(target=take_user_messages,
            args=(message_queue,))
    y = threading.Thread(target=get_and_send_messages,
            args=(sender, message_queue, convo_file))
    x.start()
    y.start()
    x.join()
    y.join()
