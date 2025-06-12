import { useEffect, useState } from "react";
import { useApi, type KPI, type Table } from "../api/ApiProvider";
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
    const [loadedKPIs, setLoadedKPIs] = useState<KPI[]>([]);
    const [currentKpiId, setCurrentKpiId] = useState<string>("");
    const [isEditingKPI, setIsEditingKPI] = useState<boolean>(false);
    const [isDeletingKPI, setIsDeletingKPI] = useState<boolean>(false);

    useEffect(() => {
        (async () => { loadTables(); loadKPIs(); })();
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

    const loadKPIs = async () => {
        const response = await api.getKPIs(dbId);
        if (!response.is_success) {
            console.error("Failed to load KPIs:", response.message);
            return;
        }
        if (response.payload == null) {
            console.error("List of KPIs is inexplicably null");
            return;
        }

        setLoadedKPIs(response.payload);
    }

    const handleStartCreateKPI = () => {
        setLoadedKPIs([...loadedKPIs, { id: '', name: '', aka: '', description: '', formula: '' }]);
        setIsEditingKPI(true);
        setCurrentKpiId('');
    }

    const handleStartEditKPI = (kpiId: string) => {
        setCurrentKpiId(kpiId);
        setIsEditingKPI(true);
    }

    const handleCancelEditKPI = () => {
        if (currentKpiId === '') {
            // If we are canceling a new KPI creation, remove the empty KPI from the list
            const updatedKPIs = loadedKPIs.filter(kpi => kpi.id !== "");
            setLoadedKPIs(updatedKPIs);
        }
        resetKPIEditing();
    }

    const resetKPIEditing = () => {
        setIsEditingKPI(false);
        setCurrentKpiId('');
    }

    const handleSaveKPI = async () => {
        const kpi = loadedKPIs.find(kpi => kpi.id === currentKpiId);
        if (!kpi) {
            console.error("KPI not found for saving");
            resetKPIEditing();
            loadKPIs();
            return;
        }

        const upsertResponse = await api.upsertKPI(dbId, kpi);
        if (!upsertResponse.is_success) {
            console.error("Failed to save KPI:", upsertResponse.message);
        }

        resetKPIEditing();
        loadKPIs();
    }

    const handleStartDeleteKPI = (kpiId: string) => {
        setCurrentKpiId(kpiId);
        setIsDeletingKPI(true);
    }

    const resetDeleteKPI = () => {
        setIsDeletingKPI(false);
        setCurrentKpiId('');
    }

    const handleConfirmDeleteKPI = async () => {
        if (!currentKpiId) {
            console.error("No KPI ID provided for deletion");
            resetDeleteKPI();
            return;
        }

        const deleteResponse = await api.deleteKPI(dbId, currentKpiId);
        if (!deleteResponse.is_success) {
            console.error("Failed to delete KPI:", deleteResponse.message);
        }

        resetDeleteKPI();
        loadKPIs();
    }

    return (
        <>
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
            <div className="p-5 table-kpis">
                <div className="row kpi-header-row">
                    <div className="col p-2 fw-bold kpi-header-col">KPI Name</div>
                    <div className="col p-2 fw-bold kpi-header-col">AKA / Also Known As</div>
                    <div className="col p-2 fw-bold kpi-header-col">Description</div>
                    <div className="col p-2 fw-bold kpi-header-col">Formula</div>
                    <div className="col p-2 fw-bold kpi-header-col">Actions</div>
                </div>
                {loadedKPIs.map((kpi) => (
                    <div className="row row-kpi-data" key={kpi.id}>
                        <div className="col border p-2 col-kpi-data">
                            {
                                isEditingKPI && currentKpiId === kpi.id ? (
                                    <input
                                        type="text"
                                        name="kpi-name"
                                        className="form-control"
                                        value={kpi.name}
                                        onChange={(e) => {
                                            const updatedKPIs = loadedKPIs.map(item => item.id === kpi.id ? { ...item, name: e.target.value } : item);
                                            setLoadedKPIs(updatedKPIs);
                                        }}
                                    />
                                ) : (
                                    <>{kpi.name}</>
                                )
                            }
                        </div>
                        <div className="col border p-2 col-kpi-data">
                            {
                                isEditingKPI && currentKpiId === kpi.id ? (
                                    <input
                                        type="text"
                                        name="kpi-aka"
                                        className="form-control"
                                        value={kpi.aka}
                                        onChange={(e) => {
                                            const updatedKPIs = loadedKPIs.map(item => item.id === kpi.id ? { ...item, aka: e.target.value } : item);
                                            setLoadedKPIs(updatedKPIs);
                                        }}
                                    />
                                ) : (
                                    <>{kpi.aka}</>
                                )
                            }
                        </div>
                        <div className="col border p-2 col-kpi-data">
                            {
                                isEditingKPI && currentKpiId === kpi.id ? (
                                    <textarea
                                        name="kpi-description"
                                        className="form-control"
                                        // value={kpi.description}
                                        onChange={(e) => {
                                            const updatedKPIs = loadedKPIs.map(item => item.id === kpi.id ? { ...item, description: e.target.value } : item);
                                            setLoadedKPIs(updatedKPIs);
                                        }}
                                    >{kpi.description}</textarea>
                                ) : (
                                    <>{kpi.description}</>
                                )
                            }
                        </div>
                        <div className="col border p-2 col-kpi-data">
                            {
                                isEditingKPI && currentKpiId === kpi.id ? (
                                    <textarea
                                        name="kpi-formula"
                                        className="form-control"
                                        // value={kpi.formula}
                                        onChange={(e) => {
                                            const updatedKPIs = loadedKPIs.map(item => item.id === kpi.id ? { ...item, formula: e.target.value } : item);
                                            setLoadedKPIs(updatedKPIs);
                                        }}
                                    >{kpi.formula}</textarea>
                                ) : (
                                    <>{kpi.formula}</>
                                )
                            }
                        </div>
                        <div className="col border p-2 col-kpi-data">
                            {isEditingKPI && currentKpiId === kpi.id ? (
                                <>
                                    <button
                                        className="btn btn-primary"
                                        name="save-kpi"
                                        onClick={handleSaveKPI}
                                    >Save</button>
                                    <button
                                        className="btn btn-secondary ms-2"
                                        name="cancel-edit-kpi"
                                        onClick={handleCancelEditKPI}
                                    >Cancel</button>
                                </>
                            ) : (
                                <>{
                                    isDeletingKPI && currentKpiId === kpi.id ? (
                                        <>
                                            <button
                                                className="btn btn-danger"
                                                name="confirm-delete-kpi"
                                                onClick={handleConfirmDeleteKPI}
                                            >Confirm Delete</button>
                                            <button
                                                className="btn btn-secondary ms-2"
                                                name="cancel-delete-kpi"
                                                onClick={resetDeleteKPI}
                                            >Cancel</button>
                                        </>
                                    ) : (<>
                                        <button
                                            className="btn bg-primary-subtle start-edit-kpi"
                                            onClick={() => { handleStartEditKPI(kpi.id || "") }}
                                        >Edit</button>
                                        <button
                                            className="btn bg-danger-subtle ms-2 start-delete-kpi"
                                            onClick={() => { handleStartDeleteKPI(kpi.id || "") }}
                                        >Delete</button>
                                    </>)
                                }</>

                            )}
                        </div>
                    </div>
                ))}
                <div className="d-flex flex-row m-2">
                    {!isEditingKPI && (
                        <button
                            className="btn bg-primary-subtle"
                            name="start-create-kpi"
                            onClick={handleStartCreateKPI}
                        >Create KPI</button>
                    )}
                </div>
            </div>
        </>
    );
}
