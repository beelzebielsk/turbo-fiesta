import socket
from my_socket import MySocket, msg_prep, MSGLEN
import select

# Multithreaded stuff
import queue
import threading

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.bind(('localhost', 10000))
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
            readers = [sock]
            writers = [sock]
            #errs = [sock]
            timeout = 2.0 # seconds
            # print("About to select...")
            readers, writers, _ = select.select(
                    readers, writers, [], timeout)
            # print("Select finished.")
            if len(readers) > 0: 
                chunk = sock.recv(MSGLEN)
                if chunk == b'':
                    print("Empty msg: client ended communications.")
                    return
                print("<", chunk.decode('utf-8'))
            if len(writers) > 0:
                # print("About to get a line...")
                try:
                    line = message_queue.get_nowait()
                    # print("Got a line.")
                    if line is None:
                        print("Server ended communications.")
                        message_queue.task_done()
                        return
                    sock.send(msg_prep(line))
                    message_queue.task_done()
                except queue.Empty:
                    pass

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
