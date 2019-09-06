This is a playground for exploring networking issues. I've always been
curious about network programming and peer-to-peer networks, and found
them impenetrable. So this is a very simple POC chat application I'm
creating to explore both of these.

Progress
========

- I've got two programs able to talk to each other over a network
  connection. They are sort-of peers with each other, but they aren't
  equal. One program listens for an incoming connection and the other
  program connects. There are no ways for more people to join: just
  two programs talk to each other.

TODO
====

I think the following issues will help me see and explore p2p
networking concepts first hand, and why it is different from
client-server models

- If I let many people talk to each other on a p2p architecture, how
  will they actually transmit messages to one another? Will each
  person connect to every other person in a complete graph? Just some?
- If I maintain a conversation history, how will I distribute the
  history?
- How will I order the messages? What does this even mean once I
  consider that some messages could get delayed---perhaps even
  significantly? What if a message claims it came from 3 hours ago? Am
  I going to have to handle re-printing 3 hours worth of messages for
  everyone that could have seen the message? Skip it?
