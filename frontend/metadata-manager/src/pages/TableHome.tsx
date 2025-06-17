import { useEffect, useState } from "react";
import { useApi, type Field } from "../api/ApiProvider";
import { useParams } from 'react-router-dom';

export default function DBHomePage() {
    const api = useApi();
    if (!api) {
        return <div>Error: API not available</div>;
    }
    const { dbId, tableId } = useParams<{ dbId: string, tableId: string }>();
    if (!dbId || !tableId) {
        return <div>Error: Database ID or Table ID is not provided</div>;
    }

    const [loadedFields, setLoadedFields] = useState<Field[]>([]);
    const [isAddingField, setIsAddingField] = useState<boolean>(false);
    const [fieldBeingAdded, setFieldBeingAdded] = useState<Field>({
        name: "",
        type: "text",
        description: "",
        aka: "",
    });
    const [indexBeingEdited, setIndexBeingEdited] = useState<number>(-1);

    useEffect(() => { loadFields(); }, []);

    const loadFields = async () => {
        const response = await api.getFields(dbId, tableId);
        if (!response.is_success) {
            console.error("Failed to load fields:", response.message);
            return;
        }
        if (response.payload == null) {
            console.error("List of fields is inexplicably null");
            return;
        }

        setLoadedFields(response.payload);
    }

    const resetAddingField = () => {
        setIsAddingField(false);
        setFieldBeingAdded({
            name: "",
            type: "text",
            description: "",
            aka: "",
        });
    }

    const onFinishAddingField = async () => {
        const response = await api.upsertField(dbId, tableId, fieldBeingAdded);
        if (!response.is_success) {
            console.error("Failed to add field:", response.message);
            return;
        }

        resetAddingField();
        await loadFields();
    }

    const onDeleteField = async (fieldId: string) => {
        const response = await api.deleteField(dbId, tableId, fieldId);
        if (!response.is_success) {
            console.error("Failed to delete field:", response.message);
            return;
        }

        await loadFields();
    }

    const resetEditingField = () => {
        setIndexBeingEdited(-1);
    }

    const onEditField = (index: number, key: string, value: string) => {
        const updatedFields = [...loadedFields];
        updatedFields[index][key as keyof Field] = value;
        setLoadedFields(updatedFields);
    }

    const onFinishEditingField = async (index: number) => {
        const field = loadedFields[index];
        if (!field) {
            console.error("No field found at index:", index);
            return;
        }

        const response = await api.upsertField(dbId, tableId, field);
        if (!response.is_success) {
            console.error("Failed to update field:", response.message);
            return;
        }

        resetEditingField();
        await loadFields();
    }

    return (
        <>
            <div className="p-5">
                <div id="list-of-fields">
                    <div className="row p-2">
                        <div className="col-1 p-2 fw-bold">Field</div>
                        <div className="col-1 p-2 fw-bold">Type</div>
                        <div className="col-4 p-2 fw-bold">Description</div>
                        <div className="col-4 p-2 fw-bold">AKA</div>
                        <div className="col-2 p-2 fw-bold">Actions</div>
                    </div>
                    {loadedFields.map((field, index) => (
                        <div className="row row-data" key={field.id}>
                            <div className="col-1 border p-2 col-data">
                                {
                                    indexBeingEdited === index ? (
                                        <input
                                            type="text"
                                            name="field-name"
                                            className="form-control"
                                            value={field.name}
                                            onChange={(e) => { onEditField(index, "name", e.target.value) }} />
                                    ) : (
                                        <>{field.name}</>
                                    )
                                }
                            </div>
                            <div className="col-1 border p-2 col-data">
                                {
                                    indexBeingEdited === index ? (
                                        <input
                                            type="text"
                                            value={field.type}
                                            className="form-control"
                                            onChange={(e) => { onEditField(index, "type", e.target.value) }} />
                                    ) : (
                                        <>{field.type}</>
                                    )
                                }
                            </div>
                            <div className="col-4 border p-2 col-data">
                                {
                                    indexBeingEdited === index ? (
                                        <textarea
                                            className="form-control"
                                            name="field-description"
                                            onChange={(e) => { onEditField(index, "description", e.target.value) }}
                                        >{field.description}</textarea>
                                    ) : (
                                        <>{field.description}</>
                                    )
                                }
                            </div>
                            <div className="col-4 border p-2 col-data">
                                {
                                    indexBeingEdited === index ? (
                                        <input
                                            type="text"
                                            value={field.aka}
                                            className="form-control"
                                            onChange={(e) => { onEditField(index, "aka", e.target.value) }} />
                                    ) : (
                                        <>{field.aka}</>
                                    )
                                }
                            </div>
                            <div className="col-2 border p-2 d-flex gap-2">
                                {
                                    indexBeingEdited === index ? (
                                        <>
                                            <button
                                                className="btn btn-primary"
                                                name="action-finish-edit-field"
                                                onClick={async () => {
                                                    onFinishEditingField(index);
                                                }}
                                            >Save</button>
                                            <button
                                                className="btn bg-danger-subtle"
                                                onClick={() => { resetEditingField() }}
                                            >Cancel</button>
                                        </>
                                    ) : (
                                        <>
                                            <button
                                                className="btn bg-primary-subtle"
                                                name="action-start-edit-field"
                                                onClick={() => {
                                                    setIndexBeingEdited(index);
                                                }}
                                            >Edit</button>
                                            <button
                                                className="btn btn-danger"
                                                name="action-delete-field"
                                                onClick={() => onDeleteField(field.id || "")}
                                            >Delete</button>
                                        </>
                                    )
                                }
                            </div>
                        </div>
                    ))}
                </div>
                <div className="row">
                    <div className="col p-2">
                        {
                            !isAddingField ? (
                                <button className="btn bg-primary-subtle" name="action-start-add-field"
                                    onClick={() => setIsAddingField(true)}
                                >
                                    Add Field
                                </button>
                            ) : (
                                <div className="row">
                                    <div className="col p-2">
                                        <input
                                            type="text"
                                            className="form-control"
                                            name="field-name"
                                            value={fieldBeingAdded.name}
                                            onChange={(e) => {
                                                setFieldBeingAdded({
                                                    ...fieldBeingAdded,
                                                    name: e.target.value
                                                });
                                            }} />
                                    </div>
                                    <div className="col p-2">
                                        <input
                                            type="text"
                                            className="form-control"
                                            name="field-type"
                                            value={fieldBeingAdded.type}
                                            onChange={(e) => {
                                                setFieldBeingAdded({
                                                    ...fieldBeingAdded,
                                                    type: e.target.value
                                                });
                                            }} />
                                    </div>
                                    <div className="col p-2">
                                        <textarea
                                            className="form-control mt-2"
                                            name="field-description"
                                            onChange={(e) => {
                                                setFieldBeingAdded({
                                                    ...fieldBeingAdded,
                                                    description: e.target.value
                                                });
                                            }}>{fieldBeingAdded.description}</textarea>
                                    </div>
                                    <div className="col">
                                        <input
                                            type="text"
                                            className="form-control mt-2"
                                            name="field-aka"
                                            value={fieldBeingAdded.aka}
                                            onChange={(e) => {
                                                setFieldBeingAdded({
                                                    ...fieldBeingAdded,
                                                    aka: e.target.value
                                                });
                                            }} />
                                    </div>
                                    <div className="col p-2 d-flex gap-2">
                                        <button
                                            className="btn btn-primary"
                                            name="action-finish-add-field"
                                            onClick={() => onFinishAddingField()}
                                        >Save</button>
                                        <button
                                            className="btn btn-danger"
                                            name="action-cancel-add-field"
                                            onClick={() => resetAddingField()}
                                        >Cancel</button>
                                    </div>
                                </div>
                            )
                        }
                    </div>
                </div>
            </div>
        </>
    );
}