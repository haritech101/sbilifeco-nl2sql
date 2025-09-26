from __future__ import annotations
from typing import Annotated, Any
from sbilifeco.boundaries.sql_db import ISqlDb
from sbilifeco.cp.common.mcp.server import MCPServer


class SqlDbMCPServer(MCPServer):
    def __init__(self):
        super().__init__()

    def set_sql_db(self, sql_db: ISqlDb) -> SqlDbMCPServer:
        self._sql_db = sql_db
        return self

    async def async_init(self) -> None:
        await super().async_init()

    def create_tools(self) -> None:
        super().create_tools()

        @self.tool(
            name="sql_executor",
            description="Executes a SQL query and returns the result",
        )
        async def execute_query(
            query: Annotated[str, "The SQL query to execute"],
        ) -> list[dict[str, Any]] | str:
            try:
                response = await self._sql_db.execute_query(query)

                if not response.is_success:
                    return f"Failed to execute query: {response.message}"
                if not response.payload:
                    return "No data returned from agent"

                return response.payload
            except Exception as e:
                return f"Error executing query: {str(e)}"
