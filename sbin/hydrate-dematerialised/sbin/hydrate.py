from __future__ import annotations
from asyncio import run
from itertools import product
from dotenv import load_dotenv
from sbin.model import (
    DematerialisedBase,
    Region,
    MasterChannel,
    SubChannel,
    ProductBroadSegment,
    Product,
    Policy,
    NewBusinessActual,
    NewBusinessBudget,
)
from sqlalchemy import create_engine, Engine, Connection, select, Select, text
from sqlalchemy.orm import Session
from random import seed, choice, randint
from uuid import uuid4
from faker import Faker
from datetime import date
from os import getenv


class EnvVars:
    conn_string = "CONN_STRING"


class Defaults:
    conn_string = ""


class Hydrator:
    def __init__(self) -> None:
        self.conn_string = ""
        self.regions: list[Region] = []
        self.channels: list[SubChannel] = []
        self.products: list[Product] = []
        self.faker = Faker()

    def set_conn_string(self, conn_string: str) -> Hydrator:
        self.conn_string = conn_string
        self.engine: Engine
        self.conn: Connection
        return self

    async def async_init(self) -> None:
        self.engine = create_engine(self.conn_string)
        DematerialisedBase.metadata.create_all(self.engine)

        self.conn = self.engine.connect()

        self.regions = list(self.conn.execute(self._select_regions()).scalars().all())
        self.channels = list(self.conn.execute(self._select_channels()).scalars().all())
        self.products = list(self.conn.execute(self._select_products()).scalars().all())

    async def async_shutdown(self) -> None:
        self.conn.close()
        self.engine.dispose()

    async def run(self) -> None:
        self.set_conn_string(getenv(EnvVars.conn_string, Defaults.conn_string))

        await self.async_init()

        await self.hydrate_nbp_budget()
        await self.hydrate_nbp_actuals()

    async def hydrate_nbp_actuals(self) -> None:
        seed(42)
        with Session(self.engine) as session, session.begin():
            stmt = select(NewBusinessBudget)
            budgets = session.scalars(stmt)
            for budget in budgets:
                # Randomly decide how much of the budget to fulfill (50% to 100%)
                achievement_percent = randint(50, 100)
                months_passed = date.today().month - 4 + 1  # Since April
                achievement = (achievement_percent / 100) * (
                    months_passed / 12 * budget.nbp
                )

                # Keep creating imaginary policies until the fulfilled budget is met
                budget_fulfilled = 0
                while budget_fulfilled < achievement:
                    print(
                        f"Policy and actuals for Region: {budget.region_id}, "
                        f"Channel: {budget.sub_channel_id}, Product: {budget.product_id}, "
                        f"{budget_fulfilled} / {achievement} ({budget.rated_nbp})"
                    )
                    sum_assured = round(randint(500000, 10000000), -5)
                    premium = round(sum_assured * 0.05, -2)
                    gross_premium = premium + randint(0, 100)  # Small random gross up
                    policy = Policy(
                        productid=budget.product_id,
                        policytechnicalid=str(uuid4()),
                        policycurrentstatus=choice(["Active", "Lapsed", "Surrendered"]),
                        policysumassured=sum_assured,
                        policyannualizedpremiium=premium,
                    )
                    budget_fulfilled += premium
                    session.add(policy)

                    session.flush()  # Ensure policies get their IDs

                    # Make a new business actuals entry for the policy
                    # Random date since April 1st of this year
                    policy_date = self.faker.date_between(
                        date(2025, 4, 1), date.today()
                    )

                    nbp_actual = NewBusinessActual(
                        region_id=budget.region_id,
                        sub_channel_id=budget.sub_channel_id,
                        policy_id=policy.policytechnicalid,
                        date=policy_date,
                        nbp=premium,
                        rated_nbp=premium,  # For simplicity, assume rated_nbp = nbp
                        nbp_gross=gross_premium,  # Small random gross up
                        rated_nbp_gross=gross_premium,  # Assume rated_nbp_gross = nbp_gross
                    )
                    session.add(nbp_actual)
                    session.flush()

    async def hydrate_nbp_budget(self) -> None:
        seed(42)
        with Session(self.engine) as session, session.begin():
            for region_id in self.regions:
                for channel_id in self.channels:
                    for product_id in self.products:
                        print(
                            f"Budget for Region: {region_id}, Channel: {channel_id}, "
                            f"Product: {product_id}"
                        )

                        nbp = round(randint(10000000, 30000000), -6)
                        rated_nbp = nbp
                        nbp_gross = round(randint(nbp, nbp + 10000000), -6)
                        rated_nbp_gross = nbp_gross

                        session.add(
                            NewBusinessBudget(
                                region_id=region_id,
                                sub_channel_id=channel_id,
                                product_id=product_id,
                                current_flag=1,
                                nbp=nbp,
                                rated_nbp=rated_nbp,
                                nbp_gross=nbp_gross,
                                rated_nbp_gross=rated_nbp_gross,
                            )
                        )

    def _select_regions(self) -> Select:
        return (
            select(Region)
            .add_columns(Region.__table__.c.region_id)
            .order_by(Region.region_id)
        )

    def _select_channels(self) -> Select:
        return (
            select(SubChannel)
            .add_columns(SubChannel.__table__.c.subchannel_id)
            .order_by(SubChannel.subchannel_id)
        )

    def _select_products(self) -> Select:
        return (
            select(Product)
            .add_columns(Product.__table__.c.product_id)
            .order_by(Product.product_id)
        )


if __name__ == "__main__":
    load_dotenv()
    run(Hydrator().run())
