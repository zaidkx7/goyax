import os
import json
import requests

from typing import Any, Dict, List
from bs4 import BeautifulSoup
from clogger import get_logger
from exceptions import *


class GoyaxScrapper:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(PROJECT_DIR, 'data')
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    JSON_FILE = os.path.join(DATA_DIR, 'data.json')

    def __init__(self, url: str) -> None:
        self.logger = get_logger()
        self.url: str = url
        self.report_: Dict[str, str] = {}
        self.logger.info("Initializing scraper for GOYAX")
        self.resp: str = self.get_resp()
        self.soup: BeautifulSoup = BeautifulSoup(self.resp, 'html.parser')

    def get_resp(self) -> str:
        """Fetches the HTML response text from the given URL."""
        self.logger.info("Sending GET request to the URL...")
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.logger.info("Successfully fetched the response.")
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch the URL: %s", e)
            raise RequestExceptionError(f"Request error: {e}") from e

    def get_data(self) -> str:
        """
        Extracts the main stock data from the page and returns it as a JSON-formatted string.
        Raises: DataExtractionError: If any part of the extraction fails.
        """
        self.logger.info("Extracting main stock data...")
        try:
            details = self.soup.find('p', class_='instrument-details')
            table_headers = self.get_table_data()
            side_data = self.get_unlisted_data()

            instrument_fullname_div = self.soup.find(
                'div', class_='instrument-fullname')
            if instrument_fullname_div is None:
                raise DataExtractionError(
                    "Instrument fullname section not found.")

            h1 = instrument_fullname_div.find('h1')
            p = instrument_fullname_div.find('p')
            if not h1 or not p:
                raise DataExtractionError(
                    "Name components not found in instrument fullname section.")
            name = h1.text.strip() + " " + p.text.strip()

            main_price = self.soup.find('span', class_='main-price')
            unit = self.soup.find('span', class_='unit')
            if not main_price or not unit:
                raise DataExtractionError("Price components not found.")
            price = main_price.text.strip() + " " + unit.text.strip()

            data: Dict[str, Any] = {
                'main_stock_data': {
                    "name": name,
                    "price": price,
                }
            }

            if details:
                spans = details.find_all('span', class_='badge')
                for span in spans:
                    label = span.get('aria-label')
                    if label:
                        text = span.text.split(":")[1].strip(
                        ) if ":" in span.text else span.text.strip()
                        if label == 'Währung':
                            label = label.replace('Währung', 'Wahrung')
                        data['main_stock_data'][label.lower()] = text
                if table_headers:
                    data['main_stock_data']['statistiken'] = table_headers
            if side_data:
                data['main_stock_data']['side_data'] = side_data

            self.logger.info("Main stock data extracted successfully.")
            return json.dumps(data, indent=4)
        except Exception as e:
            self.logger.error("Error extracting main stock data: %s", e)
            raise DataExtractionError(f"Data extraction error: {e}") from e

    def get_table_data(self) -> Dict[str, Any]:
        """
        Extracts table data from the page.
        Raises:
            TableDataExtractionError: If the expected table section is not found.
        """
        self.logger.info("Extracting table data...")
        table_data = self.soup.find('div', class_='instrument-statistik mt-10')
        if not table_data:
            raise TableDataExtractionError("Table data section not found.")

        header_elements = table_data.tr.find_all('th')
        headers: List[str] = [x.text.strip() for x in header_elements]
        statistics: Dict[str, Any] = {
            "headers": headers,
            "rows": []
        }

        rows = table_data.tbody.find_all('tr')
        for row in rows:
            th_data = row.th.text.strip() if row.th else ""
            td_data = [x.text.strip() for x in row.find_all('td')]
            cells: List[str] = [th_data] + td_data
            statistics["rows"].append(cells)

        self.logger.info("Table data extracted successfully.")
        return statistics

    def get_unlisted_data(self) -> Dict[str, Dict[str, str]]:
        """
        Extracts the side (unlisted) data from the page.
        Raises:
            UnlistedDataExtractionError: If the unlisted data section is not found.
        """
        self.logger.info("Extracting unlisted data (side data)...")
        unlisted_data = self.soup.find(
            'div', class_='wrap-areas wrap-area-aside')
        if not unlisted_data:
            raise UnlistedDataExtractionError(
                "Unlisted data section not found.")

        side_data: Dict[str, Dict[str, str]] = {}
        sections = unlisted_data.find_all("div", class_="section-area")
        for section in sections:
            section_title = section.find("h2")
            if section_title:
                section_name = section_title.text.strip()
                ul = section.find("ul", class_="list-rows")
                if ul:
                    section_data = {
                        li.find_all("span")[0].text.strip(): li.find_all("span")[1].text.strip()
                        for li in ul.find_all("li") if len(li.find_all("span")) >= 2
                    }
                    side_data[section_name] = section_data

        self.logger.info("Unlisted data extracted successfully.")
        return side_data

    def save_data_to_json(self, data: Dict[str, Any]) -> None:
        """
        Saves the provided data dictionary to a JSON file.
        Raises:
            FileSaveError: If the data cannot be saved.
        """
        self.logger.info("Saving data to JSON file...")
        try:
            with open(self.JSON_FILE, "w") as json_file:
                json.dump(data, json_file, indent=4)
            self.logger.info("Data successfully saved to %s", self.JSON_FILE)
        except Exception as e:
            self.logger.error("Error saving data to file: %s", e)
            raise FileSaveError(f"File save error: {e}") from e


if __name__ == "__main__":
    scrapper = GoyaxScrapper(
        "https://www.goyax.de/aktien/DE000A3E5A26/arbitrage-investment-ag/#instrument-ueberblick")
    try:
        data_str = scrapper.get_data()
        data = json.loads(data_str)
        scrapper.save_data_to_json(data)
    except GoyaxScrapperError as e:
        scrapper.logger.critical("An error occurred: %s", e)
    scrapper.logger.info("GoyaxScrapper execution finished.")
