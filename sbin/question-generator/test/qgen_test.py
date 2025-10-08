import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from pprint import pprint
from sbin.envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbin.qgen import (
    QGen,
    QGenRequest,
    QGenMetric,
    QGenRegion,
    QGenProduct,
    QGenTimeframe,
)


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".env.test")

        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)
        llm_proto = getenv(EnvVars.llm_proto, Defaults.llm_proto)
        llm_host = getenv(EnvVars.llm_host, Defaults.llm_host)
        llm_port = int(getenv(EnvVars.llm_port, Defaults.llm_port))

        # Initialise the service(s) here
        self.service = (
            QGen()
            .set_conn_string(conn_string)
            .set_llm_scheme(llm_proto, llm_host, llm_port)
        )
        await self.service.async_init()

        # Initialise the client(s) here
        ...

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        await self.service.async_shutdown()
        ...

    async def test_generate_rated_nbp_mtd(self) -> None:
        # Arrange
        request = QGenRequest(metric=QGenMetric(focus="nbp", index=0))

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert isinstance(result[0], list)
        self.assertIn("New Business Premium", result[0])

    async def test_generate_rp_from_specific_region(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="rp", index=0),
            region=QGenRegion(focus="region", index=0),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        # Verify the tuple has the expected length
        assert len(result) == 2

        assert isinstance(result[0], list)
        self.assertIn("Renewal Premium", result[0])

        # Verify that a specific region is returned at index 1
        assert result[1] == self.service.regions[0]

    async def test_generate_persistency_from_specific_zone(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="persistency", index=0),
            region=QGenRegion(focus="zone", index=0),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        # Verify the tuple has the expected length
        assert len(result) == 2

        assert isinstance(result[0], list)
        self.assertIn("Persistency", result[0])

        # Verify that a specific zone is returned at index 1
        assert result[1] == self.service.zones[0]

    async def test_generate_refund_from_specific_channel(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="refund", index=0), channel_index=0
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        # Verify the tuple has the expected length
        assert len(result) == 2

        assert isinstance(result[0], list)
        self.assertIn("New Business Refund", result[0])

        # Verify that a specific channel is returned at index 1
        assert result[1] == self.service.sub_channels[0]

    async def test_generate_nbp_from_specific_product(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="nbp", index=0),
            product=QGenProduct(focus="product", index=0),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("New Business Premium", result[0])
        assert result[1] == self.service.products[0]

    async def test_generate_rp_from_specific_segment(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="rp", index=0),
            product=QGenProduct(focus="segment", index=0),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("Renewal Premium", result[0])
        assert result[1] == self.service.broad_segments[0]

    async def test_generate_persistency_from_specific_lob(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="persistency", index=0),
            product=QGenProduct(focus="lob", index=0),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("Persistency", result[0])
        assert result[1] == self.service.lobs[0]

    async def test_generate_refund_from_region_and_channel(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="refund", index=0),
            region=QGenRegion(focus="region", index=0),
            channel_index=0,
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 3
        assert isinstance(result[0], list)
        self.assertIn("New Business Refund", result[0])
        assert self.service.regions[0] in result
        assert self.service.sub_channels[0] in result

    async def test_generate_nbp_ytd(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="nbp", index=0),
            temporal=QGenTimeframe(focus="year", is_to_date=True),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("New Business Premium", result[0])
        # Assert temporal output
        assert result[1] == "YTD"

    async def test_generate_rp_march_2025(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="rp", index=0),
            temporal=QGenTimeframe(focus="month", is_to_date=False, month=3, year=2025),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("Renewal Premium", result[0])
        # Assert temporal output
        assert result[1] == "March 2025"

    async def test_generate_persistency_q3_2024(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="persistency", index=0),
            temporal=QGenTimeframe(
                focus="quarter", is_to_date=False, quarter_number=3, year=2024
            ),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("Persistency", result[0])
        # Assert temporal output
        assert result[1] == "Q3 2024"

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("Persistency", result[0])

    async def test_generate_refund_2023(self) -> None:
        # Arrange
        request = QGenRequest(
            metric=QGenMetric(focus="refund", index=0),
            temporal=QGenTimeframe(focus="year", is_to_date=False, year=2023),
        )

        # Act
        result = await self.service.generate_one(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        assert len(result) == 2
        assert isinstance(result[0], list)
        self.assertIn("New Business Refund", result[0])
        # Assert temporal output
        assert result[1] == "2023"

    async def test_generate_one_line(self) -> None:
        # Arrange - Test with all possible dimensions using randomization
        request = QGenRequest(
            metric=QGenMetric(focus="nbp", index=-1),
            temporal=QGenTimeframe(focus="month", is_to_date=False, month=3, year=2025),
            region=QGenRegion(focus="region", index=-1),
            product=QGenProduct(focus="product", index=-1),
            channel_index=-1,
        )

        # Act
        result = await self.service.generate_one_line(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        # Should contain one of the metric words from any NBP category
        self.assertRegex(result, r"New Business Premium|NBP|Rated NBP|Actual NBP")
        # Should contain the temporal component with "during"
        self.assertIn("during March 2025", result)
        # Should contain a region from the available regions
        self.assertIn(True, (region in result for region in self.service.regions))
        # Should contain a product from the available products
        self.assertIn(True, (product in result for product in self.service.products))
        # Should contain a channel from the available sub_channels
        self.assertIn(
            True, (channel in result for channel in self.service.sub_channels)
        )
        # Should start with one of the imperatives
        self.assertRegex(result, r"^(Show me|Give me|What is|I need|How much)")

        # Test MTD/YTD behavior (no preposition)
        mtd_request = QGenRequest(
            metric=QGenMetric(focus="nbp", index=-1),
            temporal=QGenTimeframe(focus="month", is_to_date=True),
        )

        mtd_result = await self.service.generate_one_line(mtd_request)

        # MTD should not have "during" preposition
        self.assertRegex(mtd_result, r"\bMTD\b")
        self.assertNotIn("during MTD", mtd_result)

    async def test_generate_one_line_mtd(self) -> None:
        # Arrange - Test MTD with multiple dimensions
        request = QGenRequest(
            metric=QGenMetric(focus="rp", index=-1),
            temporal=QGenTimeframe(focus="month", is_to_date=True),
            region=QGenRegion(focus="zone", index=-1),
            product=QGenProduct(focus="segment", index=-1),
        )

        # Act
        result = await self.service.generate_one_line(request)

        # Debug: Pretty print the result
        pprint(result)

        # Assert
        # Should contain one of the RP metric words
        self.assertRegex(result, r"Renewal Premium|RP|Rated RP|Actual RP|IRP")
        # Should contain MTD without "during" preposition
        self.assertRegex(result, r"\bMTD\b")
        self.assertNotIn("during MTD", result)
        # Should contain a zone from the available zones
        self.assertIn(
            True, (zone in result for zone in self.service.zones if zone is not None)
        )
        # Should contain a segment from the available broad_segments
        self.assertIn(
            True, (segment in result for segment in self.service.broad_segments)
        )
        # Should start with one of the imperatives
        self.assertRegex(result, r"^(Show me|Give me|What is|I need|How much)")
        # Should use "for" with non-temporal dimensions
        self.assertRegex(result, r"MTD for")

    async def test_generate_many_lines(self) -> None:
        # Arrange
        num_tests = 10
        possible_metrics = [
            metric
            for metric in [
                submetrics for submetrics in self.service.available_metrics.values()
            ]
        ]

        # Act
        results = await self.service.generate_many_lines(num_tests)

        # Debug: Pretty print the results
        pprint(results)

        # Assert
        self.assertEqual(len(results), num_tests)

    async def test_generate_with_llm(self) -> None:
        # Arrange
        num_tests = -1

        # Act
        result = await self.service.generate_with_llm(num_tests)

        # Assert
        print(result)
        assert result is not None
