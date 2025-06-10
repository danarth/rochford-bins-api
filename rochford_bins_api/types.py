from dataclasses import dataclass
from datetime import datetime


@dataclass
class BinCollectionDate:
    date: datetime
    bin_type: str


@dataclass
class RoadOverview:
    road: str
    area: str
    usual_collection_day: str


@dataclass
class AllRoadsResponse:
    all_roads: list[RoadOverview]


@dataclass
class RoadDetailResponse:
    road: str
    area: str
    usual_collection_day: str
    collection_days: list[BinCollectionDate]
    

