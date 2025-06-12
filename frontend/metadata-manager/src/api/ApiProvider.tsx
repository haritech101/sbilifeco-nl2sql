import React, { type PropsWithChildren } from "react";

const api_proto = import.meta.env.VITE_API_PROTO || 'http';
const api_host = import.meta.env.VITE_API_HOST || 'localhost';
const api_port = import.meta.env.VITE_API_PORT || '80';

const port_part = api_port && api_port !== '80' ? `:${api_port}` : '';
const api_url = `${api_proto}://${api_host}${port_part}/api/v1/db-metadata`;

export type ApiResponse<T> = {
    is_success: boolean;
    code: number;
    message: string;
    payload?: T | null;
}

export type Field = {
    id?: string;
    name: string;
    type?: string;
    description?: string;
    aka?: string;
};

export type Table = {
    id?: string;
    name: string;
    description?: string;
    fields?: Field[] | null;
};

export type KPI = {
    id?: string;
    name: string;
    aka?: string;
    description?: string;
    formula: string;
}

export type DB = {
    id?: string;
    name: string;
    description?: string;
    tables?: Table[] | null;
};

export interface Api {
    getDBs: () => Promise<ApiResponse<DB[]>>;
    getTables: (dbId: string) => Promise<ApiResponse<Table[]>>;
    upsertKPI(dbId: string, kpi: KPI): Promise<ApiResponse<string>>;
    deleteKPI: (dbId: string, kpiId: string) => Promise<ApiResponse<null>>;
    getKPIs: (dbId: string) => Promise<ApiResponse<KPI[]>>;
    upsertField: (dbId: string, tableId: string, field: Field) => Promise<ApiResponse<string>>;
    deleteField: (dbId: string, tableId: string, fieldId: string) => Promise<ApiResponse<null>>;
    getFields: (dbId: string, tableId: string) => Promise<ApiResponse<Field[]>>;
}

export const processHttpResponse = async (response: Response): Promise<ApiResponse<any>> => {
    if (!response.ok) {
        return {
            is_success: false,
            code: response.status,
            message: response.statusText,
            payload: null
        };
    }

    return await response.json();
}

const api: Api = {
    getDBs: async (): Promise<ApiResponse<DB[]>> => {
        const response = await fetch(`${api_url}/dbs`);
        return processHttpResponse(response);
    },
    getTables: async (dbId: string): Promise<ApiResponse<Table[]>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/tables`);
        return processHttpResponse(response);
    },
    upsertKPI: async (dbId: string, kpi: KPI): Promise<ApiResponse<string>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/kpis`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(kpi)
        });
        return processHttpResponse(response);
    },
    deleteKPI: async (dbId: string, kpiId: string): Promise<ApiResponse<null>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/kpis/${kpiId}`, {
            method: 'DELETE'
        });
        return processHttpResponse(response);
    },
    getKPIs: async (dbId: string): Promise<ApiResponse<KPI[]>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/kpis`);
        return processHttpResponse(response);
    },
    upsertField: async (dbId: string, tableId: string, field: Field): Promise<ApiResponse<string>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/tables/${tableId}/fields`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(field)
        });
        return processHttpResponse(response);
    },
    deleteField: async (dbId: string, tableId: string, fieldId: string): Promise<ApiResponse<null>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/tables/${tableId}/fields/${fieldId}`, {
            method: 'DELETE'
        });
        return processHttpResponse(response);
    },
    getFields: async (dbId: string, tableId: string): Promise<ApiResponse<Field[]>> => {
        const response = await fetch(`${api_url}/dbs/${dbId}/tables/${tableId}/fields`);
        return processHttpResponse(response);
    }
}

export const ApiContext = React.createContext<Api | null>(null);

export const useApi = (): Api | null => {
    return React.useContext(ApiContext);
}

export default function ApiProvider({ children }: PropsWithChildren) {
    return <ApiContext.Provider value={api}>
        {children}
    </ApiContext.Provider>;
}