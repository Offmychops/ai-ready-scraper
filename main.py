from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import trafilatura

app = FastAPI(title="AI-Ready Scraper API")

# NEW: Tell the API to accept requests from absolutely anywhere (like your local browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

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
        downloaded = trafilatura.fetch_url(data.url)
        
        if downloaded is None:
            raise HTTPException(
                status_code=400, 
                detail="Could not fetch data from URL. Make sure it is valid and public."
            )
        
        metadata = trafilatura.extract_metadata(downloaded)
        main_image_url = metadata.image if metadata else None

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
            "main_image": main_image_url,
            "content": markdown_result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
