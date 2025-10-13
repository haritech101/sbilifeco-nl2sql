import sys
from venv import create

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text, func

# Import the necessary service(s) here
from sbin.hydrate import Hydrator, EnvVars, Defaults
from sbin.model import (
    DematerialisedBase,
    Region,
    SubChannel,
    Product,
    Policy,
    NewBusinessBudget,
    NewBusinessActual,
    RenewalPremiumBudget,
    RenewalPremiumActual,
)


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv(".env.test")

        self.conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)

        # Initialise the service(s) here
        self.hydrator = Hydrator().set_conn_string(self.conn_string)
        await self.hydrator.async_init()

        # Initialise the client(s) here

    async def asyncTearDown(self) -> None:
        engine = create_engine(self.conn_string)
        with engine.connect() as conn:
            conn.execute(text("truncate policy cascade"))
            conn.execute(text("truncate fact_nbp_budget"))
            conn.execute(text("truncate fact_rp_budget"))
            conn.commit()

        # Shutdown the service(s) here
        await self.hydrator.async_shutdown()

    async def test_hydrate_nbp_actuals(self) -> None:
        # Arrange
        await self.hydrator.hydrate_nbp_budget()

        # Act
        await self.hydrator.hydrate_nbp_actuals()

        # Assert
        engine = create_engine(self.conn_string)
        with engine.connect() as conn:
            # Check for actuals entries
            result = conn.execute(select(func.count()).select_from(NewBusinessActual))
            count = result.scalar_one()
            self.assertGreater(count, 0)

            # Check for policy entries
            result = conn.execute(select(func.count()).select_from(Policy))
            count = result.scalar_one()
            self.assertGreater(count, 0)
        engine.dispose()

    async def test_hydrate_nbp_budget(self) -> None:
        # Act
        await self.hydrator.hydrate_nbp_budget()

        # Assert
        engine = create_engine(self.conn_string)
        with engine.connect() as conn:
            result = conn.execute(select(func.count()).select_from(NewBusinessBudget))
            count = result.scalar_one()
            self.assertGreater(count, 0)
        engine.dispose()

    async def test_hydrate_rp_budget(self) -> None:
        # Act
        await self.hydrator.hydrate_rp_budget()

        # Assert
        engine = create_engine(self.conn_string)
        with engine.connect() as conn:
            result = conn.execute(
                select(func.count()).select_from(RenewalPremiumBudget)
            )
            count = result.scalar_one()
            self.assertGreater(count, 0)
        engine.dispose()

    async def test_hydrate_rp_actuals(self) -> None:
        # Arrange
        await self.hydrator.hydrate_rp_budget()

        # Act
        await self.hydrator.hydrate_rp_actuals()

        # Assert
        engine = create_engine(self.conn_string)
        with engine.connect() as conn:
            # Check for actuals entries
            result = conn.execute(
                select(func.count()).select_from(RenewalPremiumActual)
            )
            count = result.scalar_one()
            self.assertGreater(count, 0)

            # Check for policy entries
            result = conn.execute(select(func.count()).select_from(Policy))
            count = result.scalar_one()
            self.assertGreater(count, 0)
        engine.dispose()
