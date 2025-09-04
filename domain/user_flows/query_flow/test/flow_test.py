from random import randint
import sys

sys.path.append("./src")

from typing import AsyncGenerator
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from sbilifeco.user_flows.query_flow import QueryFlow
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.models.base import Response
from faker import Faker
from uuid import uuid4
from sbilifeco.models.db_metadata import DB


class FlowTest(IsolatedAsyncioTestCase):
    num_prompts = randint(2, 4)

    async def _generate_prompts(self) -> AsyncGenerator[str, None]:
        for prompt in self.prompts:
            yield prompt

    async def asyncSetUp(self) -> None:
        self.faker = Faker()
        self.session_id = uuid4().hex
        self.prompts = [self.faker.paragraph() for _ in range(self.num_prompts)]
        self.random_session_data = self.faker.paragraph()
        self.question = self.faker.sentence() + "?"
        self.answer = self.faker.paragraph()
        self.db_metadata = DB(
            id=uuid4().hex,
            name=self.faker.word(),
            description=self.faker.sentence(),
        )

        self.metadata_storage: IMetadataStorage = AsyncMock(spec=IMetadataStorage)
        self.llm: ILLM = AsyncMock(spec=ILLM)
        self.session_data_manager: ISessionDataManager = AsyncMock(
            spec=ISessionDataManager
        )

        self.patched_get_db = patch.object(
            self.metadata_storage,
            "get_db",
            AsyncMock(return_value=Response.ok(self.db_metadata)),
        ).start()

        self.query_flow = QueryFlow()
        (
            self.query_flow.set_metadata_storage(self.metadata_storage)
            .set_llm(self.llm)
            .set_session_data_manager(self.session_data_manager)
            .set_prompts(self._generate_prompts())
        )

        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        return await super().asyncTearDown()

    async def test_start_session(self) -> None:
        # Arrange

        # Act
        response = await self.query_flow.start_session()

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

    async def test_stop_session(self) -> None:
        # Arrange
        with patch.object(
            self.session_data_manager,
            "delete_session_data",
            AsyncMock(return_value=Response.ok(None)),
        ) as patched_delete_session_data:
            # Act
            response = await self.query_flow.stop_session(self.session_id)

            # Assert
            self.assertTrue(response.is_success, response.message)
            patched_delete_session_data.assert_any_call(
                f"{self.session_id}{QueryFlow.SUFFIX_METADATA}"
            )
            patched_delete_session_data.assert_any_call(
                f"{self.session_id}{QueryFlow.SUFFIX_LAST_QA}"
            )

    async def __test_query(self, initial_session_data: str = "") -> None:
        # Arrange
        patched_get_session_data = patch.object(
            self.session_data_manager,
            "get_session_data",
            AsyncMock(return_value=Response.ok(initial_session_data)),
        ).start()

        patched_update_session_data = patch.object(
            self.session_data_manager,
            "update_session_data",
            AsyncMock(return_value=Response.ok(None)),
        ).start()

        patched_llm_query = patch.object(
            self.llm,
            "generate_reply",
            AsyncMock(return_value=Response.ok(self.answer)),
        ).start()

        # Act
        query_response = await self.query_flow.query(
            dbId=self.db_metadata.id,
            session_id=self.session_id,
            question=self.question,
        )

        # Assert
        # Response should be successful and have a non-None payload
        self.assertTrue(query_response.is_success, query_response.message)
        assert query_response.payload is not None
        # self.assertEqual(query_response.payload, self.answer)

        # session data manager should have been queried for preamble, metadata and postamble
        patched_get_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_METADATA}"
        )

        if not initial_session_data:
            # db metadata should have been fetched from metadata storage
            self.patched_get_db.assert_called_once()
        else:
            self.patched_get_db.assert_not_called()

        # session data manager should have been queried for the last question asked and its answer
        patched_get_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_LAST_QA}"
        )

        # Data should have been sent to LLM with session data parts of it
        patched_llm_query.assert_called()

        llm_call_count = patched_llm_query.call_count

        # The first call should either build on initial session data or just use prompts and metadata
        session_data_for_llm = patched_llm_query.call_args[0][0]
        if initial_session_data:
            self.assertIn(initial_session_data, session_data_for_llm)
        else:
            self.assertIn(self.prompts[0], session_data_for_llm)
            self.assertIn(self.db_metadata.name, session_data_for_llm)
            self.assertIn(self.db_metadata.description, session_data_for_llm)
        self.assertIn(self.question, session_data_for_llm)

        self.assertEqual(llm_call_count, self.num_prompts)

        # Subsequent calls (if any) should have successive prompts
        if llm_call_count > 1:
            for i in range(1, llm_call_count):
                session_data_for_llm = patched_llm_query.call_args_list[i][0][0]
                self.assertIn(self.prompts[i], session_data_for_llm)

        # session data manager should have been called with updated session data
        self.assertEqual(2, patched_update_session_data.call_count)

        # First update should be for metadata, either existing or new
        updated_metadata = patched_update_session_data.call_args_list[0][0][1]
        if initial_session_data:
            self.assertIn(initial_session_data, updated_metadata)
        else:
            self.assertIn(self.prompts[0], updated_metadata)
            self.assertIn(self.db_metadata.name, updated_metadata)
            self.assertIn(self.db_metadata.description, updated_metadata)

        # Second update call should have been for latest question and answer
        updated_qa = patched_update_session_data.call_args_list[1][0][1]
        self.assertIn(self.question, updated_qa)
        self.assertIn(self.answer, updated_qa)

    async def test_query_new_session(self) -> None:
        await self.__test_query()

    async def test_query_continue_session(self) -> None:
        await self.__test_query(self.random_session_data)

    async def test_reset(self) -> None:
        # Arrange
        patched_delete_session_data = patch.object(
            self.session_data_manager,
            "delete_session_data",
            AsyncMock(return_value=Response.ok(None)),
        ).start()

        # Act
        response = await self.query_flow.reset_session(self.session_id)

        # Assert
        self.assertTrue(response.is_success, response.message)
        patched_delete_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_METADATA}"
        )
        patched_delete_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_LAST_QA}"
        )
