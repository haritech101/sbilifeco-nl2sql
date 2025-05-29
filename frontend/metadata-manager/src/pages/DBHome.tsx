import { useEffect, useState } from "react";
import { useApi, type Table } from "../api/ApiProvider";
import { useParams } from 'react-router-dom';

export default function DBHomePage() {
    const api = useApi();
    if (!api) {
        return <div>Error: API not available</div>;
    }

    const { dbId } = useParams<{ dbId: string }>();
    if (!dbId) {
        return <div>Error: Database ID is not provided</div>;
    }

    const [loadedTables, setLoadedTables] = useState<Table[]>([]);

    useEffect(() => {
        (async () => { loadTables(); })();
    }, []);

    const loadTables = async () => {
        const response = await api.getTables(dbId);
        if (!response.is_success) {
            console.error("Failed to load tables:", response.message);
            return;
        }
        if (response.payload == null) {
            console.error("List of tables is inexplicably null");
            return;
        }

        setLoadedTables(response.payload);
    }

    return (
        <>{
            <div className="p-5">
                <div className="row p-2">
                    <div className="col p-2 fw-bold">Table</div>
                    <div className="col p-2 fw-bold">Description</div>
                </div>
                {loadedTables.map((table) => (
                    <div className="row" key={table.id}>
                        <div className="col border p-2"><a href={`/dbs/${dbId}/tables/${table.id}`}>{table.name}</a></div>
                        <div className="col border p-2">{table.description}</div>
                    </div>
                ))}
            </div>

        }</>
    );
}
