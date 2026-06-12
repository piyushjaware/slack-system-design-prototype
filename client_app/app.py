import os
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

SERVICE_URL = os.getenv("SERVICE_URL")
CONNECT_SERVICE_URL = "http://connect_service:5000"
USER_ID = os.getenv("USER_ID")
USER_NAME = os.getenv("USER_NAME")


def fetch_channels():
    channels_resp = requests.get(f"{SERVICE_URL}/users/{USER_ID}/channels", timeout=5)
    channels_resp.raise_for_status()
    channels = channels_resp.json().get("channels", [])

    for channel in channels:
        msg_resp = requests.get(
            f"{SERVICE_URL}/channels/{channel['id']}/messages", timeout=5
        )
        msg_resp.raise_for_status()
        channel["messages"] = msg_resp.json().get("messages", [])

    return channels


def fetch_socket_url(user_name):
    connect_resp = requests.get(
        f"{CONNECT_SERVICE_URL}/connect/{user_name}",
        timeout=5,
    )
    connect_resp.raise_for_status()
    return connect_resp.json()["socket_url"]


@app.route("/")
def home():
    channels = []
    error = request.args.get("error")
    socket_url = None
    try:
        channels = fetch_channels()
    except requests.RequestException as exc:
        error = f"Could not load data from msg_service: {exc}"

    try:
        socket_url = fetch_socket_url(USER_NAME)
    except requests.RequestException as exc:
        error = f"Could not load socket url from connect_service: {exc}"

    return render_template(
        "index.html",
        channels=channels,
        user_id=USER_ID,
        user_name=USER_NAME,
        socket_url=socket_url,
        error=error,
    )


@app.route("/channels/<int:channel_id>/send", methods=["POST"])
def send_message(channel_id):
    text = (request.form.get("text") or "").strip()
    if not text:
        return redirect(url_for("home", error="Message cannot be empty"))

    try:
        response = requests.post(
            f"{SERVICE_URL}/channels/{channel_id}/messages",
            json={"text": text, "sender_id": int(USER_ID)},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return redirect(url_for("home", error=f"Could not send message: {exc}"))

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
