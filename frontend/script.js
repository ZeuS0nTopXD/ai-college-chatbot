function readStoredObject(key, fallback = {}) {
    try {
        const value = JSON.parse(localStorage.getItem(key) || "null");
        return value && typeof value === "object" && !Array.isArray(value) ? value : fallback;
    } catch (_error) {
        return fallback;
    }
}

function readStoredList(key) {
    try {
        const parsed = JSON.parse(localStorage.getItem(key) || "[]");
        return Array.isArray(parsed) ? parsed.filter((item) => typeof item === "string").slice(0, 6) : [];
    } catch (_error) {
        return [];
    }
}

function readStoredHistory() {
    try {
        const parsed = JSON.parse(localStorage.getItem("vsitChatHistory") || "[]");
        return Array.isArray(parsed) ? parsed.filter((item) => item && typeof item.question === "string" && typeof item.answer === "string").slice(0, 20) : [];
    } catch (_error) {
        return [];
    }
}

const studentTokenKey = "vsit-student-token";

const state = {
    latestAnswer: "",
    speechEnabled: true,
    profile: readStoredObject("vsitStudentProfile"),
    recentQuestions: readStoredList("vsitRecentQuestions"),
    chatHistory: readStoredHistory(),
    studentToken: localStorage.getItem(studentTokenKey) || sessionStorage.getItem(studentTokenKey),
    studentUser: null,
};

const views = {
    assistant: document.getElementById("assistant-view"),
    academics: document.getElementById("academics-view"),
    resources: document.getElementById("resources-view"),
    notices: document.getElementById("notices-view"),
    syllabus: document.getElementById("syllabus-view"),
    services: document.getElementById("services-view"),
    history: document.getElementById("history-view"),
    feedback: document.getElementById("feedback-view"),
};

const titles = {
    assistant: "Ask the VSIT Assistant",
    academics: "Academic calendar",
    resources: "College resources",
    notices: "Notices and circulars",
    syllabus: "Syllabus and courses",
    services: "Student services",
    history: "Chat history",
    feedback: "Student feedback",
};

document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => showView(button.dataset.view));
});

function showView(name) {
    document.querySelector(".app-shell").dataset.currentView = name;
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
    const pageTitle = document.getElementById("page-title");
    if (name === "assistant") pageTitle.innerHTML = "A little clarity.<br>A lot of possibility.";
    else pageTitle.textContent = titles[name];
    if (name === "academics") loadAcademicEvents();
    if (name === "resources") loadDocuments();
    if (["notices", "syllabus", "services"].includes(name)) loadTopicPage(name);
    if (name === "history") renderHistory();
    if (name === "feedback") updateFeedbackVisibility();
}

const authDialog = document.getElementById("student-auth-dialog");
const authForm = document.getElementById("student-auth-form");
let authMode = "login";

document.getElementById("student-login-button").addEventListener("click", () => openStudentAuth("login"));
document.getElementById("student-register-button").addEventListener("click", () => openStudentAuth("register"));
document.getElementById("feedback-login-action").addEventListener("click", () => openStudentAuth("login"));
document.getElementById("student-auth-close").addEventListener("click", () => authDialog.close());
document.getElementById("student-logout-button").addEventListener("click", studentLogout);
document.getElementById("student-auth-switch").addEventListener("click", () => openStudentAuth(authMode === "login" ? "register" : "login"));
authForm.addEventListener("submit", submitStudentAuth);

function openStudentAuth(mode) {
    authMode = mode;
    authForm.reset();
    document.getElementById("student-auth-title").textContent = mode === "register" ? "Create your account" : "Sign in";
    document.getElementById("student-auth-description").textContent = mode === "register" ? "Create a student account to share feedback with VSIT." : "Use your student account to send feedback.";
    document.getElementById("student-register-fields").hidden = mode !== "register";
    document.getElementById("student-register-fields").querySelector("input").required = mode === "register";
    document.getElementById("student-auth-submit").textContent = mode === "register" ? "Create account" : "Sign in";
    document.getElementById("student-auth-switch").textContent = mode === "register" ? "Already have an account? Sign in" : "Create an account";
    document.getElementById("student-auth-status").textContent = "";
    if (typeof authDialog.showModal === "function") authDialog.showModal();
    else authDialog.hidden = false;
}

