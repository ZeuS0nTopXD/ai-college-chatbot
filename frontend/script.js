// ============================================================
// VSIT STUDENT ASSISTANT - FRONTEND CHAT SCRIPT
// ============================================================

// FastAPI backend URL
const API_URL = "http://127.0.0.1:8000/chat";


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const sendButton = document.getElementById("send-button");

    const message = userInput.value.trim();

    // Do not send empty messages
    if (message === "") {
        return;
    }


    // ========================================================
    // ADD USER MESSAGE
    // ========================================================

    const userMessageHTML = `
        <div class="message user-message">

            <div class="message-label">
                👤 You
            </div>

            <div class="message-text">
                ${escapeHTML(message)}
            </div>

        </div>
    `;

    chatBox.insertAdjacentHTML(
        "beforeend",
        userMessageHTML
    );


    // Clear input
    userInput.value = "";


    // Scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;


    // Disable send button
    sendButton.disabled = true;
    sendButton.innerText = "Sending...";


    // ========================================================
    // LOADING MESSAGE
    // ========================================================

    const loadingId = "loading-message";

    const loadingMessageHTML = `
        <div class="message bot-message" id="${loadingId}">

            <div class="message-label">
                🤖 Assistant
            </div>

            <div class="message-text thinking-message">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>
    `;

    chatBox.insertAdjacentHTML(
        "beforeend",
        loadingMessageHTML
    );

    chatBox.scrollTop = chatBox.scrollHeight;


    // ========================================================
    // SEND REQUEST TO FASTAPI
    // ========================================================

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        // ====================================================
        // CHECK SERVER RESPONSE
        // ====================================================

        if (!response.ok) {

            throw new Error(
                "Unable to connect to the chatbot server."
            );

        }


        // Get JSON response
        const data = await response.json();


        // ====================================================
        // REMOVE LOADING MESSAGE
        // ====================================================

        const loadingMessage =
            document.getElementById(loadingId);

        if (loadingMessage) {
            loadingMessage.remove();
        }


        // ====================================================
        // GET BOT RESPONSE
        // ====================================================

        let botResponse = "";


        if (data.bot_response) {

            botResponse = data.bot_response;

        }

        else if (data.response) {

            botResponse = data.response;

        }

        else if (data.answer) {

            botResponse = data.answer;

        }

        else {

            botResponse =
                "Sorry, I could not understand the response from the server.";

        }


        // ====================================================
        // ADD BOT RESPONSE
        // ====================================================

        const botMessageHTML = `

            <div class="message bot-message">

                <div class="message-label">
                    🤖 Assistant
                </div>

                <div class="message-text">

                    ${formatResponse(botResponse)}

                </div>

            </div>

        `;

        chatBox.insertAdjacentHTML(
            "beforeend",
            botMessageHTML
        );


        // ====================================================
        // HANDLE RESULT LINK IF BACKEND SENDS ONE
        // ====================================================

        if (data.result_url) {

            addResultLink(
                chatBox,
                data.result_url
            );

        }

        else if (data.result_link) {

            addResultLink(
                chatBox,
                data.result_link
            );

        }

        else if (data.url) {

            addResultLink(
                chatBox,
                data.url
            );

        }


    }


    // ========================================================
    // ERROR HANDLING
    // ========================================================

    catch (error) {

        // Remove loading message
        const loadingMessage =
            document.getElementById(loadingId);

        if (loadingMessage) {

            loadingMessage.remove();

        }


        // Error message
        const errorMessageHTML = `

            <div class="message bot-message">

                <div class="message-label">
                    ⚠️ Error
                </div>

                <div class="message-text">

                    Unable to connect to the chatbot.

                    <br><br>

                    Please make sure the FastAPI server is running.

                </div>

            </div>

        `;

        chatBox.insertAdjacentHTML(
            "beforeend",
            errorMessageHTML
        );


        console.error(
            "Chatbot Error:",
            error
        );

    }


    // ========================================================
    // FINALLY
    // ========================================================

    finally {

        // Enable button
        sendButton.disabled = false;

        sendButton.innerText = "Send ➤";


        // Scroll to latest message
        chatBox.scrollTop =
            chatBox.scrollHeight;


        // Focus input
        userInput.focus();

    }

}



// ============================================================
// ADD RESULT LINK
// ============================================================

function addResultLink(chatBox, url) {

    if (!url) {
        return;
    }


    const resultHTML = `

        <div class="message bot-message">

            <div class="message-label">
                🔗 Result Page
            </div>

            <div class="message-text">

                <a
                    href="${escapeAttribute(url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="result-link"
                >

                    📄 Open Result Page

                </a>

            </div>

        </div>

    `;


    chatBox.insertAdjacentHTML(
        "beforeend",
        resultHTML
    );


    chatBox.scrollTop =
        chatBox.scrollHeight;

}



// ============================================================
// ENTER KEY SUPPORT
// ============================================================

document
    .getElementById("user-input")
    .addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();

            }

        }
    );



// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}



// ============================================================
// ESCAPE ATTRIBUTE
// ============================================================

function escapeAttribute(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}



// ============================================================
// FORMAT BOT RESPONSE
// ============================================================
function formatResponse(text) {

    if (!text) {
        return "";
    }

    let formattedText = String(text);

    // Detect HTML anchor tags
    if (formattedText.includes("<a ")) {
        return formattedText;
    }

    // Escape everything else
    formattedText = escapeHTML(formattedText);

    // Markdown bold
    formattedText = formattedText.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    // Markdown links
    formattedText = formattedText.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        (match, text, url) => `
            <a href="${escapeAttribute(url)}"
               target="_blank"
               rel="noopener noreferrer"
               class="result-link">
                ${text}
            </a>
        `
    );

    // Plain URLs
    formattedText = formattedText.replace(
        /(https?:\/\/[^\s<]+)/g,
        (url) => `
            <a href="${escapeAttribute(url)}"
               target="_blank"
               rel="noopener noreferrer"
               class="result-link">
                🔗 Open Link
            </a>
        `
    );

    // Bullets
    formattedText = formattedText.replace(
        /^\s*[\*\-]\s+/gm,
        "• "
    );

    // New lines
    formattedText = formattedText.replace(
        /\n/g,
        "<br>"
    );

    return formattedText;
}



// ============================================================
// QUICK QUESTIONS
// ============================================================

function askQuickQuestion(question) {

    const userInput =
        document.getElementById("user-input");


    userInput.value =
        question;


    sendMessage();

}