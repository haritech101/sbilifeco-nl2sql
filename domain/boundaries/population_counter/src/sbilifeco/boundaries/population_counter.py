from datetime import date, datetime
from sbilifeco.models.base import Response


class IPopulationCounter:
    async def count_by_named_division(
        self, key: str, matching_division: str
    ) -> Response[int]: ...
    async def count_by_numeric_range(
        self,
        key: str,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> Response[int]: ...
    async def count_by_date_range(
        self,
        key: str,
        start_date: date | datetime | None = None,
        end_date: date | datetime | None = None,
    ) -> Response[int]: ...
    async def count_by_boolean(
        self, key: str, true_or_false: bool
    ) -> Response[int]: ...
