from __future__ import annotations
from random import randint
from typing import Sequence
from sbin.base_hydrator import BaseHydrator, run, Session, date, randint
from sbin.model import (
    NewBusinessRefund,
    Product,
    ProductBroadSegment,
    SubChannel,
    Region,
)


class RefundHydrator(BaseHydrator):
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
        record_num = 1
        for region in self.regions:
            for sub_channel in self.sub_channels:
                for product in self.products:
                    for i in range(5, 50):
                        day = self.faker.date_between_dates(
                            date_start=date(2023, 1, 1), date_end=date.today()
                        )
                        formatted_month = day.strftime("%b-%y").upper()

                        refund = round(randint(20000, 200000), -3)

                        with Session(self.engine) as session, session.begin():
                            refund = NewBusinessRefund(
                                region=region.region,
                                channel=sub_channel.sub_channel_name,
                                product=product.product_name,
                                mtd_refund_amt=refund,
                                as_on_date=date.today(),
                                branch="N/A",
                                broad_segment=self.segments.get(
                                    product.broad_segment_id, "N/A"
                                ),
                                lob=product.lob,
                                zone=region.zone or "N/A",
                                month=formatted_month,
                            )

                            print(f"Preparing record number {record_num}...")
                            print(
                                f"{region.region}, "
                                f"{sub_channel.sub_channel_name}, "
                                f"{product.product_name}, "
                                f"{formatted_month}, "
                                f"Refund #{i}: "
                                f"{refund}"
                            )
                            session.add(refund)
                            record_num += 1


if __name__ == "__main__":
    run(RefundHydrator().run_as_tool())
