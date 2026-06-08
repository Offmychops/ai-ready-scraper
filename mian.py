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
    Fetches a web page, strips all layout junk (ads, menus, footers),
    and converts the core content into clean Markdown for AI use.
    """
    try:
        # 1. Fetch the raw HTML from the target web address securely
        downloaded = trafilatura.fetch_url(data.url)
        
        if downloaded is None:
            raise HTTPException(
                status_code=400, 
                detail="Could not fetch data from URL. Make sure it is valid and public."
            )
        
        # 2. Extract the main content and convert it directly to clean markdown formatting
        markdown_result = trafilatura.extract(
            downloaded, 
            output_format="markdown",
            include_links=data.include_links,
            include_images=False
        )
        
        if not markdown_result:
            raise HTTPException(
                status_code=422, 
                detail="Failed to extract readable article text from this page structure."
            )
            
        return {
            "success": True,
            "target_url": data.url,
            "content": markdown_result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))