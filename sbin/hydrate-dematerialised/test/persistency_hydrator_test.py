from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv
from sbin.envvars import EnvVars, Defaults

# Import the necessary service(s) here
from sbin.base_hydrator import select, func, Session, create_engine
from sbin.persistency_hydrator import PersistencyHydrator
from sbin.model import RollingPersistency


class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        load_dotenv()

        conn_string = getenv(EnvVars.conn_string, Defaults.conn_string)

        # Initialise the service(s) here
        self.service = PersistencyHydrator().set_conn_string(conn_string)
        await self.service.async_init()

        # Initialise the client(s) here
        self.engine = create_engine(conn_string)

    async def asyncTearDown(self) -> None:
        # Shutdown the service(s) here
        with Session(self.engine) as session, session.begin():
            session.query(RollingPersistency).delete()
        await self.service.async_shutdown()

    async def test_hydrate(self) -> None:
        # Arrange
        ...

        # Act
        await self.service.hydrate()

        # Assert
        with Session(self.engine) as session:
            query = select(func.count()).select_from(RollingPersistency)
            result = session.execute(query).scalar_one()
            self.assertGreater(result, 0)
