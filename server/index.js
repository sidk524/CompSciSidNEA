
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });


var connectedUsers = new Map();
var games = new Map();

connectedUsers.set("user1", "ws1");

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
        
      } else if (msg.type == "logout") {
        if (connectedUsers.delete(sendingClient)){
          ws.send(JSON.stringify({type: "logout", success: true}));
        } else {
          ws.send(JSON.stringify({type: "logout", success: false}));
        }
      } else if (msg.type == "requestToPlay") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "playRequest", user: sendingClient}));
          }
        });
      } else if (msg.type == "acceptGame") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "confirmationAcceptRequest", user: sendingClien, opponent: msg.opponent}));
            games.set(sendingClient, msg.opponent);
          }
        });
      } else if (msg.type == "rejectGame") {
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "confirmationRejectRequest", user: sendingClient, opponent: msg.opponent}));
          }
        });
      } else if (msg.type == "sendMaze"){
        wss.clients.forEach(function each(client) {
          if (client.readyState === WebSocket.OPEN && client != ws && client == connectedUsers.get(msg.opponent))  { 
            client.send(JSON.stringify({type: "maze", config: msg.config}));
          }
        });
      }
    } catch (e) {
      console.log(e);
      console.log(msg)
    }

  });
} );  
