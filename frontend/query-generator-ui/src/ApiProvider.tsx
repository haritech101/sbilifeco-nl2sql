import type { PropsWithChildren } from "react";
import React from "react";

const metadataUrl = import.meta.env.VITE_METADATA_URL;
const queryFlowUrl = import.meta.env.VITE_QUERY_FLOW_URL;

export type ApiResponse<T> = {
    is_success: boolean;
    code: number;
    message: string;
    payload: T;
}

export type Schema = {
    id: string;
    name: string;
}

export interface Api {
    getSchemas: () => Promise<ApiResponse<Schema[]>>;
    query: (schemaId: string, question: string) => Promise<ApiResponse<string>>;
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
    query: async (schemaId: string, question: string) => {
        return {
            is_success: false,
            code: 501,
            message: "Not implemented",
            payload: ""
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
            message: "An error occurred while processing the response.",
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
    query: async (schemaId: string, question: string) => {
        console.log(`Sending HTTP request with schema ID: ${schemaId} and question: ${question}`);

        return processHttpResponse(
            await fetch(`${queryFlowUrl}/api/v1/query-flow/queries`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    db_id: schemaId,
                    question
                })
            })
        )
    }
}

export default function ApiProvider({ children }: PropsWithChildren) {
    return (<ApiContext.Provider value={api}>{children}</ApiContext.Provider>);
}

export const useApi = () => {
    return React.useContext(ApiContext);
}