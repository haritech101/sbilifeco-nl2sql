from __future__ import annotations
from calendar import month_name
from random import choice, randint
from typing import Literal, Sequence, Tuple
from pydantic import BaseModel
from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import Session
from .model import Region, MasterChannel, SubChannel, ProductBroadSegment, Product
from asyncio import run
from argparse import ArgumentParser
from dotenv import load_dotenv
from os import getenv
from sbin.envvars import EnvVars, Defaults
from sys import argv
from sbilifeco.cp.llm.http_client import LLMHttpClient


class QGenRegion(BaseModel):
    focus: Literal["zone"] | Literal["region"] = "region"
    index: int | Sequence[int] = -1


class QGenProduct(BaseModel):
    focus: Literal["product"] | Literal["segment"] | Literal["lob"] = "product"
    index: int | Sequence[int] = -1


class QGenTimeframe(BaseModel):
    focus: Literal["month"] | Literal["quarter"] | Literal["year"] = "month"
    is_to_date: bool = True
    quarter_number: int | None = None
    year: int | None = None
    month: int | None = None


class QGenMetric(BaseModel):
    focus: Literal["nbp"] | Literal["rp"] | Literal["refund"] | Literal["persistency"]
    index: int | Sequence[int] = -1


class QGenRequest(BaseModel):
    metric: QGenMetric
    region: None | QGenRegion = None
    product: None | QGenProduct = None
    channel_index: None | int | Sequence[int] = None
    temporal: None | QGenTimeframe = None


