import { basicSetup } from "codemirror";
import { Compartment, EditorState } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { python } from "@codemirror/lang-python";
import { markdown } from "@codemirror/lang-markdown";

const API_BASE_URL = "http://localhost:11200";
let currentFileId = "";
let editor: EditorView | null = null;

class Page {
    file_types = {
        test: null,
        nb_schema: python,
        generic_prompt: markdown,
        nb_prompt: markdown,
    };

    onSelectFile = async (selectedFileId: string) => {
        if (!selectedFileId) {
            return;
        }

        currentFileId = selectedFileId;
        const url = `${API_BASE_URL}/api/v1/updatable-objects/${selectedFileId}`;
        const req = new Request(url);
        const response = await fetch(req);
        if (!response.ok) {
            console.log(
                `Failed to fetch file content: ${await response.text()}`,
            );
            return;
        }

        const apiResponse = await response.json();
        if (!apiResponse.is_success) {
            console.log(`API reported failure: ${apiResponse.message}`);
            return;
        }

        const lang = new Compartment();

        const fileContent = apiResponse.payload;
        if (editor) {
            editor.dispatch({
                changes: {
                    from: 0,
                    to: editor.state.doc.length,
                    insert: fileContent,
                },
                effects: lang.reconfigure(
                    EditorState.languageData.of(
                        this.file_types[selectedFileId](),
                    ),
                ),
            });
        }
    };

    onSaveFile = async () => {
        if (!currentFileId) {
            console.log("No file selected to save.");
            return;
        }

        const feedbackPanel = document.getElementById(
            "feedback-panel",
        ) as HTMLDivElement;
        feedbackPanel.innerText = "Saving...";

        const textarea = document.getElementById(
            "file-content",
        ) as HTMLTextAreaElement;
        const updatedContent = textarea.value;

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

    init = async () => {
        document
            .getElementById("which-file")
            ?.addEventListener("change", async (event) => {
                const selectElement = event.target as HTMLSelectElement;
                await this.onSelectFile(selectElement.value);
            });

        document
            .getElementById("save-file")
            ?.addEventListener("click", async () => {
                await this.onSaveFile();
            });

        editor = new EditorView({
            extensions: [basicSetup],
            parent: document.getElementById("file-content")!,
        });
    };
}

const page = new Page();
await page.init();
