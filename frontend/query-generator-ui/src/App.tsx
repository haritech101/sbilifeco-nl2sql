import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import { useApi, type Schema } from "./ApiProvider";
import Markdown from "react-markdown";

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
    const [isSeekingAnswer, setIsSeekingAnswer] = useState<boolean>(false);


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
        setIsSeekingAnswer(true);

        let updatedChat: ChatMessage[] = [...chat, { role: "You", content: currentQuestion }];
        setChat(updatedChat);
        setCurrentQuestion("");

        if (chosenSchemaId === "") {
            console.error("No schema selected");
            return;
        }

        console.log(`Handling query request with schema ID: ${chosenSchemaId} and question: ${currentQuestion}`);

        const response = await api.query(chosenSchemaId, sessionId, currentQuestion, withThoughts);

        // Response recieved, either success or failure

        const newMessage: ChatMessage = { role: "Me", content: "" };
        if (!response.is_success) {
            newMessage.content = `Error: ${response.message}`;
        } else {
            newMessage.content = response.payload;
        }

        updatedChat = [
            ...updatedChat,
            newMessage
        ];

        setChat(updatedChat);
        setIsSeekingAnswer(false);
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

    const handleResetSession = async () => {
        setChat([]);
        setCurrentQuestion("");

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
                    <div className="d-flex flex-row gap-2 align-items-center">
                        <span>Thought dump?</span>
                        <input type="checkbox" checked={withThoughts} onChange={(e) => setWithThoughts(e.target.checked)} />
                        <span className="flex-grow-1"></span>
                        <button
                            className="btn bg-black text-white"
                            onClick={handleResetSession}
                        >Reset Session</button>
                    </div>
                </div>
                <div className="flex-grow-1 border overflow-auto chat-window d-flex flex-column gap-2 p-3">
                    <Markdown>
                        {
                            chat.map(
                                (message) =>
                                (
                                    message.role === "You"
                                        ? `**You asked:** ${message.content}`
                                        : `**My response:**\n\n${message.content}`
                                )
                            ).join("\n\n")
                        }
                    </Markdown>
                </div>
                <div className="d-flex flex-row gap-2">
                    <textarea value={currentQuestion} className="flex-grow-1 form-control" name="question" onChange={(e) => setCurrentQuestion(e.target.value)}></textarea>
                    <button
                        className="btn btn-primary"
                        name="generate"
                        onClick={() => { handleSubmitMessage() }}
                        disabled={currentQuestion.trim() === "" || chosenSchemaId === ""}
                    >{isSeekingAnswer ? <span className='spinner-border'></span> : `Generate Query`}</button>
                </div>
            </main>
        </div>
    )
}

export default App
