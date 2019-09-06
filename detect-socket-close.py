import socket
from my_socket import *
import select

# Multithreaded stuff
import threading

sockone, socktwo = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)

def try_to_read(sock):
    with sock:
        while True:
            readers = [sock]
            print("Select started...")
            readers, _, __ = select.select(readers, [], [])
            print("Select ended...")
            # TODO: Is it ever not?
            if len(readers) > 0:
                try:
                    msg = sock.myreceive()
                except RuntimeError:
                    print("Socket was empty.")
                    return
                print("<", msg)


receiver = threading.Thread(target=try_to_read, args=(MySocket(socktwo),))
receiver.start()

with MySocket(sockone) as sock:
    while True:
        line = input("> ")
        if line == "":
            break
        else:
            sock.mysend(line)

receiver.join()

# Conclusion from this file: select can detect when a socket has
# closed. If a socket is returned as a reader from a select call and
# has no data on it, then the connection has been closed.
