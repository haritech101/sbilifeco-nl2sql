import sys
from pprint import pformat
from random import randint

sys.path.append("./src")

from json import dumps
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from faker import Faker
from sbilifeco.boundaries.llm import ILLM
from sbilifeco.boundaries.metadata_storage import IMetadataStorage
from sbilifeco.boundaries.session_data_manager import ISessionDataManager
from sbilifeco.models.base import Response
from sbilifeco.models.db_metadata import DB

from sbilifeco.user_flows.query_flow import QueryFlow


class FlowTest(IsolatedAsyncioTestCase):
    num_prompts = randint(2, 4)

    async def asyncSetUp(self) -> None:
        self.faker = Faker()
        self.session_id = uuid4().hex
        self.prompt = "\n\n".join(
            [
                self.faker.paragraph(),
                f"{{{QueryFlow.PLACEHOLDER_METADATA}}}",
                self.faker.paragraph(),
                f"{{{QueryFlow.PLACEHOLDER_LAST_QA}}}",
                self.faker.paragraph(),
                f"{{{QueryFlow.PLACEHOLDER_QUESTION}}}",
                self.faker.paragraph(),
                f"{{{QueryFlow.PLACEHOLDER_MASTER_VALUES}}}",
                self.faker.paragraph(),
                f"{{{QueryFlow.PLACEHOLDER_THIS_MONTH}}}",
                self.faker.paragraph(),
            ]
        )
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

        self.fn_get_db = patch.object(
            self.metadata_storage,
            "get_db",
            AsyncMock(return_value=Response.ok(self.db_metadata)),
        ).start()

        self.query_flow = QueryFlow()
        (
            self.query_flow.set_metadata_storage(self.metadata_storage)
            .set_llm(self.llm)
            .set_session_data_manager(self.session_data_manager)
            .set_prompt(self.prompt)
        )

        return await super().asyncSetUp()

    async def asyncTearDown(self) -> None:
        patch.stopall()
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
        fn_get_session_data = patch.object(
            self.session_data_manager,
            "get_session_data",
            AsyncMock(return_value=Response.ok(initial_session_data)),
        ).start()

        fn_update_session_data = patch.object(
            self.session_data_manager,
            "update_session_data",
            AsyncMock(return_value=Response.ok(None)),
        ).start()

        fn_llm_query = patch.object(
            self.llm,
            "generate_reply",
            AsyncMock(return_value=Response.ok(self.answer)),
        ).start()

        # Act
        flow_response = await self.query_flow.query(
            dbId=self.db_metadata.id,
            session_id=self.session_id,
            question=self.question,
            with_thoughts=False,
        )

        # Assert
        # Response should be successful and the payload should be LLM's answer
        self.assertTrue(flow_response.is_success, flow_response.message)
        assert flow_response.payload is not None
        self.assertEqual(flow_response.payload, self.answer)

        # session data manager should have been queried for DB metadata
        fn_get_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_METADATA}"
        )

        # session data manager should have been queried for master values
        fn_get_session_data.assert_any_call(
            f"{self.db_metadata.id}{QueryFlow.SUFFIX_MASTER_VALUES}"
        )

        if not initial_session_data:
            # No cached db metadata in session data,
            # db metadata should have been fetched from metadata storage
            self.fn_get_db.assert_called_once()
        else:
            # Cached db metadata exists in session data,
            # db metadata should NOT have been fetched from metadata storage
            self.fn_get_db.assert_not_called()

        # session data manager should have been queried for the last question asked and its answer
        fn_get_session_data.assert_any_call(
            f"{self.session_id}{QueryFlow.SUFFIX_LAST_QA}"
        )

        # LLM should have been invoked
        fn_llm_query.assert_called_once()

        # Contents of the prompt sent to LLM
        context_sent_to_llm = fn_llm_query.call_args[0][0]

        self.assertIn(self.prompt[:10], context_sent_to_llm)
        if initial_session_data:
            # Cached db metadata, so that should be sent as part of LLM context
            self.assertIn(initial_session_data, context_sent_to_llm)
        else:
            # Fresh db metadata fetched from metadata storage, so that should be sent as part of LLM context
            self.assertIn(self.db_metadata.name, context_sent_to_llm)
            self.assertIn(self.db_metadata.description, context_sent_to_llm)

        # The latest question should be in the context sent to LLM
        self.assertIn(self.question, context_sent_to_llm)

        # The context data shouldn't have placeholder strings
        # Everything should have been replaced with actual data
        self.assertNotIn(
            "{" + QueryFlow.PLACEHOLDER_METADATA + "}", context_sent_to_llm
        )
        self.assertNotIn("{" + QueryFlow.PLACEHOLDER_LAST_QA + "}", context_sent_to_llm)
        self.assertNotIn(
            "{" + QueryFlow.PLACEHOLDER_QUESTION + "}", context_sent_to_llm
        )
        self.assertNotIn(
            "{" + QueryFlow.PLACEHOLDER_MASTER_VALUES + "}", context_sent_to_llm
        )
        self.assertNotIn(
            "{" + QueryFlow.PLACEHOLDER_THIS_MONTH + "}", context_sent_to_llm
        )

        # There should be at least one call made to update session data manager
        self.assertGreaterEqual(
            fn_update_session_data.call_count, 1, "No session data update calls made"
        )

        # Post query operations
        # Fetch the calls made to update session data
        session_data_update_calls = fn_update_session_data.call_args_list

        if not initial_session_data:
            # No cached db metadata, so that will be updated in session data manager
            update_db_metadata_call = session_data_update_calls.pop(0)
            key, db_metadata = update_db_metadata_call.args

            self.assertEqual(key, f"{self.session_id}{QueryFlow.SUFFIX_METADATA}")
            self.assertIn(self.db_metadata.name, db_metadata)
            self.assertIn(self.db_metadata.description, db_metadata)

        # There should be an update call for last question and answer
        update_last_qa_call = session_data_update_calls.pop(0)
        key, updated_qa = update_last_qa_call.args
        self.assertEqual(key, f"{self.session_id}{QueryFlow.SUFFIX_LAST_QA}")
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

    async def test_master_values_retrieval(self) -> None:
        # Arrange
        session_id = uuid4().hex
        question = self.faker.sentence() + "?"
        master_dimension = self.faker.word()
        master_values = [self.faker.word() for _ in range(10)]
        cache = dumps({master_dimension: ",".join(master_values)})
        pretty_cache = pformat({master_dimension: ",".join(master_values)}, indent=2)

        patched_get_master_values = patch.object(
            self.session_data_manager,
            "get_session_data",
            AsyncMock(
                side_effect=lambda key: (
                    Response.ok(cache)
                    if key == f"{self.db_metadata.id}{QueryFlow.SUFFIX_MASTER_VALUES}"
                    else Response.ok("")
                )
            ),
        ).start()

        patched_llm_query = patch.object(
            self.llm,
            "generate_reply",
            AsyncMock(side_effect=[Response.ok(self.faker.paragraph())]),
        ).start()

        # Act
        response = await self.query_flow.query(
            dbId=self.db_metadata.id,
            session_id=session_id,
            question=question,
        )

        # Assert
        self.assertTrue(response.is_success, response.message)
        assert response.payload is not None

        patched_get_master_values.assert_any_call(
            f"{self.db_metadata.id}{QueryFlow.SUFFIX_MASTER_VALUES}"
        )

        (context,) = patched_llm_query.call_args.args
        self.assertIn(pretty_cache, context)
