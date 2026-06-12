## Services overview

- **client_app**: Web UI for Alice and Bob. It loads channels/messages and sends chat messages.
- **msg_service**: REST API for channels and messages backed by MySQL.
- **connect_service**: Returns the websocket URL for a user.
- **ws_service_alice**: Websocket server serving Alice.
- **ws_service_bob**: Websocket server serving Bob.
- **mysql**: Stores users, channels, memberships, and messages.
- **redis**: Broadcast layer used by the websocket services.

Alice's Client App: http://localhost:7001/
Bob's Client App: http://localhost:7002/


---
Sample Test Requests

```

Get all channels for user 1
curl http://127.0.0.1:5001/users/1/channels 

Get all messages in channel 1
curl -X GET http://localhost:5001/channels/1/messages

Post a message to channel 1 
curl -X POST http://localhost:5001/channels/1/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey everyone!", "sender_id": 1}'


Get connected users
curl http://localhost:5002/users  

Test ws send message
curl -X POST http://localhost:5002/send \
  -H "Content-Type: application/json" \
  -d '{"to_user_id": 1, "message": "Hello Alice!"}'
  
```

---
How to run locally?

```html
make install_reqs
make run
```
