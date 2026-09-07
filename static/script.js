const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");

function addMessage(role, text) {
    const welcome = chatBox.querySelector(".welcome");
    if (welcome) welcome.remove();

    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "user" ? "U" : "A";

    const body = document.createElement("div");
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = role === "user" ? "You" : "AIRI";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = text;

    body.append(label, content);
    wrapper.append(avatar, body);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function setLoading(loading) {
    sendBtn.disabled = loading;
    messageInput.disabled = loading;
    sendBtn.textContent = loading ? "..." : "Send";
}

async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const history = await response.json();
        history.forEach(item => addMessage(item.role, item.message));
    } catch (error) {
        console.error("History error:", error);
    }
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage("user", message);
    messageInput.value = "";
    setLoading(true);

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Request failed");
        addMessage("assistant", data.response);
    } catch (error) {
        addMessage("assistant", `Error: ${error.message}`);
    } finally {
        setLoading(false);
        messageInput.focus();
    }
});

newChatBtn.addEventListener("click", async () => {
    try {
        await fetch("/api/clear", { method: "POST" });
        chatBox.innerHTML = `
            <div class="welcome">
                <div class="welcome-icon">A</div>
                <h2>Welcome to AIRI</h2>
                <p>Ask a question and start a conversation.</p>
            </div>`;
    } catch (error) {
        console.error("Clear error:", error);
    }
});

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

loadHistory();
