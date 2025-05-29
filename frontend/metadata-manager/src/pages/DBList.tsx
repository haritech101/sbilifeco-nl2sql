import { useEffect, useState } from "react";
import { useApi, type DB } from "../api/ApiProvider";


export default function DBListPage() {
    const api = useApi();
    if (!api) {
        return <div>Error: API not available</div>;
    }

    const [loadedDBs, setLoadedDBs] = useState<DB[]>([]);

    useEffect(() => {
        (async () => {
            await loadDBs();
        })();
    }, [])

    const loadDBs = async () => {
        const response = await api.getDBs();
        if (!response.is_success) {
            console.error("Failed to load databases:", response.message);
            return;
        }
        if (response.payload == null) {
            console.error("List of databases is inexplicably null");
            return;
        }

        setLoadedDBs(response.payload);
    }

    return (
        <div className="p-5">
            <div className="row p-2">
                <div className="col p-2 fw-bold">Database</div>
                <div className="col p-2 fw-bold">Description</div>
            </div>
            {loadedDBs.map((db) => (<>
                <div className="row" key={db.id}>
                    <div className="col border p-2"><a href={`/dbs/${db.id}`}>{db.name}</a></div>
                    <div className="col border p-2">{db.description}</div>
                </div>
            </>))}
        </div>
    );
}
