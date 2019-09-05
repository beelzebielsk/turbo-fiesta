Explore communications and p2p networks via a basic chatting
application

- recv is blocking
- Right now, if the client is started first, it crashes with a
  connection refused error. So the server has to start up first and
  listen for a connection on the agreed-upon port.
- There's also a fixed back-and-forth message order where the client
  talks first, the server talks 2nd, client, server, ... etc. There's
  no way to send two messages one after another, and there's no way
  for each party to send messages at the same time.
- The select call keeps returning immediately because the socket is
  always writable. There's always some space to write.

Useful Links:
Overview of diff methods of concurrency
https://realpython.com/python-concurrency/

Intro to threading and its nitty-gritty details
https://realpython.com/intro-to-python-threading/

Documentation on context managers
https://book.pythontips.com/en/latest/search.html?q=with+statement&check_keywords=yes&area=default#

Details on TTYs
https://askubuntu.com/questions/66195/what-is-a-tty-and-how-do-i-access-a-tty

I have two programs talking to each other. They're a little
asymmetric. One program has to start up first and the other one has to
start up 2nd. And there's a single agreed-upon port that they connect
to each other on on the same computer.

From here on out, there's the question of connecting more than one
perosn, and doing this without one person having to tell someone else
which IP and port to connect to them on.

One possibility is a client-server model where there's a server that
will always be running, be expected to be up first, and everyone else
is a client of that server. Each person gets messages from others from
the server, and sends their messages to the server.

Another possibility is a "peer-to-peer" model, which I don't
understand very well. But I figure that no one program has to be "up
first". Someone starts up and others join them. But that's a little
hard to believe. How do the others know who to join on? Another
possibility is that there's a server which just helps peers find each
other, and then from there the peers connect to one another. Stuff
like chat history will be stored and shared among peers without a
central server helping out---except to help peers locate one another.

Other troubles are things like chat history and message ordering. How
would you have conversation histories shared among the people in the
conversation without storing them on a central server? And for all of
the possible ways to set this chat thing up, how would each person in
a conversation get all the messages in the correct order and display
them in the correct order? What does "correct order" even mean?

TODO
====

- Change the socket communication to actually use my_socket.py and to
  support variable-length messages.
- Change this to a real client-server model.
- Work on conversation history and sharing it with users.
- Work on message ordering. What that means, how to enforce it.
