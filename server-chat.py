import socket
from my_socket import *
import os
import os.path
from uuid import UUID as uuid

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
        with self._lock, self.empty:
            self.lst.append(item)
            current_len = len(self.lst)
            if current_len == 1:
                self.empty.notify()

    def remove(self, item):
        with self._lock:
            for i in range(len(self.lst)):
                if item is self.lst[i]:
                    del self.lst[i:i+1]
                    return True
        return False

class GuardedDict:
    def __init__(self, _dict=None):
        if _dict is None:
            self.dict = {}
        else:
            self.dict = _dict
        self._lock = threading.Lock()
        self.empty = threading.Condition()

    def isNotEmpty(self):
        with self._lock:
            return len(self.dict) > 0

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self._lock.release()

    def add(self, key, item):
        with self._lock, self.empty:
            self.dict[key] = item
            current_len = len(self.dict)
            if current_len == 1:
                self.empty.notify()

    def remove(self, key):
        with self._lock:
            if key in self.dict:
                del self.dict[key]
                return True
        return False

# People will be a map of uuid to tuples of (socket, nickname).
people = GuardedList()
unregistered_people = GuardedList()

# The server has to both accept connections as people join the room
# and listen for messages being sent from someone

def accept_people():
    """Listens for incoming connections and places them in
    unregistered_people"""
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
            unregistered_people.add(clientsocket)

def register_people():
    """Waits for entries to arrive in unregistered_people. Takes a
    uuid and nickname from each person, then places them in people."""
    while True:
        print("Check if unregistered_people is empty...")
        empty = not unregistered_people.isNotEmpty()
        if empty:
            print("Wait for unregistered_people to not be empty.")
            with unregistered_people.empty:
                unregistered_people.empty.wait_for(unregistered_people.isNotEmpty)
                print("unregistered_people is not empty!")
                with unregistered_people:
                    current_people = unregistered_people.lst.copy()
        else:
            with unregistered_people:
                current_people = unregistered_people.lst.copy()
        current_people, _, __ = select.select(current_people, [], [])
        for person in current_people:
            # NOTE: Assumption that all data immediately available
            uuid_hex = person.myreceive()
            nickname = person.myreceive()
            print(f"Registering {nickname} with identity {uuid_hex}")
            people.add(Person(uuid_hex, nickname, person))
            unregistered_people.remove(person)

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
def broadcast_message(nickname, msg):
    """Takes a nickname (string), and a single message (string) and
    sends it to everyone who is in people when the function is first
    invoked."""
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
        recipient.sock.mysend(nickname)
        recipient.sock.mysend(msg)

def send_and_receive_messages():
    """Watches for incoming messages from anyone in people. Once a
    message comes, broadcasts it to everyone in people."""
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
        # TODO: Pair a socket with its id and nickname so I can
        # quickly send out the nickname of a message along with the
        # message. One soln is to make a person object which has an
        # id, nick, and socket, and exposes the fileno of its socket
        # so that it can be used with select.
        readers, _ , __ = select.select(readers, [], [])
        print("Number of redable sockets:", len(readers))
        for reader in readers:
            try:
                # I am not ordering these messages yet. I should be
                # checking some kind of timestamp on the messages to
                # decide how and when to send them. Either the time
                # they arrive at the server of the time they left the
                # client computer.
                msg = reader.sock.myreceive()
                broadcast_message(reader.nickname, msg)
            except RuntimeError:
                print("Someone disconnected.")
                with people:
                    people.remove(reader)

connector = threading.Thread(target=accept_people)
registrator = threading.Thread(target=register_people)
message_coordinator = threading.Thread(target=send_and_receive_messages)
try:
    connector.start()
    registrator.start()
    message_coordinator.start()
    # Maybe this will make sure the connection always gets closed
    # properly.
    connector.join()
except Exception as e:
    # Kill them... this is the only way I know how.
    connector.daemon = True
    registrator.daemon = True
    message_coordinator.daemon = True
    raise e

# Protocol:
# - The server starts up and starts accepting connections.
# - A client starts up. It connects to the server's listening socket.
# - The client sends a uuid as hex characters in a single message.
# - The client sends a nickname as a single message.
# - The client can now send and receive messages to and from the
#   server. 
#       - Each message sent from client to server sends a message to
#         the server using a single call to mysend. 
#       - Each message sent from server to client will be sent using
#         two calls to mysend: one for a nickname, one for the actual
#         message content.
#   message content sent as two separate messages over the connection
#   (two separate uses of myreceive are needed).

# TODO:
# - It is possible that semaphores are more appropriate for the
#   guarded classes. I think I saw register_people hang because it was
#   waiting on a condition variable that would never get notified.
