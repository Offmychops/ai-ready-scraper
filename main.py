from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import trafilatura

app = FastAPI(title="AI-Ready Scraper API")

class ScrapeRequest(BaseModel):
    url: str
    include_links: bool = True

@app.post("/scrape")
async def scrape_url(data: ScrapeRequest):
    """
    Fetches a web page, extracts the main image URL, strips layout junk,
    and converts the core content into clean Markdown.
    """
    try:
        # 1. Fetch the raw HTML from the target web address
        downloaded = trafilatura.fetch_url(data.url)
        
        if downloaded is None:
            raise HTTPException(
                status_code=400, 
                detail="Could not fetch data from URL. Make sure it is valid and public."
            )
        
        # NEW: Extract the main featured/lead image URL of the article
        metadata = trafilatura.extract_metadata(downloaded)
        main_image_url = metadata.image if metadata else None

        # 2. Extract the main body text and convert to clean markdown
        markdown_result = trafilatura.extract(
            downloaded, 
            output_format="markdown",
            include_links=data.include_links,
            include_images=False  # Keeps the main body text clean of inline junk images
        )
        
        if not markdown_result:
            raise HTTPException(
                status_code=422, 
                detail="Failed to extract readable article text from this page structure."
            )
            
        return {
            "success": True,
            "target_url": data.url,
            "main_image": main_image_url,  # NEW: Drops the main picture link right here
            "content": markdown_result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
