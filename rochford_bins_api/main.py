import asyncio
import dataclasses
import json
import logging
from pathlib import Path
from playwright.async_api import Browser, Playwright, async_playwright

from rochford_bins_api.encoder import JSONEncoder
from rochford_bins_api.models.BinsAndCollectionsCalendarPage import BinsAndCollectionsCalendarPage
from rochford_bins_api.models.BinsAndCollectionsPage import BinsAndCollectionsPage
from rochford_bins_api.types import AllRoadsResponse, BinCollectionDate, RoadDetailResponse, RoadOverview
from rochford_bins_api.util import weekday_to_int

logger = logging.getLogger(__name__)

async def scrape_batch(
    browser: Browser,
    roads: list[str],
    all_collection_dates: list[BinCollectionDate],
):
    page = await browser.new_page()
    collections_page = BinsAndCollectionsPage(page)
    await collections_page.navigate()
    for i, road in enumerate(roads):
        logger.info(f"Fetching info for road {i + 1} / {len(roads)}...")
        road_overview = await collections_page.select_road_name(road)

        collection_days = [
            d
            for d in all_collection_dates
            if road_overview.usual_collection_day and d.date.weekday() == weekday_to_int(road_overview.usual_collection_day)
        ]
        
        output_path = Path(f"out/collections/{road}.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Generating JSON file for road {i + 1} / {len(roads)}...")
        with open(output_path, "w") as f:
            json.dump(dataclasses.asdict(RoadDetailResponse(
                road,
                road_overview.area,
                road_overview.usual_collection_day,
                collection_days
            )), f, cls=JSONEncoder)
        logger.info(f"File generated {output_path}.")
    await page.close()


async def main():
    logging.basicConfig(level=logging.INFO)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        calendar_page = BinsAndCollectionsCalendarPage(page)
        await calendar_page.navigate()
        logger.info("Fetching all collection dates...")
        all_collection_dates = await calendar_page.get_bin_collection_dates()
        logger.info("Fetching all collection dates... Done")

        collections_page = BinsAndCollectionsPage(page)
        await collections_page.navigate()
        logger.info("Fetching all road names...")
        all_roads = await collections_page.get_all_road_names()
        logger.info("Fetching all road names... Done")

        all_road_overviews: list[RoadOverview] = []
        logger.info(f"{len(all_roads)} roads found. Fetching road-specific info...")
        batch_size = 50

        tasks = [
            scrape_batch(browser, all_roads[i : i + batch_size], all_collection_dates)
            for i in range(0, len(all_roads), batch_size)
        ]

        await asyncio.gather(*tasks)

        logger.info("Generating top-level roads.json file...")
        output_path = Path("out/roads.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(dataclasses.asdict(AllRoadsResponse(all_road_overviews)), f)
        logger.info(f"File generated {output_path}.")


asyncio.run(main())
