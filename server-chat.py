import socket
from my_socket import *
import os
import os.path

# Multithreaded stuff
import queue
import threading

# The point of this is to get clients to be able to talk to each
# other. A client can connect here and... let's just assume everyone
# talks on the same "room" for now. No separation of people. You just
# talk to this server to "get things started".
#
# So, supposing there's already a "room" started, you're going to want
# to become able to submit messages and receive messages from this
# room, and you're going to want to see some conversation history.
#
# For now, let's just say that you get no history, You just start
# seeing messages as they're sent.
#
# I guess the server will hold a directory of people to send messages
# to and receive messages from. Each time a person sends a message,
# everyone else gets that message sent to them, too.
port, convo_file = get_args()

class GuardedList:
    def __init__(self, lst=None):
        if lst is None:
            self.lst = []
        else:
            self.lst = lst
        self._lock = threading.Lock()
        self.empty = threading.Condition()

    def isNotEmpty(self):
        with self._lock:
            return len(self.lst) > 0

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self._lock.release()

    def add(self, item):
        with self._lock:
            self.lst.append(item)
    def remove(self, item):
        with self._lock:
            for i in range(len(self.lst)):
                if item is self.lst[i]:
                    del self.lst[i:i+1]
                    return True
        return False

people = GuardedList()

# people will be represented entirely by the socket they opened up
# with the server.

# The server has to both accept connections as people join the room
# and listen for messages being sent from someone

def accept_people():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', port))
    listener.listen(5)
    with listener:
        while True:
            print("Going to accept a connection...")
            (clientsocket, address) = listener.accept()
            print("Accepted!")
            print(clientsocket, address)
            clientsocket = MySocket(clientsocket)
            people.add(clientsocket)
            with people.empty:
                people.empty.notify()

# The best thing this can do, really, is to send out the message to
# each socket as best it can at any given time. I wouldn't want the
# server to "block" on each message, busy looping while checking to
# see if it is writable. This is also the WORST-CASE for this program.
# While messing around at home, it is likely all the sockets will be
# free for writing all of the time. Running a bunch of threads for
# each person to send a message to is not ideal, I think. It may be
# best to make one thread that uses a different form of concurrency,
# like an event loop. The more complicated way to program this is to
# keep a list of people that should get the message and send out as
# much of the message as possible to each person. Each time I send a
# person the full message, remove that person from the list. For those
# whom I can't send the full message, keep track of how much I've sent
# so far. Each time I loop through the whole list of people that I can
# write to one at a time.
def broadcast_message(msg):
    # For now, just send to those that are currently connected. Do not
    # worry about the possibility of the broadcast taking a long time
    # and people joining in on the room. If they hadn't joined by the
    # time the broadcast starts, they don't get the message.
    # Do note, however, that readers here may be more than readers
    # from send and receive messages, since I re-copy people.
    with people:
        readers = people.lst.copy()
    # I should really be doing select to see if I can write to them. I
    # may end up blocking here.
    for recipient in readers:
        recipient.mysend(msg)

def send_and_receive_messages():
    while True:
        # I may do this very often. Should I really keep locking up
        # people and making a copy of it that often? If I had a lot of
        # messages to distribute, this would get really wasteful.
        with people.empty:
            people.empty.wait_for(people.isNotEmpty)
            print("Copying people...")
            with people:
                readers = people.lst.copy()
        print("Number of people:", len(readers))
        # Do NOT put this inside the with statement! I shouldn't block
        # on a select call while holding a lock on people. This will
        # lock up the connection-accepting thread, most likely.
        readers, _ , __ = select.select(readers, [], [])
        print("Number of redable sockets:", len(readers))
        for reader in readers:
            try:
                # I am not ordering these messages yet. I should be
                # checking some kind of timestamp on the messages to
                # decide how and when to send them. Either the time
                # they arrive at the server of the time they left the
                # client computer.
                msg = reader.myreceive()
                broadcast_message(msg)
            except RuntimeError:
                print("Someone disconnected.")
                with people:
                    people.remove(reader)

connector = threading.Thread(target=accept_people)
message_coordinator = threading.Thread(target=send_and_receive_messages)
try:
    connector.start()
    message_coordinator.start()
except Exception as e:
    # Kill them... this is the only way I know how.
    connector.daemon = True
    message_coordinator.daemon = True
    raise e
