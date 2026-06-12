import json
import os
import mysql.connector
import redis
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    decode_responses=True
)
redis_pubsub = redis_client.pubsub()

# In-memory connection state
user_to_sid = {}
sid_to_user = {}
channel_to_users = {}


def push_to_users(channel, event):
    users = channel_to_users.get(channel)
    print(f"[{channel}] -> Sending to users: {users}")
    if not users:
        print(f"No users subscribed to channel: {channel}")
        return

    event_with_channel = dict(event)
    event_with_channel["channel_id"] = int(channel)
    # users.discard(str(event.get("sender_id")))
    if users:
        for user_id in users:
            if user_id == str(event.get("sender_id")):
                continue
            sid = user_to_sid.get(user_id)
            if sid:
                socketio.emit("message", event_with_channel, to=sid)


def redis_listener():
    print("Redis listener started***********", flush=True)
    while True:
        try:
            # Use get_message with a short timeout instead of blocking endlessly
            message = redis_pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                channel = message["channel"]
                event = json.loads(message["data"])
                push_to_users(channel, event)
            socketio.sleep(0.01)  # Yields execution control back to the WSGI worker
        except Exception as e:
            print(f"Error in listener: {e}")
            socketio.sleep(1)


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'root'),
            database=os.getenv('MYSQL_DATABASE', 'testdb')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


# Logic to send a message to user
# maintain a map of a channel to users
# on registration, query channels for user, update the map and subscribe to the channel
# listen to redis pub sub and once a notification is received for a channel
# send the message to the users of the channel


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/users")
def users():
    return jsonify({"connected_users": list(user_to_sid.keys())})


@app.post("/send")
def send_to_user_http():
    payload = request.get_json(silent=True) or {}
    to_user_id = str(payload.get("to_user_id", "")).strip()
    message = str(payload.get("message", "")).strip()

    if not to_user_id or not message:
        return jsonify({"error": "to_user_id and message are required"}), 400

    sid = user_to_sid.get(to_user_id)
    if not sid:
        return jsonify({"error": f"user {to_user_id} is not connected"}), 404

    socketio.emit("message", {"to_user_id": to_user_id, "message": message}, to=sid)
    return jsonify({"status": "sent"})


@socketio.on("connect")
def on_connect():
    print(f"User connected: {request.sid}")
    emit("connected", {"sid": request.sid})


def subscribe_to_channels(user_id):
    channels = get_user_channels(user_id)
    print(f"Subscribing to channels: {channels} for user: {user_id}")
    for channel in channels:
        channel_id = str(channel["channel_id"])
        redis_channel = channel_id
        if redis_channel not in channel_to_users:
            print(f"Creating Redis channel: {redis_channel}")
            channel_to_users[redis_channel] = set()
            channel_to_users[redis_channel].add(user_id)
            redis_pubsub.subscribe(redis_channel)
            print(f"Subscribed to Redis channel: {redis_channel}")
        else:
            channel_to_users[redis_channel].add(user_id)


def get_user_channels(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT channel_id FROM channel_membership WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    channels = cursor.fetchall()
    cursor.close()
    conn.close()
    return channels


@socketio.on("register")
def on_register(data):
    print(f"Registering user: {data} with sid: {request.sid}")
    user_id = str((data or {}).get("user_id", "")).strip()
    if not user_id:
        emit("error", {"error": "user_id is required"})
        return

    existing_sid = user_to_sid.get(user_id)
    if existing_sid and existing_sid != request.sid:
        sid_to_user.pop(existing_sid, None)

    user_to_sid[user_id] = request.sid
    sid_to_user[request.sid] = user_id

    #  Subscribe to channels for the user
    subscribe_to_channels(user_id)

    emit("registered", {"user_id": user_id, "sid": request.sid})


@socketio.on("disconnect")
def on_disconnect():
    user_id = sid_to_user.pop(request.sid, None)
    if user_id:
        user_to_sid.pop(user_id, None)
        print(f"User disconnected: {user_id}")
        for users in channel_to_users.values():
            users.discard(user_id)


if __name__ == "__main__":
    print("Starting ws_service background listener", flush=True)
    socketio.start_background_task(redis_listener)
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, use_reloader=False)
