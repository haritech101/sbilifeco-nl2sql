import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import { useApi, type Schema } from "./ApiProvider";

type ChatMessage = {
    role: "You" | "Me";
    content: string;
}

function App() {
    const api = useApi();

    const [sessionId, setSessionId] = useState<string>("");
    const [schemas, setSchemas] = useState<Schema[]>([]);
    const [chosenSchemaId, setChosenSchemaId] = useState<string>("");
    const [chat, setChat] = useState<ChatMessage[]>([]);
    const [currentQuestion, setCurrentQuestion] = useState<string>("");
    const [withThoughts, setWithThoughts] = useState<boolean>(false);


    useEffect(() => {
        (async () => {
            await loadSchemas();
            await startASession();

        })();
    }, []);

    const loadSchemas = async () => {
        const response = await api.getSchemas();
        if (!response.is_success) {
            console.error("Failed to load schemas:", response.message);
            return;
        }

        setSchemas(response.payload);
    }

    const startASession = async () => {
        const sessionResponse = await api.startSession();
        if (!sessionResponse.is_success) {
            console.error("Failed to start session:", sessionResponse.message);
            return;
        }
        setSessionId(sessionResponse.payload);
    }

    const handleSubmitMessage = async () => {
        let updatedChat: ChatMessage[] = [...chat, { role: "You", content: currentQuestion }, { role: "Me", content: "..." }];
        setChat(updatedChat);
        setCurrentQuestion("");

        if (chosenSchemaId === "") {
            console.error("No schema selected");
            return;
        }

        console.log(`Handling query request with schema ID: ${chosenSchemaId} and question: ${currentQuestion}`);

        const response = await api.query(chosenSchemaId, sessionId, currentQuestion, withThoughts);
        if (!response.is_success) {
            updatedChat.splice(updatedChat.length - 1, 1); // Remove the last "Me" message
            updatedChat = [
                ...updatedChat,
                { role: "Me", content: `Error: ${response.message}` }];
            setChat(updatedChat);
            return;
        }

        updatedChat.splice(updatedChat.length - 1, 1); // Remove the last "Me" message
        updatedChat = [...updatedChat, { role: "Me", content: response.payload }];
        setChat(updatedChat);
    }

    const handleChooseSchema = async (schemaId: string) => {
        setChosenSchemaId(schemaId);
        setChat([]); // Clear chat when a new schema is selected
        setCurrentQuestion(""); // Clear the current question input

        const resetResponse = await api.reset(sessionId);
        if (!resetResponse.is_success) {
            console.error("Failed to reset state:", resetResponse.message);
        }
    }

    return (
        <div className="d-flex flex-column p-3 gap-3 vh-100">
            <header>
                <h1>Query Generator</h1>
            </header>
            <main className="d-flex flex-column gap-3 flex-grow-1">
                <div className="d-flex flex-column gap-2">
                    <label htmlFor="input-schema">Choose a Scheme to generate a query for:</label>
                    <select id="input-schema" name="schema" className="form-select" value={chosenSchemaId} onChange={(e) => handleChooseSchema(e.target.value)}>
                        <option value="">Select a Schema</option>
                        {schemas.map((schema, idx: number) => (
                            <option key={schema.id} value={schema.id}>
                                {schema.name}
                            </option>
                        ))}
                    </select>
                    <div className="d-flex flex-row gap-2">
                        <span>Thought dump?</span>
                        <input type="checkbox" checked={withThoughts} onChange={(e) => setWithThoughts(e.target.checked)} />
                    </div>
                </div>
                <div className="flex-grow-1 border overflow-auto chat-window d-flex flex-column gap-2 p-3">
                    {chat.map((message, idx) => (<>
                        <p key={idx}>
                            <strong>{message.role}:</strong>{
                                message.content === "..." ? (
                                    <div className="spinner-border"></div>
                                ) : (
                                    <>{
                                        message.content.split("\n").map((line, lineIdx) => (<>{line}<br /></>))
                                    }</>
                                )
                            }
                        </p>
                    </>))}
                </div>
                <div className="d-flex flex-row gap-2">
                    <textarea value={currentQuestion} className="flex-grow-1 form-control" name="question" onChange={(e) => setCurrentQuestion(e.target.value)}></textarea>
                    <button className="btn btn-primary" name="generate" onClick={() => { handleSubmitMessage() }}>Generate Query</button>
                </div>
            </main>
        </div>
    )
}

export default App
