import socket

thing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thing.connect(('localhost', 10002))

line = input("> ")
thing.send(line.encode('utf-8'))
thing.close()

