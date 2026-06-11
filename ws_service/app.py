from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory connection state
user_to_sid = {}
sid_to_user = {}


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/users")
def users():
    return jsonify({"connected_users": list(user_to_sid.keys())})


# @app.post("/send")
# def send_to_user_http():
#     payload = request.get_json(silent=True) or {}
#     to_user_id = str(payload.get("to_user_id", "")).strip()
#     message = str(payload.get("message", "")).strip()
#
#     if not to_user_id or not message:
#         return jsonify({"error": "to_user_id and message are required"}), 400
#
#     sid = user_to_sid.get(to_user_id)
#     if not sid:
#         return jsonify({"error": f"user {to_user_id} is not connected"}), 404
#
#     socketio.emit("message", {"to_user_id": to_user_id, "message": message}, to=sid)
#     return jsonify({"status": "sent"})


@socketio.on("connect")
def on_connect():
    print(f"User connected: {request.sid}")
    emit("connected", {"sid": request.sid})


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
    emit("registered", {"user_id": user_id, "sid": request.sid})


@socketio.on("disconnect")
def on_disconnect():
    user_id = sid_to_user.pop(request.sid, None)
    if user_id:
        user_to_sid.pop(user_id, None)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
