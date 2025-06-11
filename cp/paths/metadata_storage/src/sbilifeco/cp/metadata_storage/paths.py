class Paths:
    BASE = "/api/v1/db-metadata"

    DB = BASE + "/dbs"
    DB_BY_ID = DB + "/{db_id}"
    DB_BY_ID_WITH_FLAGS = (
        DB_BY_ID
        + "?with_tables={with_tables}&with_fields={with_fields}&with_kpis={with_kpis}"
    )

    TABLE = DB_BY_ID + "/tables"
    TABLE_BY_ID = TABLE + "/{table_id}"
    TABLE_BY_ID_WITH_FLAGS = TABLE_BY_ID + "?with_fields={with_fields}"

    FIELD = TABLE_BY_ID + "/fields"
    FIELD_BY_ID = FIELD + "/{field_id}"

    KPI = DB_BY_ID + "/kpis"
    KPI_BY_ID = KPI + "/{kpi_id}"
