import socket

MSGLEN = 128

def msg_prep(msg):
    return msg.encode('utf-8').ljust(MSGLEN, b'\0')

thing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thing.connect(('localhost', 10003))

with thing:
    while True:
        line = input("> ")
        if line == "":
            break
        else:
            thing.send(msg_prep(line))

