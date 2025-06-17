document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("clear-btn").addEventListener("click", clearChat);

async function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const chatContainer = document.getElementById("chat-container");
    const mode = document.getElementById("function-select").value;
    const message = messageInput.value.trim();

    if (!message) return;

    appendMessage("You", message, "chat-user");
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

        appendMessage("Thinkbot", reply, "chat-bot");
    } catch (err) {
        appendMessage("Thinkbot", "❌ Error: " + err.message, "chat-bot");
    } finally {
        toggleLoading(false);
        autoScroll();
    }
}

function appendMessage(sender, text, cssClass) {
    const chatContainer = document.getElementById("chat-container");
    const messageDiv = document.createElement("div");
    messageDiv.innerHTML = `<span class="${cssClass}">${sender}:</span> ${text}`;
    chatContainer.appendChild(messageDiv);
}

function clearChat() {
    document.getElementById("chat-container").innerHTML = "";
}

function toggleLoading(show) {
    document.getElementById("loading-indicator").style.display = show ? "block" : "none";
}

function autoScroll() {
    const chatContainer = document.getElementById("chat-container");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
