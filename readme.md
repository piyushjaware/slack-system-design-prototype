
Alice: http://localhost:7001/
Bob: http://localhost:7002/


Sample Request

```

Get all channels for user 1
curl http://127.0.0.1:5001/users/1/channels 

Get all messages in channel 1
curl -X GET http://localhost:5001/channels/1/messages

Post a message to channel 1 
curl -X POST http://localhost:5001/channels/1/messages \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey everyone!", "sender_id": 1}'
  
```