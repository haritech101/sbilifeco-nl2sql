const API_BASE_URL = "http://localhost";
let currentFileId = "";

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
    const textarea = document.getElementById(
        "file-content"
    ) as HTMLTextAreaElement;
    textarea.value = fileContent;
};

const onSaveFile = async () => {
    if (!currentFileId) {
        console.log("No file selected to save.");
        return;
    }

    const feedbackPanel = document.getElementById(
        "feedback-panel"
    ) as HTMLDivElement;
    feedbackPanel.innerText = "Saving...";

    const textarea = document.getElementById(
        "file-content"
    ) as HTMLTextAreaElement;
    const updatedContent = textarea.value;

    const url = `${API_BASE_URL}/api/v1/updatable-objects/${currentFileId}`;
    const req = new Request(url, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
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

document
    .getElementById("which-file")
    ?.addEventListener("change", async (event) => {
        const selectElement = event.target as HTMLSelectElement;
        await onSelectFile(selectElement.value);
    });

document.getElementById("save-file")?.addEventListener("click", async () => {
    await onSaveFile();
});
