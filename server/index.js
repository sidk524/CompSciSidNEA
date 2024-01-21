
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });


var connectedUsers = new Map();
var games = new Map();

function getKeyByValue(map, searchValue) {
  for (let [key, value] of map.entries()) {
      if (value === searchValue) {
          return key;
      }
  }
  return null; // Return null if the value isn't found
}

function userLogout(ws) {

  let disconnectedUser = getKeyByValue(connectedUsers, ws);
  console.log("disconnectedUser", disconnectedUser);
  if (disconnectedUser) {
      connectedUsers.delete(disconnectedUser);
      // check if the disconnected user was in a game
      let opponent = games.get(disconnectedUser);
      if (opponent) {
        games.delete(opponent);
        games.delete(disconnectedUser);
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(opponent))  { 
            client.send(JSON.stringify({type: "opponentDisconnected", user: disconnectedUser}));
          }
        });
      }

  } wss.clients.forEach(function each(client) {
    if (client.readyState === WebSocket.OPEN && client != ws)  { 
      var usersToSend = Array.from(connectedUsers.keys());
      var index = usersToSend.indexOf(getKeyByValue(connectedUsers, client));
      if (index > -1) {
        usersToSend.splice(index, 1);
      }
      client.send(JSON.stringify({type: "newUser", connectedUsers: usersToSend}));
    }
  });
}
wss.on('connection', function connection(ws) {
  console.log("Connection established");
  ws.on('message', function incoming(message) {
    try {
      var msg = JSON.parse(message.toString());
      var sendingClient = msg.user;
      if (msg.type == "login") {
          console.log("Login request received");
          ws.send(JSON.stringify({type: "login", success: true, connectedUsers: Array.from(connectedUsers.keys())}));
          connectedUsers.set(sendingClient, ws);
          wss.clients.forEach(function each(client) {
            if (client.readyState === WebSocket.OPEN && client != ws)  { 
              var usersToSend = Array.from(connectedUsers.keys());
              var index = usersToSend.indexOf(getKeyByValue(connectedUsers, client));
              if (index > -1) {
                usersToSend.splice(index, 1);
              }
              client.send(JSON.stringify({type: "newUser", connectedUsers: usersToSend}));
            }
          });
        
      } else if (msg.type == "logout") {
        userLogout(ws);
      } else if (msg.type == "requestToPlay") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "playRequest", user: sendingClient}));
          }
        });
      } else if (msg.type == "acceptGame") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "confirmationAcceptRequest", user: sendingClient, opponent: msg.opponent}));
            games.set(sendingClient, msg.opponent);
            games.set(msg.opponent, sendingClient);
          }
        });
      } else if (msg.type == "rejectGame") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "confirmationRejectRequest", user: sendingClient, opponent: msg.opponent}));
          }
        });
      } else if (msg.type == "sendMaze"){
        console.log("sendMaze received", msg.opponent);
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "maze", maze: msg.maze}));
            console.log("sendMaze sent", msg.opponent);
          }
        });
      } else if (msg.type == "sendMove"){
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "move", move: msg.currentCell}));
          }
        });
      } else if (msg.type == "win"){
        console.log("win received", msg.opponent, connectedUsers.get(msg.opponent));
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "win", user: sendingClient}));
            console.log("win sent");
          }
        });
      } 
    } catch (e) {
      console.log(e);
      
    }

  }) 
    ws.on('pong', () => {
      ws.isAlive = true;
  });

  ws.on('close', () => {
    userLogout(ws);
  });
  
} );  

const interval = setInterval(function ping() {
  wss.clients.forEach(function each(ws) {
      if (ws.isAlive === false) {
        
          ws.terminate();
      }

      ws.isAlive = false;
      ws.ping();
  });
}, 1000);

wss.on('close', function close() {
  clearInterval(interval);
});
