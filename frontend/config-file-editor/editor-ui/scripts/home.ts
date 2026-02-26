import { basicSetup } from "./codemirror/basic-setup/dist/index.js";
import { EditorView } from "./codemirror/view/dist/index.js";

const API_BASE_URL = "http://localhost:11200";
let currentFileId = "";
let editor: EditorView | null = null;

const onSelectFile = async (selectedFileId: string) => {
    if (!selectedFileId) {
        return;
    }

    currentFileId = selectedFileId;
    const url = `${API_BASE_URL}/api/v1/updatable-objects/${selectedFileId}`;
    const req = new Request(url);
    const response = await fetch(req);
    if (!response.ok) {
        console.log(`Failed to fetch file content: ${await response.text()}`);
        return;
    }

    const apiResponse = await response.json();
    if (!apiResponse.is_success) {
        console.log(`API reported failure: ${apiResponse.message}`);
        return;
    }

    const fileContent = apiResponse.payload;
    // const textarea = document.getElementById(
    //     "file-content",
    // ) as HTMLTextAreaElement;
    // textarea.value = fileContent;
    if (editor) {
        editor.dispatch({
            changes: {
                from: 0,
                to: editor.state.doc.length,
                insert: fileContent,
            },
        });
    }
};

const onSaveFile = async () => {
    if (!currentFileId) {
        console.log("No file selected to save.");
        return;
    }

    const feedbackPanel = document.getElementById(
        "feedback-panel",
    ) as HTMLDivElement;
    feedbackPanel.innerText = "Saving...";

    // const textarea = document.getElementById(
    //     "file-content",
    // ) as HTMLTextAreaElement;
    if (!editor) {
        console.log("Editor not initialized.");
        feedbackPanel.innerText = "Error: Editor not initialized.";
        return;
    }

    const updatedContent = editor.state.doc.toString() ?? "";

    const url = `${API_BASE_URL}/api/v1/updatable-objects/${currentFileId}`;
    const req = new Request(url, {
        method: "PUT",
        headers: {
            "Content-Type": "text/plain",
        },
        body: updatedContent,
    });
    const response = await fetch(req);
    if (!response.ok) {
        const message = await response.text();
        console.log(`Failed to save file content: ${message}`);
        feedbackPanel.innerText = `Error saving file. ${message}`;
        return;
    }

    const apiResponse = await response.json();
    if (!apiResponse.is_success) {
        console.log(`API reported failure: ${apiResponse.message}`);
        feedbackPanel.innerText = `Error saving file. ${apiResponse.message}`;
        return;
    }

    feedbackPanel.innerText = "File saved successfully.";
};

const init = async () => {
    document
        .getElementById("which-file")
        ?.addEventListener("change", async (event) => {
            const selectElement = event.target as HTMLSelectElement;
            await onSelectFile(selectElement.value);
        });

    document
        .getElementById("save-file")
        ?.addEventListener("click", async () => {
            await onSaveFile();
        });

    editor = new EditorView({
        extensions: [basicSetup],
        parent: document.getElementById("file-content")!,
    });
};

await init();
