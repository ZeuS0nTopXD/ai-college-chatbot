const state = {
    latestAnswer: "",
    speechEnabled: true,
    profile: JSON.parse(localStorage.getItem("vsitStudentProfile") || "{}"),
};

const views = {
    assistant: document.getElementById("assistant-view"),
    academics: document.getElementById("academics-view"),
    resources: document.getElementById("resources-view"),
};

const titles = {
    assistant: "Ask the VSIT Assistant",
    academics: "Academic calendar",
    resources: "College resources",
};

document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => showView(button.dataset.view));
});

function showView(name) {
    Object.entries(views).forEach(([viewName, element]) => {
        const active = viewName === name;
        element.hidden = !active;
        element.classList.toggle("active", active);
    });
    document.querySelectorAll(".nav-item").forEach((button) => {
        const active = button.dataset.view === name;
        button.classList.toggle("active", active);
        if (active) button.setAttribute("aria-current", "page");
        else button.removeAttribute("aria-current");
    });
    document.getElementById("page-title").textContent = titles[name];
    if (name === "academics") loadAcademicEvents();
    if (name === "resources") loadDocuments();
}

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("user-input");
const chatMessages = document.getElementById("chat-messages");
const chatStatus = document.getElementById("chat-status");
const sendButton = document.getElementById("send-button");

chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = `${Math.min(chatInput.scrollHeight, 120)}px`;
});

chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    await sendMessage(message);
});

document.querySelectorAll("[data-question]").forEach((button) => {
    button.addEventListener("click", () => sendMessage(button.dataset.question));
});

async function sendMessage(message) {
    const profileMatch = message.match(/\b(?:fy|sy|ty)\s*it\s*[- ]?([a-e])\b/i);
    if (profileMatch) {
        state.profile.course = `${profileMatch[0].toUpperCase().replace(/[- ]?[A-E]$/, "")}`;
        state.profile.division = profileMatch[1].toUpperCase();
        localStorage.setItem("vsitStudentProfile", JSON.stringify(state.profile));
    }
    appendMessage("user", message);
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendButton.disabled = true;
    chatStatus.textContent = "Checking VSIT information…";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, course: state.profile.course || null, division: state.profile.division || null }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(readApiError(data));
        const answer = data.bot_response || data.answer || "No answer was returned.";
        state.latestAnswer = answer;
        const links = [];
        if (data.result_url) links.push({ label: "Open result", url: data.result_url });
        if (data.resource_url) links.push({ label: "Open resource", url: data.resource_url });
        appendMessage("assistant", answer, data.sources || [], links, data.category);
        chatStatus.textContent = `Answered from ${formatCategory(data.category)}.`;
    } catch (error) {
        appendMessage("assistant", "I could not reach the assistant. Please check that the server is running and try again.");
        chatStatus.textContent = error.message;
    } finally {
        sendButton.disabled = false;
        chatInput.focus();
    }
}

