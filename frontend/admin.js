const tokenKey = "vsit-admin-token";
let token = sessionStorage.getItem(tokenKey);
const loginPanel = document.getElementById("login-panel");
const workspace = document.getElementById("admin-workspace");
const adminStatus = document.getElementById("admin-status");

const resources = {
    academics: { form: "academic-form", list: "academics-list", label: (item) => item.title },
    knowledge: { form: "knowledge-form", list: "knowledge-list", label: (item) => item.question },
    faculty: { form: "faculty-form", list: "faculty-list", label: (item) => item.name },
    offices: { form: "office-form", list: "offices-list", label: (item) => item.office_name },
};

document.getElementById("admin-login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const password = new FormData(form).get("password");
    const status = document.getElementById("login-status");
    status.textContent = "Signing in…";
    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Login failed.");
        token = data.access_token;
        sessionStorage.setItem(tokenKey, token);
        form.reset();
        showWorkspace();
    } catch (error) {
        status.textContent = error.message;
    }
});

document.getElementById("logout-button").addEventListener("click", logout);

document.querySelectorAll("[data-admin-view]").forEach((button) => {
    button.addEventListener("click", () => showAdminView(button.dataset.adminView));
});

Object.entries(resources).forEach(([name, config]) => {
    const form = document.getElementById(config.form);
    form.addEventListener("submit", (event) => saveResource(event, name));
    form.addEventListener("reset", () => { form.elements.id.value = ""; });
});

document.getElementById("document-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    setStatus("Uploading document…");
    try {
        const response = await adminFetch("/api/admin/documents", {
            method: "POST",
            body: new FormData(form),
        });
        if (!response.ok) throw new Error(await responseMessage(response));
        form.reset();
        setStatus("Document uploaded.");
        await loadDocuments();
    } catch (error) {
        setStatus(error.message);
    }
});

async function showWorkspace() {
    loginPanel.hidden = true;
    workspace.hidden = false;
    await showAdminView("academics");
}

async function showAdminView(name) {
    document.querySelectorAll("[data-admin-panel]").forEach((panel) => {
        panel.hidden = panel.dataset.adminPanel !== name;
    });
    document.querySelectorAll("[data-admin-view]").forEach((button) => {
        button.classList.toggle("active", button.dataset.adminView === name);
    });
    if (name === "documents") await loadDocuments();
    else await loadResource(name);
}

async function saveResource(event, resourceName) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = formToObject(form);
    const id = payload.id;
    delete payload.id;
    setStatus(id ? "Updating record…" : "Creating record…");
    try {
        const response = await adminFetch(
            `/api/admin/${resourceName}${id ? `/${id}` : ""}`,
            {
                method: id ? "PATCH" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            },
        );
        if (!response.ok) throw new Error(await responseMessage(response));
        form.reset();
        form.elements.id.value = "";
        setStatus(id ? "Record updated." : "Record created.");
        await loadResource(resourceName);
    } catch (error) {
        setStatus(error.message);
    }
}

function formToObject(form) {
    const payload = {};
    Array.from(form.elements).forEach((field) => {
        if (!field.name) return;
        if (field.type === "checkbox") payload[field.name] = field.checked;
        else if (field.value === "") payload[field.name] = null;
        else payload[field.name] = field.value;
    });
    return payload;
}

async function loadResource(name) {
    const config = resources[name];
    const list = document.getElementById(config.list);
    list.textContent = "Loading…";
    try {
        const response = await adminFetch(`/api/admin/${name}`);
        if (!response.ok) throw new Error(await responseMessage(response));
        const records = await response.json();
        list.replaceChildren();
        if (!records.length) list.textContent = "No records yet.";
        records.forEach((record) => list.append(recordRow(name, record, config.label(record))));
    } catch (error) {
        list.textContent = error.message;
    }
}

function recordRow(resourceName, record, label) {
    const row = document.createElement("div");
    row.className = "record-row";
    const name = document.createElement("span");
    name.textContent = label;
    const actions = document.createElement("div");
    actions.className = "record-actions";
    const edit = button("Edit", () => populateForm(resourceName, record));
    const remove = button("Delete", () => deleteResource(resourceName, record.id), true);
    actions.append(edit, remove);
    row.append(name, actions);
    return row;
}

function populateForm(resourceName, record) {
    const form = document.getElementById(resources[resourceName].form);
    Object.entries(record).forEach(([key, value]) => {
        const field = form.elements[key];
        if (!field) return;
        if (field.type === "checkbox") field.checked = Boolean(value);
        else if (field.type === "datetime-local" && value) field.value = value.slice(0, 16);
        else field.value = value ?? "";
    });
    form.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function deleteResource(resourceName, id) {
    if (!window.confirm("Delete this record?")) return;
    const response = await adminFetch(`/api/admin/${resourceName}/${id}`, { method: "DELETE" });
    if (response.ok) {
        setStatus("Record deleted.");
        await loadResource(resourceName);
    } else setStatus(await responseMessage(response));
}

async function loadDocuments() {
    const list = document.getElementById("documents-list");
    list.textContent = "Loading…";
    const response = await adminFetch("/api/admin/documents");
    if (!response.ok) {
        list.textContent = await responseMessage(response);
        return;
    }
    const documents = await response.json();
    list.replaceChildren();
    if (!documents.length) list.textContent = "No documents uploaded.";
    documents.forEach((documentItem) => {
        const row = document.createElement("div");
        row.className = "record-row";
        const label = document.createElement("span");
        label.textContent = `${documentItem.title} (${documentItem.page_count} pages)`;
        row.append(label, button("Delete", () => deleteDocument(documentItem.id), true));
        list.append(row);
    });
}

async function deleteDocument(id) {
    if (!window.confirm("Delete this document and its searchable passages?")) return;
    const response = await adminFetch(`/api/admin/documents/${id}`, { method: "DELETE" });
    if (response.ok) {
        setStatus("Document deleted.");
        await loadDocuments();
    } else setStatus(await responseMessage(response));
}

function button(label, action, danger = false) {
    const element = document.createElement("button");
    element.type = "button";
    element.className = `small-button${danger ? " danger-button" : ""}`;
    element.textContent = label;
    element.addEventListener("click", action);
    return element;
}

async function adminFetch(url, options = {}) {
    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) logout();
    return response;
}

async function responseMessage(response) {
    const data = await response.json().catch(() => ({}));
    return typeof data.detail === "string" ? data.detail : "The request could not be completed.";
}

function setStatus(message) { adminStatus.textContent = message; }

function logout() {
    token = null;
    sessionStorage.removeItem(tokenKey);
    workspace.hidden = true;
    loginPanel.hidden = false;
    document.getElementById("login-status").textContent = "Session ended.";
}

if (token) showWorkspace();
