const button = document.getElementById("summarizeBtn");
const copyBtn = document.getElementById("copyBtn");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");
const resultCard = document.getElementById("resultCard");
const robot = document.getElementById("robot");
const greeting = document.getElementById("greeting");

const API_URL = "http://127.0.0.1:8000/summarize";
let rawSummary = "";

function setState(state, message = "", kind = "") {
    robot.dataset.state = state;
    statusEl.textContent = message;
    statusEl.className = "status" + (kind ? " " + kind : "");
}

// Adds text to an element, turning **bold** into <strong> without using innerHTML.
function addInline(parent, text) {
    text.split(/\*\*(.+?)\*\*/g).forEach((part, i) => {
        if (!part) return;
        if (i % 2) {
            const b = document.createElement("strong");
            b.textContent = part;
            parent.appendChild(b);
        } else {
            parent.appendChild(document.createTextNode(part));
        }
    });
}

// Safe mini-Markdown: headings, bullet lists, bold, paragraphs.
function renderSummary(text) {
    result.replaceChildren();
    let list = null;

    for (const raw of text.split(/\r?\n/)) {
        const line = raw.trim();
        if (!line) { list = null; continue; }

        const bullet = line.match(/^[-*•]\s+(.*)/);
        const heading = line.match(/^#{1,6}\s+(.*)/);

        if (bullet) {
            if (!list) {
                list = document.createElement("ul");
                result.appendChild(list);
            }
            const li = document.createElement("li");
            addInline(li, bullet[1]);
            list.appendChild(li);
        } else {
            list = null;
            const el = document.createElement(heading ? "h4" : "p");
            addInline(el, heading ? heading[1] : line);
            result.appendChild(el);
        }
    }
}

button.addEventListener("click", async () => {
    const style = document.querySelector('input[name="style"]:checked').value;

    button.disabled = true;
    resultCard.hidden = true;
    greeting.textContent = "On it! Let me read this page...";
    setState("working", "Reading current webpage...");

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || !tab.id || !/^https?:/.test(tab.url || "")) {
            throw new Error("Open a normal webpage first.");
        }

        const extracted = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body?.innerText || ""
        });

        const pageText = extracted[0]?.result?.trim();
        if (!pageText) {
            throw new Error("No readable webpage text found.");
        }

        setState("working", "Sending page text to AI...");

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                content: pageText.slice(0, 8000),
                source: "Chrome webpage",
                style: style
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Summarization failed.");
        }

        rawSummary = data.summary;
        renderSummary(rawSummary);
        resultCard.hidden = false;
        greeting.textContent = "All done! Here's your summary.";
        setState("happy", "Summary generated successfully.", "ok");

    } catch (error) {
        const message = error instanceof TypeError
            ? "Can't reach the backend. Is it running on port 8000?"
            : error.message;
        greeting.textContent = "Oops, something went wrong.";
        setState("error", message, "error");
    } finally {
        button.disabled = false;
    }
});

copyBtn.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(rawSummary);
        copyBtn.textContent = "Copied";
    } catch {
        copyBtn.textContent = "Copy failed";
    }
    setTimeout(() => { copyBtn.textContent = "Copy"; }, 1500);
});