async function submitStudentAuth(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const fields = new FormData(form);
    const payload = { email: String(fields.get("email") || ""), password: String(fields.get("password") || "") };
    if (authMode === "register") payload.name = String(fields.get("name") || "");
    const status = document.getElementById("student-auth-status");
    status.textContent = authMode === "register" ? "Creating account…" : "Signing in…";
    try {
        const endpoint = authMode === "register" ? "/api/auth/register" : "/api/auth/student-login";
        const response = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(readApiError(data));
        state.studentToken = data.access_token;
        state.studentUser = data.user;
        localStorage.setItem(studentTokenKey, state.studentToken);
        sessionStorage.removeItem(studentTokenKey);
        updateStudentAccount();
        authDialog.close();
        updateFeedbackVisibility();
    } catch (error) {
        status.textContent = error.message;
    }
}

async function loadStudentSession() {
    if (!state.studentToken) return updateStudentAccount();
    try {
        const response = await studentFetch("/api/auth/student-me");
        if (!response.ok) throw new Error("Session expired.");
        state.studentUser = await response.json();
    } catch (_error) {
        studentLogout();
        return;
    }
    updateStudentAccount();
    updateFeedbackVisibility();
}

function updateStudentAccount() {
    const signedIn = Boolean(state.studentUser && state.studentToken);
    document.getElementById("student-account-label").textContent = signedIn ? state.studentUser.name : "Guest student";
    document.getElementById("student-login-button").hidden = signedIn;
    document.getElementById("student-register-button").hidden = signedIn;
    document.getElementById("student-logout-button").hidden = !signedIn;
}

function studentLogout() {
    state.studentToken = null;
    state.studentUser = null;
    localStorage.removeItem(studentTokenKey);
    sessionStorage.removeItem(studentTokenKey);
    updateStudentAccount();
    updateFeedbackVisibility();
}

function updateFeedbackVisibility() {
    const signedIn = Boolean(state.studentToken && state.studentUser);
    document.getElementById("feedback-login-prompt").hidden = signedIn;
    document.getElementById("feedback-form").hidden = !signedIn;
}

async function studentFetch(url, options = {}) {
    const headers = new Headers(options.headers || {});
    if (state.studentToken) headers.set("Authorization", `Bearer ${state.studentToken}`);
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) studentLogout();
    return response;
}

document.getElementById("feedback-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const status = document.getElementById("feedback-status");
    const fields = new FormData(form);
    status.textContent = "Sending feedback…";
    try {
        const response = await studentFetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rating: Number(fields.get("rating")), message: String(fields.get("message") || ""), context: String(fields.get("context") || "") || null }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(readApiError(data));
        form.reset();
        status.textContent = "Thanks — your feedback was sent to the VSIT team.";
    } catch (error) {
        status.textContent = error.message;
    }
});

loadStudentSession();

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("user-input");
document.querySelector(".hero-cta").addEventListener("click", (event) => {
    event.preventDefault();
    showView("assistant");
    chatInput.focus();
});
const chatMessages = document.getElementById("chat-messages");
const chatStatus = document.getElementById("chat-status");
const sendButton = document.getElementById("send-button");
const initialChatMarkup = chatMessages.innerHTML;

function persistChatHistory() {
    try {
        localStorage.setItem("vsitChatHistory", JSON.stringify(state.chatHistory));
    } catch (_error) {
        // History is an enhancement; the assistant still works when storage is blocked.
    }
}

function rememberConversation(question, answer, category = "") {
    state.chatHistory = [
        { question, answer, category, createdAt: new Date().toISOString() },
        ...state.chatHistory.filter((item) => item.question !== question),
    ].slice(0, 20);
    persistChatHistory();
    renderConversationList();
    if (document.querySelector(".app-shell")?.dataset.currentView === "history") renderHistory();
}

function formatConversationTime(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const elapsed = Math.max(0, Date.now() - date.getTime());
    const minutes = Math.floor(elapsed / 60000);
    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    if (hours < 48) return "Yesterday";
    return date.toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

function renderConversationList() {
    const list = document.getElementById("conversation-list");
    const count = document.getElementById("conversation-count");
    if (!list) return;
    list.replaceChildren();
    const conversations = state.chatHistory.slice(0, 8);
    if (count) count.textContent = String(conversations.length);
    if (!conversations.length) {
        const empty = document.createElement("p");
        empty.className = "conversation-empty";
        empty.textContent = "Your recent questions will appear here.";
        list.appendChild(empty);
        return;
    }
    conversations.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "conversation-item";
        button.title = item.question;
        const title = document.createElement("strong");
        title.textContent = item.question;
        const meta = document.createElement("span");
        meta.textContent = `${item.category || "Assistant"} · ${formatConversationTime(item.createdAt)}`;
        button.append(title, meta);
        button.addEventListener("click", () => openSavedConversation(item));
        list.appendChild(button);
    });
}

