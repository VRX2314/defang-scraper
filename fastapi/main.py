from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import StreamingResponse
from crawler import Crawler
app = FastAPI(docs_url="/")

@app.post("/stream-indeed")
async def stream_indeed(query: str, location: str, listings: int = 1):
    """
    Stream job listings from Indeed based on the specified query and location.

    This endpoint initializes a Crawler instance with the provided search parameters
    and returns a streaming response of job listings in JSON format.

    Args:
        query (str): The job title or keywords to search for.
        location (str): The location to search for jobs.
        listings (int): The number of job listings to scrape. Defaults to 1.

    Returns:
        StreamingResponse: A streaming response containing the scraped job listings in JSON format.
    """
    crawler = Crawler(query, location, listings)

    return StreamingResponse(crawler.scrape_indeed_self())