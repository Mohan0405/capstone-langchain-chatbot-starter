document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("clear-btn").addEventListener("click", clearChat);

async function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const chatContainer = document.getElementById("chat-container");
    const mode = document.getElementById("function-select").value;
    const message = messageInput.value.trim();

    if (!message) return;

    appendMessage("You", message, "user");
    messageInput.value = "";
    toggleLoading(true);

    try {
        const response = await fetch(`/${mode}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        const reply = data.message || data.error || "No response.";
        appendMessage("Thinkbot", reply, "bot");
    } catch (err) {
        appendMessage("Thinkbot", "❌ Error: " + err.message, "bot");
    } finally {
        toggleLoading(false);
        scrollToBottom();
    }
}

function appendMessage(sender, text, role) {
    const chatContainer = document.getElementById("chat-container");

    const row = document.createElement("div");
    row.classList.add("chat-row");

    const avatar = document.createElement("div");
    avatar.classList.add("chat-avatar");
    avatar.innerText = role === "user" ? "🧑" : "🤖";

    const bubble = document.createElement("div");
    bubble.classList.add("chat-bubble", role);
    bubble.innerText = text;

    row.appendChild(avatar);
    row.appendChild(bubble);
    chatContainer.appendChild(row);
}

function clearChat() {
    document.getElementById("chat-container").innerHTML = "";
}

function toggleLoading(show) {
    document.getElementById("loading-indicator").style.display = show ? "block" : "none";
}

function scrollToBottom() {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