function openSavedConversation(item) {
    showView("assistant");
    chatMessages.replaceChildren();
    appendMessage("user", item.question);
    appendMessage("assistant", item.answer, [], [], item.category);
    state.latestAnswer = item.answer;
    chatStatus.textContent = `Viewing saved ${formatCategory(item.category)} answer.`;
}

function renderHistory() {
    const list = document.getElementById("history-list");
    if (!list) return;
    list.replaceChildren();
    if (!state.chatHistory.length) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "No saved conversations yet. Ask the assistant a question to build your history.";
        list.appendChild(empty);
        return;
    }
    state.chatHistory.forEach((item) => {
        const card = document.createElement("article");
        card.className = "history-card";
        const meta = document.createElement("p");
        meta.className = "history-meta";
        meta.textContent = (item.category || "Assistant") + " · " + new Date(item.createdAt || Date.now()).toLocaleString();
        const question = document.createElement("h3");
        question.textContent = item.question;
        const answer = document.createElement("p");
        answer.textContent = item.answer;
        const replay = document.createElement("button");
        replay.type = "button";
        replay.className = "secondary-button";
        replay.textContent = "Ask again";
        replay.addEventListener("click", () => {
            showView("assistant");
            chatInput.value = item.question;
            chatInput.focus();
        });
        card.append(meta, question, answer, replay);
        list.appendChild(card);
    });
}

document.getElementById("history-clear").addEventListener("click", () => {
    state.chatHistory = [];
    persistChatHistory();
    renderConversationList();
    renderHistory();
});

function syncStudentContextControls() {
    const course = document.getElementById("student-course");
    const year = document.getElementById("student-year");
    const division = document.getElementById("student-division");
    const legacyYear = /^(FYIT|SYIT|TYIT)$/i.test(state.profile.course || "") ? state.profile.course.toUpperCase() : "";
    if (legacyYear) {
        state.profile.year = legacyYear;
        state.profile.course = "B.Sc. Information Technology";
        persistStudentContext();
    }
    if (course) course.value = state.profile.course || "";
    if (year) year.value = state.profile.year || "";
    if (division) division.value = state.profile.division || "";
}

function persistStudentContext() {
    try {
        localStorage.setItem("vsitStudentProfile", JSON.stringify(state.profile));
    } catch (_error) {
        // Browser storage is optional; the current session still has the context in memory.
    }
}

function renderRecentQuestions() {
    const container = document.getElementById("recent-questions");
    if (!container) return;
    container.replaceChildren();
    if (!state.recentQuestions.length) {
        container.hidden = true;
        return;
    }
    container.hidden = false;
    const label = document.createElement("span");
    label.className = "tool-label";
    label.textContent = "RECENT";
    container.appendChild(label);
    state.recentQuestions.forEach((question) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "recent-question";
        button.textContent = question;
        button.addEventListener("click", () => sendMessage(question));
        container.appendChild(button);
    });
}

function rememberQuestion(question) {
    state.recentQuestions = [question, ...state.recentQuestions.filter((item) => item !== question)].slice(0, 6);
    try {
        localStorage.setItem("vsitRecentQuestions", JSON.stringify(state.recentQuestions));
    } catch (_error) {
        // Recent questions remain available until refresh when storage is unavailable.
    }
    renderRecentQuestions();
}

document.getElementById("student-context-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const course = form.elements.course.value.trim();
    const year = form.elements.year.value.trim().toUpperCase();
    const division = form.elements.division.value.trim().toUpperCase();
    if (course) state.profile.course = course;
    else delete state.profile.course;
    if (year) state.profile.year = year;
    else delete state.profile.year;
    if (division) state.profile.division = division;
    else delete state.profile.division;
    persistStudentContext();
    chatStatus.textContent = course || year || division ? "Context saved for more relevant answers." : "Context cleared; answers will use your question only.";
});

