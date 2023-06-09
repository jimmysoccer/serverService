var net = require("net");

const PORT = process.env.PORT;

// Create a server instance, and chain the listen function to it
// The function passed to net.createServer() becomes the event handler for the 'connection' event
// The sock object the callback function receives UNIQUE for each connection
net
  .createServer(function (sock) {
    // We have a connection - a socket object is assigned to the connection automatically
    console.log("CONNECTED: " + sock.remoteAddress + ":" + sock.remotePort);
    sock.write(
      sock.remoteAddress + " " + sock.remotePort + " conneted to server!"
    );
    // Add a 'data' event handler to this instance of socket
    sock.on("data", function (data) {
      console.log("DATA " + sock.remoteAddress + ": " + data);
      // Write the data back to the socket, the client will receive it as data from the server
      sock.write('Sent from server "' + data + '"');
    });
    // Add a 'close' event handler to this instance of socket
    sock.on("close", function (data) {
      console.log("CLOSED: " + sock.remoteAddress + " " + sock.remotePort);
      sock.write("socket connection is closed");
    });
  })
  .listen(PORT);

console.log("Server listening on " + ":" + PORT);
