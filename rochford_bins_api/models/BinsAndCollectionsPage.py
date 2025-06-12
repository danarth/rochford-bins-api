from typing import final
from playwright.async_api import Locator, Page, expect

from rochford_bins_api.types import RoadOverview


@final
class BinsAndCollectionsPage:
    def __init__(self, page: Page):
        self.page = page
        collection_widget = page.locator(".block-views-block--widgets-widgets-bins")
        self.road_selector = collection_widget.get_by_label("Select Road")
        self.road_name = collection_widget.locator(".views-field-name h3")
        self.area_name: Locator = collection_widget.locator(".views-field-field-area .field-content")
        self.collection_day = collection_widget.locator(".views-field-field-day .field-content")

    async def navigate(self):
        await self.page.goto("https://www.rochford.gov.uk/bins-and-collections")

    async def get_all_road_names(self) -> list[str]:
        options = self.road_selector.locator("option")
        road_names = await options.all_inner_texts()
        road_names.remove("- Any -")
        return road_names

    async def select_road_name(self, road_name: str) -> RoadOverview:
        await self.road_selector.select_option(road_name)
        await expect(self.road_name).to_have_text(road_name)
        area = await self.area_name.inner_text() if await self.area_name.count() else ""
        collection_day = await self.collection_day.inner_text() if await self.collection_day.count() else ""
        return RoadOverview(road_name, area, collection_day)
