import re
from datetime import timedelta
from typing import final

from playwright.sync_api import Locator, Page

from rochford_bins_api.types import BinCollectionDate
from rochford_bins_api.util import parse_date


@final
class BinsAndCollectionsCalendarPage:
    def __init__(self, page: Page):
        self.page = page
        self.bin_collection_tables = page.locator("main article .wp-block-cp-table table")

    def navigate(self):
        self.page.goto("https://www.rochford.gov.uk/online-bin-collections-calendar")

    def get_bin_collection_dates(self):
        month_year_regex = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})$")
        all_records: list[BinCollectionDate] = []
        for table in self.bin_collection_tables.all():
            header = table.locator(":nth-match(thead th, 1)")
            header_text = (header.text_content() or "").strip()
            if match := month_year_regex.match(header_text):
                year = match.group(2)
                rows = table.locator("tbody tr").all()
                for row in rows:
                    all_records += self._expand_bin_collection_table_row(row, year)
        return all_records

    def _expand_bin_collection_table_row(self, row: Locator, year: str) -> list[BinCollectionDate]:
        """
        Given a row in a bin collection table, and the year, expand out each of the dates in the
        range with the correct bin type. Supports both date ranges and single dates.
        """
        date_range = row.locator(":nth-match(td, 1)").text_content()
        bin_type = row.locator(":nth-match(td, 2)").text_content()
        if not date_range or not bin_type:
            return []
        date_range = re.sub(r"(\d{1,2})(st|nd|rd|th)", r"\1", date_range)
        if "-" in date_range:
            dates = date_range.split("-")
            start_date = parse_date(dates[0], year)
            end_date = parse_date(dates[1], year)
            all_dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
            return [BinCollectionDate(d, bin_type) for d in all_dates]
        else:
            return [BinCollectionDate(parse_date(date_range, year), bin_type)]

