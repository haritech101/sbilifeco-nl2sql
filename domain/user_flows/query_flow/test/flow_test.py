from ast import Is
import sys

sys.path.append("./src")

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.session_data_manager import ISessionDataManager


class FlowTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.metadata_storage: IMetadataStorage = AsyncMock(spec=IMetadataStorage)
        self.llm: ILLM = AsyncMock(spec=ILLM)
        self.session_data_manager: ISessionDataManager = AsyncMock(
            spec=ISessionDataManager
        )

        self.query_flow = QueryFlow()

        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_query(self) -> None:
        # Arrange
        # Act
        # Assert
        pass

    async def test_reset(self) -> None:
        # Arrange
        # Act
        # Assert
        pass
