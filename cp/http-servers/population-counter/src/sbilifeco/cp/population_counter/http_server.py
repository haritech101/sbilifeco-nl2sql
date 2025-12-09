from __future__ import annotations
from typing import Optional, Annotated
from pydantic import BaseModel
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from fastapi import Query
from datetime import date, datetime
from sbilifeco.boundaries.population_counter import IPopulationCounter
from sbilifeco.cp.common.http.server import HttpServer
from sbilifeco.cp.population_counter.paths import Paths


class PopulationCounterHttpServer(HttpServer):
    def __init__(self):
        super().__init__()
        self.population_counter: IPopulationCounter

    def set_population_counter(
        self, population_counter: IPopulationCounter
    ) -> PopulationCounterHttpServer:
        self.population_counter = population_counter
        return self

    def build_routes(self) -> None:
        super().build_routes()

        @self.get(Paths.SEARCH)
        async def count_by_params(
            key: Annotated[str, Query()],
            matching_division: Annotated[Optional[str], Query()] = None,
            min_value: Annotated[Optional[int], Query()] = None,
            max_value: Annotated[Optional[int], Query()] = None,
            start_date: Annotated[Optional[date | datetime], Query()] = None,
            end_date: Annotated[Optional[date | datetime], Query()] = None,
            true_or_false: Annotated[Optional[bool], Query()] = None,
        ) -> Response[int]:
            try:
                # Validate request
                if (
                    matching_division is None
                    and min_value is None
                    and max_value is None
                    and start_date is None
                    and end_date is None
                    and true_or_false is None
                ):
                    return Response.fail(
                        "At least one filtering parameter must be provided.", 400
                    )

                # Triage request
                ...

                # Gateway call
                res: Response[int] | None = None

                if matching_division is not None:
                    res = await self.population_counter.count_by_named_division(
                        key, matching_division
                    )
                elif min_value is not None or max_value is not None:
                    res = await self.population_counter.count_by_numeric_range(
                        key, min_value, max_value
                    )
                elif start_date is not None or end_date is not None:
                    res = await self.population_counter.count_by_date_range(
                        key, start_date, end_date
                    )
                elif true_or_false is not None:
                    res = await self.population_counter.count_by_boolean(
                        key, true_or_false
                    )

                if res is None:
                    return Response.fail("No valid filtering parameter provided.", 400)

                # Triage response
                ...

                # Return response
                return res
            except Exception as e:
                return Response.error(e)
