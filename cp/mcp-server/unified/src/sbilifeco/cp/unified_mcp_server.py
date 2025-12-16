from __future__ import annotations
from typing import Optional, Annotated
from pprint import pprint, pformat
from datetime import date, datetime
from sbilifeco.cp.common.mcp.server import MCPServer
from sbilifeco.boundaries.population_counter import IPopulationCounter


class UnifiedMCPServer(MCPServer):
    def __init__(self) -> None:
        super().__init__()
        self.set_server_name("SBILifeCo Unified MCP Server")
        self.population_counter: IPopulationCounter

    def set_population_counter(
        self, population_counter: IPopulationCounter
    ) -> UnifiedMCPServer:
        self.population_counter = population_counter
        return self

    def create_tools(self):
        @self.tool(
            name="count_by_named_division",
            description="""
            Return the number of items that are classified under a particular value among a set of possible values for the given key
            Returns a dict
            The first item is is_success
            Based on the success, the second item is either "count" or "error"
            """,
        )
        async def count_by_named_division(
            key: Annotated[
                str,
                "The key which has the set of possible values, also called divisions.",
            ],
            division_name: Annotated[
                str,
                "The name of the division for which we are counting the number of items.",
            ],
        ) -> dict:
            try:
                count_response = await self.population_counter.count_by_named_division(
                    key, division_name
                )
                if not count_response.is_success:
                    return {
                        "is_success": False,
                        "error": count_response.message,
                    }

                return {
                    "is_success": True,
                    "count": (
                        0 if count_response.payload is None else count_response.payload
                    ),
                }

            except Exception as ex:
                return {"is_success": False, "error": pformat(ex)}

        @self.tool(
            name="count_by_numeric_range",
            description="""
            Return the number of items that have a numeric value within a specified range for the given key
            Returns a dict
            The first item is is_success
            Based on the success, the second item is either "count" or "error"
            """,
        )
        async def count_by_numeric_range(
            key: Annotated[
                str,
                "The key which has numeric values.",
            ],
            min_value: Optional[
                Annotated[int, "The minimum value of the range."]
            ] = None,
            max_value: Optional[
                Annotated[int, "The maximum value of the range."]
            ] = None,
        ) -> dict:
            try:
                count_response = await self.population_counter.count_by_numeric_range(
                    key, min_value, max_value
                )
                if not count_response.is_success:
                    return {
                        "is_success": False,
                        "error": count_response.message,
                    }

                return {
                    "is_success": True,
                    "count": (
                        0 if count_response.payload is None else count_response.payload
                    ),
                }

            except Exception as ex:
                return {"is_success": False, "error": pformat(ex)}

        @self.tool(
            name="count_by_date_range",
            description="""
            Return the number of items that have a date value within a specified range for the given key
            Returns a dict
            The first item is is_success
            Based on the success, the second item is either "count" or "error"
            """,
        )
        async def count_by_date_range(
            key: Annotated[
                str,
                "The key which has date values.",
            ],
            start_date: Optional[
                Annotated[
                    date | datetime,
                    "The start date of the range in ISO format.",
                ]
            ] = None,
            end_date: Optional[
                Annotated[
                    date | datetime,
                    "The end date of the range in ISO format.",
                ]
            ] = None,
        ) -> dict:
            try:

                count_response = await self.population_counter.count_by_date_range(
                    key, start_date, end_date
                )
                if not count_response.is_success:
                    return {
                        "is_success": False,
                        "error": count_response.message,
                    }

                return {
                    "is_success": True,
                    "count": (
                        0 if count_response.payload is None else count_response.payload
                    ),
                }

            except Exception as ex:
                return {"is_success": False, "error": pformat(ex)}

        @self.tool(
            name="count_by_boolean",
            description="""
            Return the number of items that have a boolean value (true or false) for the given key
            Returns a dict
            The first item is is_success
            Based on the success, the second item is either "count" or "error"
            """,
        )
        async def count_by_boolean(
            key: Annotated[
                str,
                "The key which has boolean values.",
            ],
            true_or_false: Annotated[
                bool,
                "The boolean value to count (true or false).",
            ],
        ) -> dict:
            try:
                count_response = await self.population_counter.count_by_boolean(
                    key, true_or_false
                )
                if not count_response.is_success:
                    return {
                        "is_success": False,
                        "error": count_response.message,
                    }

                return {
                    "is_success": True,
                    "count": (
                        0 if count_response.payload is None else count_response.payload
                    ),
                }

            except Exception as ex:
                return {"is_success": False, "error": pformat(ex)}