function appendMessage(role, text, sources = [], links = [], category = "") {
    const article = document.createElement("article");
    article.className = `message ${role === "user" ? "user-message" : "assistant-message"}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = role === "user" ? "Y" : "V";

    const content = document.createElement("div");
    const author = document.createElement("p");
    author.className = "message-author";
    author.textContent = role === "user" ? "You" : "VSIT Assistant";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    if (role === "assistant" && category === "TIMETABLE" && /🕒/.test(text)) {
        renderTimetable(bubble, text);
    } else {
        text.split("\n").filter(Boolean).forEach((line) => {
            const paragraph = document.createElement("p");
            paragraph.textContent = line;
            bubble.appendChild(paragraph);
        });
    }

    if (sources.length) {
        const sourceList = document.createElement("div");
        sourceList.className = "source-list";
        sources.forEach((source) => {
            const chip = document.createElement("span");
            chip.className = "source-chip";
            chip.textContent = `${source.title} · page ${source.page}`;
            sourceList.appendChild(chip);
        });
        bubble.appendChild(sourceList);
    }

    links.forEach((link) => {
        try {
            const resolved = new URL(link.url, window.location.origin);
            if (!["http:", "https:"].includes(resolved.protocol)) return;
            const anchor = document.createElement("a");
            anchor.className = "resource-link";
            anchor.href = resolved.href;
            anchor.target = "_blank";
            anchor.rel = "noopener noreferrer";
            anchor.textContent = link.label;
            bubble.appendChild(anchor);
        } catch (_error) {
            // Ignore invalid links supplied by data records.
        }
    });

    content.append(author, bubble);
    article.append(avatar, content);
    chatMessages.appendChild(article);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderTimetable(container, text) {
    const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
    const heading = document.createElement("p");
    heading.className = "timetable-heading";
    heading.textContent = lines.shift() || "Timetable";
    container.appendChild(heading);
    const table = document.createElement("div");
    table.className = "timetable-grid";
    let current = null;
    const addRow = () => {
        if (!current) return;
        const row = document.createElement("div");
        row.className = "timetable-row";
        if (current.type && current.type.toLowerCase().includes("practical")) row.classList.add("practical-row");
        [current.time, current.subject, current.teacher, current.room, current.type].forEach((value) => {
            const cell = document.createElement("span");
            cell.textContent = value || "—";
            row.appendChild(cell);
        });
        table.appendChild(row);
    };
    lines.forEach((line) => {
        if (line.startsWith("🕒")) { addRow(); current = { time: line.replace("🕒", "").trim() }; }
        else if (line.startsWith("📚")) current.subject = line.replace("📚 Subject:", "").trim();
        else if (line.startsWith("👨‍🏫")) current.teacher = line.replace("👨‍🏫 Teacher:", "").trim();
        else if (line.startsWith("🏫")) current.room = line.replace("🏫 Room:", "").trim();
        else if (line.startsWith("📝")) current.type = line.replace("📝 Type:", "").trim();
    });
    addRow();
    const labels = ["Time", "Subject", "Teacher", "Room", "Type"];
    const header = document.createElement("div");
    header.className = "timetable-row timetable-header";
    labels.forEach((label) => { const cell = document.createElement("span"); cell.textContent = label; header.appendChild(cell); });
    table.prepend(header);
    container.appendChild(table);
}

function formatCategory(category) {
    return String(category || "available college data").toLowerCase();
}

function readApiError(data) {
    if (typeof data.detail === "string") return data.detail;
    return "The request could not be completed.";
}

const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const voiceButton = document.getElementById("voice-button");
const speechToggle = document.getElementById("speech-toggle");
const speechPause = document.getElementById("speech-pause");

if (Recognition) {
    const recognition = new Recognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.addEventListener("start", () => {
        voiceButton.classList.add("active");
        chatStatus.textContent = "Listening…";
    });
    recognition.addEventListener("result", (event) => {
        chatInput.value = event.results[0][0].transcript;
        chatInput.focus();
        chatStatus.textContent = "Voice input ready. Review it, then send.";
    });
    recognition.addEventListener("end", () => voiceButton.classList.remove("active"));
    recognition.addEventListener("error", () => {
        chatStatus.textContent = "Voice input was unavailable. You can continue typing.";
    });
    voiceButton.addEventListener("click", () => recognition.start());
} else {
    voiceButton.disabled = true;
    voiceButton.title = "Voice input is not supported in this browser";
}

function cleanSpeech(text) {
    return text.replace(/[📅🕒📚👨‍🏫🏫📝]/g, "").replace(/\s+/g, " ").trim();
}

speechToggle.addEventListener("click", () => {
    if (!("speechSynthesis" in window)) {
        chatStatus.textContent = "Answer playback is not supported in this browser.";
        return;
    }
    if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        speechPause.textContent = "⏸";
        speechPause.setAttribute("aria-label", "Pause answer playback");
        return;
    }
    window.speechSynthesis.cancel();
    if (!state.latestAnswer) {
        chatStatus.textContent = "Ask a question first, then play the latest answer.";
        return;
    }
    const utterance = new SpeechSynthesisUtterance(cleanSpeech(state.latestAnswer));
    utterance.lang = "en-IN";
    utterance.rate = 0.92;
    utterance.pitch = 1;
    utterance.onstart = () => { speechPause.hidden = false; speechToggle.classList.add("speaking"); };
    utterance.onend = () => { speechPause.hidden = true; speechToggle.classList.remove("speaking"); };
    window.speechSynthesis.speak(utterance);
});

speechPause.addEventListener("click", () => {
    if (!("speechSynthesis" in window)) return;
    if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        speechPause.textContent = "⏸";
        speechPause.setAttribute("aria-label", "Pause answer playback");
    } else {
        window.speechSynthesis.pause();
        speechPause.textContent = "▶";
        speechPause.setAttribute("aria-label", "Resume answer playback");
    }
});

document.getElementById("academic-filters").addEventListener("submit", (event) => {
    event.preventDefault();
    loadAcademicEvents(new FormData(event.currentTarget));
});
document.getElementById("refresh-academics").addEventListener("click", () => loadAcademicEvents());

async function loadAcademicEvents(formData = null) {
    const list = document.getElementById("academic-list");
    list.replaceChildren(emptyState("Loading academic events…"));
    const params = new URLSearchParams();
    if (formData) {
        formData.forEach((value, key) => {
            if (String(value).trim()) params.set(key, String(value).trim());
        });
    }
    try {
        const response = await fetch("/api/academics" + (params.size ? `?${params}` : ""));
        if (!response.ok) throw new Error("Could not load academic events.");
        const events = await response.json();
        list.replaceChildren();
        if (!events.length) list.append(emptyState("No published events match these filters."));
        events.forEach((event) => list.append(academicCard(event)));
    } catch (error) {
        list.replaceChildren(emptyState(error.message));
    }
}

function academicCard(event) {
    const card = document.createElement("article");
    card.className = "info-card";
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = event.event_type;
    const title = document.createElement("h3");
    title.textContent = event.title;
    const date = document.createElement("p");
    date.className = "meta";
    date.textContent = new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(event.starts_at));
    const description = document.createElement("p");
    description.textContent = event.description || "No additional details provided.";
    card.append(tag, title, date, description);
    return card;
}

async function loadDocuments() {
    const list = document.getElementById("document-list");
    list.replaceChildren(emptyState("Loading documents…"));
    try {
        const response = await fetch("/api/documents");
        if (!response.ok) throw new Error("Could not load documents.");
        const documents = await response.json();
        list.replaceChildren();
        if (!documents.length) list.append(emptyState("No college documents have been published yet."));
        documents.forEach((documentItem) => {
            const card = document.createElement("article");
            card.className = "info-card";
            const tag = document.createElement("span");
            tag.className = "tag";
            tag.textContent = documentItem.category;
            const title = document.createElement("h3");
            title.textContent = documentItem.title;
            const detail = document.createElement("p");
            detail.textContent = `${documentItem.filename} · ${documentItem.page_count} page${documentItem.page_count === 1 ? "" : "s"}`;
            card.append(tag, title, detail);
            list.append(card);
        });
    } catch (error) {
        list.replaceChildren(emptyState(error.message));
    }
}

document.getElementById("resource-search-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.getElementById("resource-query").value.trim();
    const results = document.getElementById("resource-results");
    results.replaceChildren(emptyState("Searching documents…"));
    try {
        const response = await fetch("/api/documents/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query }),
        });
        if (!response.ok) throw new Error("Document search failed.");
        const data = await response.json();
        results.replaceChildren();
        if (!data.hits.length) results.append(emptyState("No reliable document match was found."));
        data.hits.forEach((hit) => {
            const card = document.createElement("article");
            card.className = "search-hit";
            const heading = document.createElement("strong");
            heading.textContent = `${hit.title} · page ${hit.page}`;
            const excerpt = document.createElement("p");
            excerpt.textContent = hit.excerpt;
            card.append(heading, excerpt);
            results.append(card);
        });
    } catch (error) {
        results.replaceChildren(emptyState(error.message));
    }
});

function emptyState(message) {
    const element = document.createElement("div");
    element.className = "empty-state";
    element.textContent = message;
    return element;
}