document.getElementById("clear-context").addEventListener("click", () => {
    delete state.profile.course;
    delete state.profile.year;
    delete state.profile.division;
    persistStudentContext();
    syncStudentContextControls();
    chatStatus.textContent = "Context cleared; answers will use your question only.";
});

function startNewChat() {
    chatMessages.innerHTML = initialChatMarkup;
    state.latestAnswer = "";
    chatStatus.textContent = "Chat cleared. Your saved course and division are still available.";
    chatInput.value = "";
    chatInput.focus();
}

document.getElementById("clear-chat").addEventListener("click", startNewChat);
document.getElementById("new-chat").addEventListener("click", startNewChat);

document.getElementById("download-transcript").addEventListener("click", () => {
    const transcript = Array.from(chatMessages.querySelectorAll(".message")).map((message) => {
        const author = message.querySelector(".message-author")?.textContent || "Message";
        const text = message.querySelector(".message-bubble")?.innerText || "";
        return author + "\n" + text.trim();
    }).join("\n\n");
    const blob = new Blob(["VSIT Student Assistant transcript\n\n" + transcript + "\n"], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "vsit-assistant-" + new Date().toISOString().slice(0, 10) + ".txt";
    link.click();
    URL.revokeObjectURL(url);
});

syncStudentContextControls();
renderRecentQuestions();
renderConversationList();

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
    button.addEventListener("click", () => {
        let question = button.dataset.question;
        if (button.dataset.useContext === "true" && state.profile.year && state.profile.division) {
            question += " for " + (state.profile.year || state.profile.course) + ", division " + state.profile.division;
        }
        sendMessage(question);
    });
});

