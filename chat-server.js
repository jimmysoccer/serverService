const express = require("express");
const app = express();
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

var sessionStore = [];

function randomId() {
  return "id" + Math.random().toString(16).slice(2);
}

io.use((socket, next) => {
  // const sessionID = socket.handshake.auth.sessionID;
  // if (sessionID) {
  //   // find existing session
  //   var session;
  //   for (let i = 0; i < sessionStore.length; i++) {
  //     if (sessionStore[i].sessionID === sessionID) {
  //       session = sessionStore[i];
  //     }
  //   }
  //   if (session) {
  //     console.log("use existed user");
  //     socket.sessionID = sessionID;
  //     socket.userID = session.userID;
  //     socket.username = session.username;
  //     return next();
  //   }
  // }
  const username = socket.handshake.auth.username;
  if (!username) {
    return next(new Error("invalid username"));
  }
  // create new session
  // console.log("create new user");
  let temp_sessionId = randomId();
  let temp_userId = randomId();

  // socket.sessionID = temp_sessionId;
  // socket.userID = temp_userId;
  socket.username = username;

  // sessionStore.push({
  //   sessionID: temp_sessionId,
  //   userID: temp_userId,
  //   username: username,
  // });

  next();
});

io.on("connection", (socket) => {
  console.log("user connected", socket.id, socket.username);

  //notify existing users
  socket.broadcast.emit("user connected", {
    userID: socket.id,
    username: socket.username,
  });

  const users = [];
  for (let [id, socket] of io.of("/").sockets) {
    users.push({
      userID: id,
      username: socket.username,
    });
  }
  socket.emit("users", users);

  socket.on("private message", ({ content, to }) => {
    socket.to(to).emit("private message", {
      content,
      from: socket.id,
    });
  });

  socket.on("disconnect", () => {
    console.log(`User Disconnected: ${socket.id}`);

    // socket.broadcast.emit("user connected", {
    //   userID: socket.id,
    //   username: "disconnected",
    // });
    socket.broadcast.emit("user disconnected", { userID: socket.id });
    for (let i = 0; i < users.length; i++) {
      if (users[i].userID === socket.id) {
        delete users[i];
      }
    }
  });
});

server.listen(3001, () => {
  console.log("SERVER IS RUNNING");
});
