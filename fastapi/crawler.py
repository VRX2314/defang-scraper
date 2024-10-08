import asyncio
import json
from datetime import datetime, timedelta

import re
from textwrap import indent

from playwright.async_api import async_playwright
import numpy as np


# ! Scraper Branch
def convert_posting_time(posting_time_str):
    # Check if the posting time contains "Just posted"
    if "Just posted" in posting_time_str:
        return datetime.now().strftime("%Y-%m-%d")  # Return today's date

    # Use regex to find the number of days ago
    match = re.search(r'Posted (\d+) days ago', posting_time_str)
    if match:
        days_ago = int(match.group(1))  # Extract the number of days
        posting_date = datetime.now() - timedelta(days=days_ago)  # Subtract days from current date
        return posting_date.strftime("%d-%m-%Y")  #


class Crawler:
    def __init__(self, query, location, listings):
        """
        Initialize the Crawler instance.

        Args:
            query (str): The job title or keywords to search for.
            location (str): The location to search for jobs.
            listings (int): The number of job listings to scrape.
        """
        self.browser = None
        self.page = None

        self.query = query
        self.listings = listings  # TODO Make Dynamic
        self.location = location

        self.today = datetime.today().date()

    async def _load_page(self):
        """
       Load the Indeed job search page and fill in the search criteria.

       This function navigates to the Indeed website, fills in the job title and location,
       and clicks the search button. It also attempts to close any modal that may appear.
        """

        await self.page.goto("https://in.indeed.com/")
        print("On indeed")
        await self.page.wait_for_selector("input#text-input-what", timeout=60000)
        print("Selector found")
        await self.page.fill("input#text-input-what", self.query)
        await self.page.fill("input#text-input-where", self.location)
        await self.page.click("button.yosegi-InlineWhatWhere-primaryButton")

        await self.page.click("span#dateLabel")
        # Close modal if it appears
        await self._close_modal()
        await self.page.wait_for_timeout(1000)

    async def _close_modal(self):
        """
        Close any modal that appears on the page.

        This function waits for a modal to appear and attempts to close it.
        If no modal appears or an error occurs, it logs an appropriate message.
        """
        try:
            # Wait for the modal to appear and then close it
            await self.page.wait_for_selector("#mosaic-desktopserpjapopup", timeout=5000)
            close_button = await self.page.query_selector("button[aria-label='close']")
            if close_button:
                await asyncio.sleep(np.random.choice(np.arange(1, 2, 0.0001)))
                await close_button.click()
                print("Modal closed.")
        except Exception as e:
            print("No modal appeared or failed to close:", str(e))

    async def _load_browser(self, p):
        """
       Load the browser using Playwright.

       Args:
           p: The Playwright instance used to launch the browser.
       """
        self.browser = await p.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

    async def scrape_indeed(self, job) -> dict:
        """
       Scrape job details from an Indeed job listing.

       Args:
           job: The job element from which details will be scraped.

       Returns:
           dict: A dictionary containing job details such as title, company,
                 location, description, link, and posting date.
       """
        await job.click(timeout=30000)
        await self.page.wait_for_selector(
            "h2.jobsearch-JobInfoHeader-title", timeout=5000
        )

        job_title_element = await self.page.query_selector(
            "h2.jobsearch-JobInfoHeader-title"
        )
        job_title = await job_title_element.inner_text() if job_title_element else "N/A"

        company_name_element = await self.page.query_selector(
            'div[data-company-name="true"]'
        )
        company_name = (
            await company_name_element.inner_text() if company_name_element else "N/A"
        )

        location_element = await self.page.query_selector(
            'div[data-testid="inlineHeader-companyLocation"]'
        )
        location = await location_element.inner_text() if location_element else "N/A"

        job_description_element = await self.page.query_selector(
            "div.jobsearch-JobComponent-description"
        )
        job_description = (
            await job_description_element.inner_text()
            if job_description_element
            else None
        )

        posting_time_element = await self.page.query_selector('span[data-testid="myJobsStateDate"]')
        posting_time_str = await posting_time_element.inner_text() if posting_time_element else "N/A"
        posting_date = convert_posting_time(posting_time_str=posting_time_str)

        return {
            "Title": job_title,
            "Company": company_name,
            "Location": location,
            "Description": job_description,
            "Link": self.page.url,
            "Date": posting_date
        }

    async def scrape_indeed_self(self):
        """
        Scrape multiple job listings from Indeed based on the specified query and location.

        This function initializes the browser, loads the search page, and iteratively
        scrapes job listings until the specified number of listings has been reached
        or no more listings are available.

        Yields:
             str: A JSON string representation of each scraped job listing.
        """
        async with async_playwright() as p:
            await self._load_browser(p)
            print("Browser on.")
            await self._load_page()
            counter = 0

            while counter < self.listings:
                job_elements = await self.page.query_selector_all(
                    ".jobTitle.css-198pbd.eu4oa1w0"
                )

                for job in job_elements:
                    scraped_job = await self.scrape_indeed(job)

                    yield json.dumps(scraped_job, indent=2)  # dict -> str to stream

                    # Simulating randomness to avoid bot detection
                    await asyncio.sleep(np.random.choice(np.arange(1, 3, 0.0001)))

                    counter += 1
                    if self.listings == counter:
                        print("Scraped Successfully!")
                        return

                # Page navigation
                next_button = await self.page.query_selector(
                    'a[data-testid="pagination-page-next"]'
                )
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_timeout(5000)
                else:
                    break
