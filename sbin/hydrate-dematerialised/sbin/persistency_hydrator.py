from __future__ import annotations
from datetime import timedelta
from typing import Sequence
from sbin.base_hydrator import BaseHydrator, run, Session, date, randint, seed
from sbin.model import (
    Product,
    ProductBroadSegment,
    RollingPersistency,
    SubChannel,
    Region,
)


class PersistencyHydrator(BaseHydrator):
    def __init__(self) -> None:
        super().__init__()
        self.conn_string = ""
        self.products: Sequence[Product] = []
        self.sub_channels: Sequence[SubChannel] = []
        self.regions: Sequence[Region] = []
        self.segments: dict[int, str] = {}

    async def async_init(self) -> None:
        await super().async_init()
        with Session(self.engine) as session:
            self.products = session.query(Product).all()
            self.sub_channels = session.query(SubChannel).all()
            self.regions = session.query(Region).all()
            self.segments = {
                segment.prod_broad_seg_id: segment.broad_segment
                for segment in session.query(ProductBroadSegment).all()
            }

    async def hydrate(self) -> None:
        seed(42)
        record_num = 1
        with Session(self.engine) as session, session.begin():
            for region in self.regions:
                for sub_channel in self.sub_channels:
                    for product in self.products:
                        persistency_anchor = randint(60, 95)
                        one_year_collectable = round(randint(50000000, 200000000), -5)

                        year = 2025
                        month = 2
                        day = date(year, month, 1) - timedelta(days=1)
                        while day < date.today():
                            for num_years in range(1, 6):
                                period = f"{num_years * 12 + 1}M"

                                formatted_month = day.strftime("%b-%y").upper()

                                collectable_variance = randint(-5, 5)
                                collectable_over_period = round(
                                    (
                                        (num_years * one_year_collectable)
                                        + collectable_variance
                                        / 100
                                        * one_year_collectable
                                    ),
                                    -5,
                                )

                                persistency_variance = randint(-5, 5)
                                persistency_percentage = (
                                    persistency_anchor + persistency_variance
                                )
                                collected_over_period = round(
                                    collectable_over_period
                                    * persistency_percentage
                                    / 100,
                                    -5,
                                )

                                collection_stats = RollingPersistency(
                                    region=region.region,
                                    channel=sub_channel.sub_channel_name,
                                    product=product.product_name,
                                    as_on_date=date.today(),
                                    branch="N/A",
                                    broad_segment=self.segments.get(
                                        product.broad_segment_id, "N/A"
                                    ),
                                    lob=product.lob,
                                    zone=region.zone or "N/A",
                                    month=formatted_month,
                                    period=period,
                                    cy_collectable=collectable_over_period,
                                    cy_collected=collected_over_period,
                                )

                                print(f"Preparing record number {record_num}...")
                                print(
                                    f"{region.region}, "
                                    f"{sub_channel.sub_channel_name}, "
                                    f"{product.product_name}, "
                                    f"{formatted_month}, "
                                    f"{period}, "
                                    f"{collectable_over_period}, "
                                    f"{collected_over_period}"
                                )
                                session.add(collection_stats)
                                record_num += 1

                            month += 1
                            if month > 12:
                                month = 1
                                year += 1
                            day = date(year, month, 1) - timedelta(days=1)


if __name__ == "__main__":
    run(PersistencyHydrator().run_as_tool())
