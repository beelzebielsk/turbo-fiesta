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
- Looks like if I give select three empty lists and let it block, it
  will block forever.

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

### Message Ordering

For now, with a client-server architecture, the message order will be
simple: the order in which the messages arrive to the server and are
read from the sockets. There will be no special effort to maintain
them in any specific order.

### Conversation History

The history will be stored in the message order. For now, each person
will get the full history. The message history should also note who it
was that said what, so each user who connects should communicate some
ID, and perhaps a nickname.

### Reading from many potential sources with select

I often have a lot of people I can potentially read something from,
and right now I assume that I always have a full+valid message I can
read from them when they come from a select call. But this won't be
true in general. I need a clean way to either wait until a full
message is waiting in the socket (a way to select on messages rather
than on data, basically) or I need to store message pieces until I get
a full thing. Only differnce between the two is whether I handle this
in MySocket once somehow or I handle it externally somewhere.

I have a similar trouble with writing to many potential sources with
select. It would be nice to write whatever parts of a message that I
can write at any given time rather than assume that I can write all of
a message immediately.

Note that I probably won't see these problems until I exposed this
program to heavy load or slow connections.

TODO
====

- Change the socket communication to support variable-length messages.
- Work on conversation history and sharing it with users.
- Work on message ordering. What that means, how to enforce it.
- Change this to a p2p model, where there is no server that hosts the
  chat, or use of servers is minimal for ancillary purposes like
  figuring out who you can join on.

```
Server:
Check if unregistered_people is empty...
Wait for unregistered_people to not be empty.
Going to accept a connection...
Accepted!
<socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=
('127.0.0.1', 10002), raddr=('127.0.0.1', 33558)> ('127.0.0.1', 33558)
Going to accept a connection...
unregistered_people is not empty!
Accepted!
<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=
('127.0.0.1', 10002), raddr=('127.0.0.1', 33560)> ('127.0.0.1', 33560)
Going to accept a connection...
Registering top with identity 2dbcebcee4bf428ba5f9bb5706573850
Check if unregistered_people is empty...
Copying people...
Number of people: 1
Number of redable sockets: 1
Registering sir with identity hi

Client "top":
nickname: top
> hi
> there
> sir
>

Client "bottom":
nickname: bottom
> hello
> to
> you too

```

Woah. That is a serious bug. It looks like one person get registered
twice. How did that happen? See if you can reproduce this.