async function sendMessage(message) {
    const profileMatch = message.match(/\b(?:fy|sy|ty)\s*it\s*[- ]?([a-e])\b/i);
    if (profileMatch) {
        state.profile.course = `${profileMatch[0].toUpperCase().replace(/[- ]?[A-E]$/, "")}`;
        state.profile.division = profileMatch[1].toUpperCase();
        persistStudentContext();
        syncStudentContextControls();
    }
    rememberQuestion(message);
    appendMessage("user", message);
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendButton.disabled = true;
    chatStatus.textContent = "Checking VSIT information…";

    try {
        const payload = { message };
        if (state.profile.course) payload.course = state.profile.course;
        if (state.profile.year) payload.year = state.profile.year;
        if (state.profile.division) payload.division = state.profile.division;
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(readApiError(data));
        const answer = data.bot_response || data.answer || "No answer was returned.";
        state.latestAnswer = answer;
        rememberConversation(message, answer, data.category);
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
        else row.classList.add("lecture-row");
        [current.time, current.subject, current.teacher, current.room, current.type].forEach((value) => {
            const cell = document.createElement("span");
            cell.textContent = value || "—";
            row.appendChild(cell);
        });
        table.appendChild(row);
    };
    const addBreakRow = (label) => {
        addRow();
        current = null;
        const row = document.createElement("div");
        row.className = "timetable-row timetable-break";
        const cell = document.createElement("span");
        cell.colSpan = 5;
        cell.textContent = label.replace("⏸️", "").trim();
        row.appendChild(cell);
        table.appendChild(row);
    };
    lines.forEach((line) => {
        if (line.startsWith("⏸️")) addBreakRow(line);
        else if (line.startsWith("🕒")) { addRow(); current = { time: line.replace("🕒", "").trim() }; }
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
    const startsAt = new Date(event.starts_at);
    const dateOnly = /T00:00:00(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)?$/.test(event.starts_at);
    date.textContent = new Intl.DateTimeFormat("en-IN", dateOnly ? { dateStyle: "medium" } : { dateStyle: "medium", timeStyle: "short" }).format(startsAt);
    const description = document.createElement("p");
    description.textContent = event.description || "No additional details provided.";
    card.append(tag, title, date, description);
    if (event.resource_url) {
        const source = document.createElement("a");
        source.href = event.resource_url;
        source.target = "_blank";
        source.rel = "noopener noreferrer";
        source.textContent = "View on VSIT website ↗";
        card.append(source);
    }
    return card;
}

async function loadDocuments() {
    const list = document.getElementById("document-list");
    list.replaceChildren(emptyState("Loading VSIT resources…"));
    try {
        const [sourcesResponse, documentsResponse] = await Promise.all([
            fetch("/api/documents/official-sources?section=resources"),
            fetch("/api/documents").catch(() => null),
        ]);
        if (!sourcesResponse.ok) throw new Error("Could not load VSIT resources.");
        const sources = await sourcesResponse.json();
        const documents = documentsResponse?.ok ? await documentsResponse.json() : [];
        list.replaceChildren();
        const featuredUrl = document.querySelector("#resources-view .official-sample a")?.href;
        const remainingSources = sources.filter((item) => item.url !== featuredUrl);
        remainingSources.forEach((item) => list.append(officialSourceCard(item)));
        documents.forEach((item) => list.append(uploadedDocumentCard(item)));
        if (!remainingSources.length && !documents.length) list.append(emptyState("No additional VSIT resources are available right now."));
    } catch (error) {
        list.replaceChildren(emptyState(error.message));
    }
}

function officialSourceCard(item) {
    const card = document.createElement("article"); card.className = "info-card official-source-card";
    const tag = document.createElement("span"); tag.className = "tag"; tag.textContent = "VSIT website";
    const title = document.createElement("h3"); title.textContent = item.title;
    const detail = document.createElement("p"); detail.textContent = item.description;
    const link = document.createElement("a"); link.href = item.url; link.target = "_blank";
    link.rel = "noopener noreferrer"; link.textContent = "View on VSIT website ↗";
    card.append(tag, title, detail, link);
    return card;
}

function uploadedDocumentCard(item) {
    const card = document.createElement("article"); card.className = "info-card";
    const tag = document.createElement("span"); tag.className = "tag"; tag.textContent = item.category;
    const title = document.createElement("h3"); title.textContent = item.title;
    const detail = document.createElement("p");
    detail.textContent = `Indexed document · ${item.page_count} page${item.page_count === 1 ? "" : "s"}`;
    card.append(tag, title, detail);
    return card;
}

async function loadTopicPage(name) {
    const list = document.querySelector(`#${name}-view .topic-list`);
    list.replaceChildren(emptyState("Loading official VSIT sources…"));
    try {
        const [sourcesResponse, documentsResponse] = await Promise.all([
            fetch(`/api/documents/official-sources?section=${name}`),
            fetch("/api/documents").catch(() => null),
        ]);
        if (!sourcesResponse.ok) throw new Error("Could not load official sources.");
        const sources = await sourcesResponse.json();
        const documents = documentsResponse?.ok ? await documentsResponse.json() : [];
        const terms = { notices: ["news", "notice", "examination"], syllabus: ["syllabus", "academic", "programme"], services: ["contact", "student", "library", "placement", "admission"] }[name];
        const filtered = documents.filter((item) => terms.some((term) => `${item.title} ${item.category}`.toLowerCase().includes(term)));
        list.replaceChildren();
        const featuredUrl = document.querySelector(`#${name}-view .official-sample a`)?.href;
        const remainingSources = sources.filter((item) => item.url !== featuredUrl);
        remainingSources.forEach((item) => list.append(officialSourceCard(item)));
        filtered.forEach((item) => list.append(uploadedDocumentCard(item)));
        if (!remainingSources.length && !filtered.length) list.append(emptyState("No additional VSIT sources are available right now."));
    } catch (error) { list.replaceChildren(emptyState(error.message)); }
}

document.getElementById("resource-search-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = document.getElementById("resource-query").value.trim();
    const results = document.getElementById("resource-results");
    results.replaceChildren(emptyState("Searching VSIT resources…"));
    try {
        const [sourcesResponse, documentsResponse] = await Promise.all([
            fetch("/api/documents/official-sources"),
            fetch("/api/documents/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query }),
            }).catch(() => null),
        ]);
        if (!sourcesResponse.ok) throw new Error("Resource search failed.");
        const sources = await sourcesResponse.json();
        const data = documentsResponse?.ok ? await documentsResponse.json() : { hits: [] };
        const words = query.toLowerCase().replace(/\./g, "").match(/[a-z0-9]+/g) || [];
        const matchingSources = sources.filter((item) => {
            const content = `${item.title} ${item.description}`.toLowerCase().replace(/\./g, "");
            return words.some((word) => word.length > 2 && content.includes(word));
        });
        results.replaceChildren();
        matchingSources.forEach((item) => results.append(officialSourceCard(item)));
        if (!matchingSources.length && !data.hits.length) results.append(emptyState("No matching VSIT resource or uploaded document was found."));
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
