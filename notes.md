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
