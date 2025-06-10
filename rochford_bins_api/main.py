import dataclasses
import json
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

from rochford_bins_api.encoder import JSONEncoder
from rochford_bins_api.models.BinsAndCollectionsCalendarPage import BinsAndCollectionsCalendarPage
from rochford_bins_api.models.BinsAndCollectionsPage import BinsAndCollectionsPage
from rochford_bins_api.types import AllRoadsResponse, RoadDetailResponse, RoadOverview
from rochford_bins_api.util import weekday_to_int

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO)
    with sync_playwright() as p:
        with p.chromium.launch() as browser:
            page = browser.new_page()
            calendar_page = BinsAndCollectionsCalendarPage(page)
            calendar_page.navigate()
            logger.info("Fetching all collection dates...")
            all_collection_dates = calendar_page.get_bin_collection_dates()
            logger.info("Fetching all collection dates... Done")

            collections_page = BinsAndCollectionsPage(page)
            collections_page.navigate()
            logger.info("Fetching all road names...")
            all_roads = collections_page.get_all_road_names()
            logger.info("Fetching all road names... Done")

            all_road_overviews: list[RoadOverview] = []
            logger.info(f"{len(all_roads)} roads found. Fetching road-specific info...")
            for i, road in enumerate(all_roads):
                logger.info(f"Fetching info for road {i + 1} / {len(all_roads)}...")
                road_overview = collections_page.select_road_name(road)
                all_road_overviews.append(road_overview)

                collection_days = [
                    d
                    for d in all_collection_dates
                    if road_overview.usual_collection_day and d.date.weekday() == weekday_to_int(road_overview.usual_collection_day)
                ]
                
                output_path = Path(f"out/collections/{road}.json")
                output_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Generating JSON file for road {i + 1} / {len(all_roads)}...")
                with open(output_path, "w") as f:
                    json.dump(dataclasses.asdict(RoadDetailResponse(
                        road,
                        road_overview.area,
                        road_overview.usual_collection_day,
                        collection_days
                    )), f, cls=JSONEncoder)
                logger.info(f"File generated {output_path}.")

            logger.info("Generating top-level roads.json file...")
            output_path = Path("out/roads.json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(dataclasses.asdict(AllRoadsResponse(all_road_overviews)), f)
            logger.info(f"File generated {output_path}.")


main()
