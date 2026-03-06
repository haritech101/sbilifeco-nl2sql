import type { PropsWithChildren } from "react";
import React from "react";

const metadataUrl = import.meta.env.VITE_METADATA_URL;
const queryFlowUrl = import.meta.env.VITE_QUERY_FLOW_URL;

export type ApiResponse<T> = {
    is_success: boolean;
    code: number;
    message: string;
    payload: T | null;
}

export type Schema = {
    id: string;
    name: string;
}

export type QueryFlowRequest = {
    session_id: string;
    request_id: string;
    db_id: string;
    question: string;
    is_pii_allowed: boolean;
    with_thoughts: boolean;
}

export interface Api {
    getSchemas: () => Promise<ApiResponse<Schema[]>>;
    query: (schemaId: string, sessionId: string, question: string, withThoughts: boolean) => Promise<ApiResponse<string>>;
    ask: (req: QueryFlowRequest) => Promise<ApiResponse<ReadableStream>>;
    startSession: () => Promise<ApiResponse<string>>;
    stopSession: (sessionId: string) => Promise<ApiResponse<null>>;
    reset: (sessionId: string) => Promise<ApiResponse<null>>;
}

export const ApiContext = React.createContext<Api>({
    getSchemas: async () => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: []
        };
    },
    query: async (schemaId: string, sessionId: string, question: string, withThoughts: boolean) => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: null
        };
    },
    ask: async (req: QueryFlowRequest): Promise<ApiResponse<ReadableStream>> => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: null
        };
    },
    startSession: async (): Promise<ApiResponse<string>> => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: null
        };
    },
    stopSession: async (sessionId: string): Promise<ApiResponse<null>> => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: null
        };
    },
    reset: async (sessionId: string): Promise<ApiResponse<null>> => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: null
        };
    }
});

const processHttpResponse = async (httpResponse: Response): Promise<ApiResponse<any>> => {
    try {
        if (!httpResponse.ok) {
            return {
                is_success: false,
                code: httpResponse.status,
                message: await httpResponse.text(),
                payload: null
            };
        }


        return await httpResponse.json()
    } catch (error) {
        return {
            is_success: false,
            code: 500,
            message: `An error occurred while processing the response: ${error}`,
            payload: null
        }
    }
};

const api: Api = {
    getSchemas: async () => {
        return processHttpResponse(
            await fetch(`${metadataUrl}/api/v1/db-metadata/dbs`)
        );
    },
    query: async (schemaId: string, sessionId: string, question: string, withThoughts: boolean) => {
        return processHttpResponse(
            await fetch(`${queryFlowUrl}/api/v1/query-flow/sessions/${sessionId}/queries`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    db_id: schemaId,
                    question,
                    with_thoughts: withThoughts
                })
            })
        )
    },
    ask: async (req: QueryFlowRequest): Promise<ApiResponse<ReadableStreamDefaultReader>> => {
        try {
            const response = await fetch(`${queryFlowUrl}/api/v1/query-flow/asks`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(req)
            });

            if (!response.ok) {
                const errorText = await response.text();
                return {
                    is_success: false,
                    code: response.status,
                    message: errorText,
                    payload: null
                };
            }

            const reader = response.body;
            if (!reader) {
                return {
                    is_success: false,
                    code: 500,
                    message: "Failed to get response stream reader",
                    payload: null
                };
            }

            return {
                is_success: true,
                code: 200,
                message: "OK",
                payload: reader
            };
        } catch (error) {
            return {
                is_success: false,
                code: 500,
                message: `An error occurred while processing the request: ${error}`,
                payload: null
            };
        }
    },
    startSession: async (): Promise<ApiResponse<string>> => {
        return processHttpResponse(
            await fetch(`${queryFlowUrl}/api/v1/query-flow/sessions`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            })
        );
    },
    stopSession: async (sessionId: string): Promise<ApiResponse<null>> => {
        return processHttpResponse(
            await fetch(`${queryFlowUrl}/api/v1/query-flow/sessions/${sessionId}`, {
                method: "DELETE",
            })
        );
    },
    reset: async (sessionId: string): Promise<ApiResponse<null>> => {
        return processHttpResponse(
            await fetch(`${queryFlowUrl}/api/v1/query-flow/sessions/${sessionId}/reset`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({})
            })
        );
    }
}

export default function ApiProvider({ children }: PropsWithChildren) {
    return (<ApiContext.Provider value={api}>{children}</ApiContext.Provider>);
}

export const useApi = () => {
    return React.useContext(ApiContext);
}