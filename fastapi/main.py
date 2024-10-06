from fastapi import FastAPI, Body, File, UploadFile
from fastapi.responses import StreamingResponse
from crawler import Crawler
app = FastAPI()

@app.post("/stream-indeed")
async def stream_indeed(query: str, location: str, listings: int = 1):
    crawler = Crawler(query, location, listings)

    return StreamingResponse(crawler.scrape_indeed_self())