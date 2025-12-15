from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from urllib.parse import urlencode
from pydantic import BaseModel
from sbilifeco.models.base import Response

# Import other required contracts/modules here
from sbilifeco.boundaries.population_counter import IPopulationCounter
from sbilifeco.cp.common.http.client import HttpClient, Request
from sbilifeco.cp.population_counter.paths import Paths


class PopulationCounterHttpClient(HttpClient, IPopulationCounter):
    def __init__(self):
        HttpClient.__init__(self)

    async def count_by_named_division(
        self, key: str, matching_division: str
    ) -> Response[int]:
        try:
            # Form request
            pairs = {"key": key, "matching_division": matching_division}

            # Return response
            return await self._search_by_pairs(pairs)
        except Exception as e:
            return Response.error(e)

    async def count_by_numeric_range(
        self, key: str, min_value: int | None = None, max_value: int | None = None
    ) -> Response[int]:
        try:
            # Form request
            pairs = {"key": key}
            if min_value is not None:
                pairs["min_value"] = str(min_value)
            if max_value is not None:
                pairs["max_value"] = str(max_value)

            # Return response
            return await self._search_by_pairs(pairs)
        except Exception as e:
            return Response.error(e)

    async def count_by_date_range(
        self,
        key: str,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> Response[int]:
        try:
            # Form request
            pairs = {"key": key}
            if start_date is not None:
                pairs["start_date"] = start_date.isoformat()
            if end_date is not None:
                pairs["end_date"] = end_date.isoformat()

            # Return response
            return await self._search_by_pairs(pairs)
        except Exception as e:
            return Response.error(e)

    async def count_by_boolean(self, key: str, true_or_false: bool) -> Response[int]:
        try:
            # Form request
            pairs = {"key": key, "true_or_false": str(true_or_false)}

            # Return response
            return await self._search_by_pairs(pairs)
        except Exception as e:
            return Response.error(e)

    async def _search_by_pairs(self, pairs: dict[str, str]) -> Response[int]:
        search_query = urlencode(pairs)
        # Form request
        url = f"{self.url_base}{Paths.SEARCH}?{search_query}"
        req = Request(url=url, method="GET")

        # Send request
        res = await self.request_as_model(req)

        # Triage response
        ...

        # Return response
        return res