class QGen:
    default_num_tests = 100
    available_metrics: dict[str, list[list[str]]] = {
        "nbp": [["New Business Premium", "NBP", "Rated NBP"], ["Actual NBP"]],
        "rp": [
            ["Renewal Premium", "RP", "Rated RP", "IRP"],
            ["Actual RP", "Actual Renewal Premium"],
        ],
        "refund": [["New Business Refund", "Refund", "NB refund"]],
        "persistency": [
            ["Persistency", "Rolling Persistency"],
            ["Collectable", "Collectable amount"],
            ["Collected", "Collected amount"],
        ],
    }

    imperatives: list[str] = ["Show me", "Give me", "What is the", "I need", "How much"]

    def __init__(self):
        self.conn_string = ""
        self.engine: Engine
        # Initialize dimension data containers
        self.regions: list[str] = []
        self.zones: list[str | None] = []
        self.master_channels: list[str] = []
        self.sub_channels: list[str] = []
        self.broad_segments: list[str] = []
        self.products: list[str] = []
        self.lobs: list[str] = []
        self.llm_client: LLMHttpClient
        self.llm_proto: str
        self.llm_host: str
        self.llm_port: int

    def set_conn_string(self, conn_string: str) -> QGen:
        self.conn_string = conn_string
        return self

    def set_llm_scheme(self, proto: str, host: str, port: int) -> QGen:
        self.llm_proto = proto
        self.llm_host = host
        self.llm_port = port
        return self

    async def async_init(self):
        self.engine = create_engine(self.conn_string)

        # Get the list of values for the dimension models from models.py
        with Session(self.engine) as session:
            # Get all regions
            self.regions = list(
                session.scalars(select(Region.region).order_by(Region.region))
            )

            # Get all zones (distinct, excluding None values)
            self.zones = list(
                session.scalars(
                    select(Region.zone)
                    .distinct()
                    .where(Region.zone.is_not(None))
                    .order_by(Region.zone)
                )
            )

            # Get all master channels
            self.master_channels = list(
                session.scalars(
                    select(MasterChannel.master_channel_name).order_by(
                        MasterChannel.master_channel_name
                    )
                )
            )

            # Get all sub channels
            self.sub_channels = list(
                session.scalars(
                    select(SubChannel.sub_channel_name).order_by(
                        SubChannel.sub_channel_name
                    )
                )
            )

            # Get all product broad segments
            self.broad_segments = list(
                session.scalars(
                    select(ProductBroadSegment.broad_segment).order_by(
                        ProductBroadSegment.broad_segment
                    )
                )
            )

            # Get all products
            self.products = list(
                session.scalars(
                    select(Product.product_name).order_by(Product.product_name)
                )
            )

            # Get all LOBs
            self.lobs = list(
                session.scalars(select(Product.lob).distinct().order_by(Product.lob))
            )

        self.llm_client = LLMHttpClient()
        (
            self.llm_client.set_proto(self.llm_proto)
            .set_host(self.llm_host)
            .set_port(self.llm_port)
        )

    async def async_shutdown(self) -> None:
        self.engine.dispose()

    async def generate_with_llm(self, num_questions: int) -> str:
        try:
            if num_questions == -1:
                num_questions = self.default_num_tests

            formatted_metrics = ""
            for category, metrics in self.available_metrics.items():
                formatted_metrics += f"  Metric category: {category}\n"
                for metric in metrics:
                    formatted_metrics += f"    {' aka '.join(metric)}\n"

            prompt = (
                f"I want you to generate some questions for a business intelligence dashboard.\n\n"
                f"Here is a list of metrics and dimensions that can be used and their possible values:\n\n"
                f"An imperative phrase to start each question, such as: {', '.join(self.imperatives)}\n"
                f"Use your own generated imperative once in a while.\n\n"
                f"Metrics:\n"
                f"{formatted_metrics}\n\n"
                f"Dimensions:\n"
                f"  Location centric: \n"
                f"    Regions: Possible values: {', '.join(self.regions)}\n"
                f"    Zones: Possible values: {', '.join(self.zones)}\n\n"
                f"  Channels: Possible values: {', '.join(self.sub_channels)}\n\n"
                f"  Product centric: \n"
                # f"    Products: Possible values: {', '.join(self.products)}\n"
                f"    Broad Segments: Possible values: {', '.join(self.broad_segments)}\n"
                f"    LOBs: Possible values: {', '.join(self.lobs)}\n\n"
                f"  Temporal: \n"
                f"    Month to Date (MTD)\n"
                f"    Quarter to Date (QTD)\n"
                f"    Year to Date (YTD)\n"
                f"    Specific Month (e.g., March 2025)\n"
                f"    Specific Quarter (e.g., Q3 2024)\n"
                f"    Specific Year (e.g., 2023)\n\n"
                f"  Additional temporal (for persistency only): \n"
                f"    One of 13M, 25M, 37M, 49M, 61M, indicating a rolling monthly period\n\n"
                f"One well-formed question can be one of:\n"
                f"  - Seeking answer for a single metric (overall or drilled down):\n"
                f"    - One metric from one category, using one of the possible names for the metric\n"
                f"    - Zero or one temporal condition\n"
                f"    - Zero or one location centric dimension (region or zone)\n"
                f"    - Zero or one channel\n"
                f"    - Zero or one product centric dimension (product, broad segment, or LOB)\n"
                f"  - Seeking comparison of a metric between two instances of a dimension:\n"
                f"    - One metric from one category, using one of the possible names for the metric\n"
                f"    - Zero or one temporal condition\n"
                f"    - Two or more instances of a dimension that can be:\n"
                f"      - location centric (region or zone)\n"
                f"      - channel\n"
                f"      - product centric (product, broad segment, or LOB)\n\n"
                f"    - One of more of another dimension to drill down the comparison\n"
                f"  - A list of ranked performers (best or worst) :\n"
                f"    - One metric from one category, using one of the possible names for the metric\n"
                f"    - Zero or one temporal condition\n"
                f"    - One dimension that can be:\n"
                f"      - location centric (region or zone)\n"
                f"      - channel\n"
                f"      - product centric (product, broad segment, or LOB)\n"
                f"    - Zero or more of another dimension to drill down the ranking\n"
                f"    - Whether best or worst, and how many (min 1, max 10)\n\n"
                f"Guidelines:\n"
                f"Each question should be a single line, starting with an imperative phrase, "
                f"and should be in natural English as if spoken by a business user.\n"
                f"Introduce subtle spelling and grammar mistakes once in a while."
                f"Each question should be unique and not repeat any other question.\n\n"
                f"Display one question per line, starting with 1-based serial number.\n"
                f"At the start and end of the list print a line with ===\n\n"
                f"Use the above information to generate {num_questions} relevant questions.\n\n"
            )

            print(prompt, flush=True)

            llm_response = await self.llm_client.generate_reply(prompt)
            if not llm_response.is_success:
                return llm_response.message
            if llm_response.payload is None:
                return "LLM returned no payload."

            return llm_response.payload

        except Exception as e:
            print(f"Error in LLM generation: {e}")
            return "LLM generation failed."

    async def run_once(self, num_questions=-1) -> None:
        await qgen.async_init()
        result = await self.generate_with_llm(num_questions=num_questions)
        print(result)


if __name__ == "__main__":
    load_dotenv()

    num_lines = -1
    try:
        num_lines = int(argv[1])
    except Exception as e:
        print(f"Warning: {e}")

    qgen = QGen().set_conn_string(getenv(EnvVars.conn_string, Defaults.conn_string))
    run(qgen.run_once(num_questions=num_lines))
