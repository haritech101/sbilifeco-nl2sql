from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlmodel import SQLModel
from typing import Optional
import datetime


class DematerialisedBase(DeclarativeBase):
    pass


@dataclass
class Region(DematerialisedBase):
    __tablename__ = "dim_region"

    region_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    zone: Mapped[Optional[str]] = mapped_column(String(64))


@dataclass
class MasterChannel(DematerialisedBase):
    __tablename__ = "dim_master_channel"

    masterchannel_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    master_channel_name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )


@dataclass
class SubChannel(DematerialisedBase):
    __tablename__ = "dim_sub_channel"

    subchannel_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sub_channel_name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    master_channel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_master_channel.masterchannel_id"),
        nullable=False,
    )


@dataclass
class ProductBroadSegment(DematerialisedBase):
    __tablename__ = "dim_product_broad_segment"

    prod_broad_seg_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    broad_segment: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


@dataclass
class Product(DematerialisedBase):
    __tablename__ = "dim_product"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    broad_segment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_product_broad_segment.prod_broad_seg_id"),
        nullable=False,
    )
    lob: Mapped[str] = mapped_column(String(64), nullable=False)


@dataclass
class Policy(DematerialisedBase):
    __tablename__ = "policy"

    policytechnicalid: Mapped[str] = mapped_column(String(64), primary_key=True)
    policycurrentstatus: Mapped[Optional[str]] = mapped_column(String(32))
    policysumassured: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    productid: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_product.product_id"), nullable=False
    )
    policyannualizedpremium: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )


@dataclass
class NewBusinessActual(DematerialisedBase):
    __tablename__ = "fact_nbp_actual"

    nbp_actual_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nbp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rated_nbp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nbp_gross: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rated_nbp_gross: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    policy_id: Mapped[Optional[str]] = mapped_column(
        String(64), ForeignKey("policy.policytechnicalid")
    )
    sub_channel_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dim_sub_channel.subchannel_id")
    )
    region_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("dim_region.region_id")
    )
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)


@dataclass
class NewBusinessBudget(DematerialisedBase):
    __tablename__ = "fact_nbp_budget"

    nbp_budget_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nbp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rated_nbp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nbp_gross: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rated_nbp_gross: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_flag: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_product.product_id"), nullable=False
    )
    sub_channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_sub_channel.subchannel_id"), nullable=False
    )
    region_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_region.region_id"), nullable=False
    )


@dataclass
class RenewalPremiumBudget(DematerialisedBase):
    __tablename__ = "fact_rp_budget"

    rp_budget_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rp: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    current_flag: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_product.product_id"), nullable=False
    )
    sub_channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_sub_channel.subchannel_id"), nullable=False
    )
    region_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_region.region_id"), nullable=False
    )


@dataclass
class RenewalPremiumActual(DematerialisedBase):
    __tablename__ = "fact_rp_actual"

    rp_actual_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    region_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_region.region_id"), nullable=False
    )
    sub_channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dim_sub_channel.subchannel_id"), nullable=False
    )
    policytechnicalid: Mapped[str] = mapped_column(
        String(50), ForeignKey("policy.policytechnicalid"), nullable=False
    )
    rp_premium: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rp_cancellations_amount: Mapped[float] = mapped_column(
        Integer, nullable=False, default=0
    )
    rp_gross: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rp_service_tax: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rp_entry_fee: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rated_rp: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rated_rp_gross: Mapped[float] = mapped_column(Integer, nullable=False, default=0)
    rated_rp_service_tax: Mapped[float] = mapped_column(
        Integer, nullable=False, default=0
    )
    rated_rp_entry_fee: Mapped[float] = mapped_column(
        Integer, nullable=False, default=0
    )


@dataclass
class NewBusinessRefund(DematerialisedBase):
    __tablename__ = "nb_refund_aotg"

    as_on_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    branch: Mapped[str] = mapped_column(String(32), nullable=False)
    broad_segment: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, primary_key=True)
    lob: Mapped[str] = mapped_column(String(32), nullable=False)
    product: Mapped[str] = mapped_column(String(32), nullable=False, primary_key=True)
    region: Mapped[str] = mapped_column(String(32), nullable=False, primary_key=True)
    zone: Mapped[str] = mapped_column(String(32), nullable=False)
    month: Mapped[str] = mapped_column(String(6), nullable=False, primary_key=True)
    mtd_refund_amt: Mapped[float] = mapped_column(Integer, nullable=False)
