import os

from flask import Flask, jsonify

app = Flask(__name__)

SOCKET_URLS = {
    "alice": "http://localhost:5002",
    "bob": "http://localhost:5003",
}


@app.get("/health")
def health():
    return jsonify({"status": "healthy"})


@app.get("/connect/<string:user_name>")
def connect(user_name):
    socket_url = SOCKET_URLS.get(user_name.strip().lower())
    if not socket_url:
        return jsonify({"error": f"unknown user: {user_name}"}), 404

    return jsonify({"user_name": user_name, "socket_url": socket_url})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
