const userId = document.body.dataset.userId;
const userName = document.body.dataset.userName;
const socket = io("http://localhost:5002");

function appendMessageToChannel(channelId, senderName, messageText) {
    const channelEl = document.querySelector(`.channel[data-channel-id="${channelId}"]`);
    if (!channelEl) {
        return;
    }

    const messagesEl = channelEl.querySelector(".messages");
    if (!messagesEl) {
        return;
    }

    const emptyEl = messagesEl.querySelector(".empty");
    if (emptyEl) {
        emptyEl.remove();
    }

    const displaySenderName = senderName;
    const msgEl = document.createElement("div");
    msgEl.className = "msg";
    const senderEl = document.createElement("span");
    senderEl.className = "msg-sender";
    senderEl.textContent = displaySenderName;

    const textEl = document.createElement("span");
    textEl.className = "msg-text";
    textEl.textContent = messageText;

    msgEl.appendChild(senderEl);
    msgEl.appendChild(textEl);
    messagesEl.appendChild(msgEl);
}

socket.on("connect", function () {
    console.log("Connected to server!");
    socket.emit("register", {user_id: userId});
});

socket.on("registered", function (response) {
    console.log("Successfully registered on server:", response);
});

socket.on("message", function (data) {
    console.log("Message received:", data);
    appendMessageToChannel(data.channel_id, data.sender_name, data.msg);
});

socket.on("error", function (err) {
    console.error("Error:", err.error);
});

document.querySelectorAll("form.composer").forEach(function (form) {
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const input = form.querySelector('input[name="text"]');
        const text = input.value.trim();
        if (!text) {
            return;
        }

        const formData = new URLSearchParams();
        formData.append("text", text);

        const response = await fetch(form.action, {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: formData.toString()
        });

        if (!response.ok) {
            console.error("Failed to send message:", response.status);
            return;
        }

        const channelEl = form.closest(".channel");
        const channelId = channelEl ? channelEl.dataset.channelId : null;
        if (channelId) {
            appendMessageToChannel(channelId, userName, text);
        }
        input.value = "";
    });
});
