const state = {
    latestAnswer: "",
    speechEnabled: true,
    profile: JSON.parse(localStorage.getItem("vsitStudentProfile") || "{}"),
    studentToken: sessionStorage.getItem("vsit-student-token"),
    studentUser: null,
};

const views = {
    assistant: document.getElementById("assistant-view"),
    academics: document.getElementById("academics-view"),
    resources: document.getElementById("resources-view"),
    notices: document.getElementById("notices-view"),
    syllabus: document.getElementById("syllabus-view"),
    services: document.getElementById("services-view"),
    feedback: document.getElementById("feedback-view"),
};

const titles = {
    assistant: "Ask the VSIT Assistant",
    academics: "Academic calendar",
    resources: "College resources",
    notices: "Notices and circulars",
    syllabus: "Syllabus and courses",
    services: "Student services",
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
        sessionStorage.setItem("vsit-student-token", state.studentToken);
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
    sessionStorage.removeItem("vsit-student-token");
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
        else row.classList.add("lecture-row");
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
