from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import trafilatura
import re

app = FastAPI(title="AI-Ready Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    include_links: bool = True

def find_video_url(html_content: str) -> str:
    """
    Scans raw HTML for YouTube links, embeds, or standard video tags.
    """
    if not html_content:
        return None
    
    # Check for standard YouTube watch or embed links
    yt_match = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=|embed/)[a-zA-Z0-9_-]+)', html_content)
    if yt_match:
        return yt_match.group(1)
        
    # Fallback to general video source or iframe links if present
    video_match = re.search(r'src="(https?://[^"]+\.(?:mp4|webm))"', html_content)
    if video_match:
        return video_match.group(1)
        
    return None

@app.post("/scrape")
async def scrape_url(data: ScrapeRequest):
    try:
        downloaded = trafilatura.fetch_url(data.url)
        
        if downloaded is None:
            raise HTTPException(status_code=400, detail="Could not fetch data from URL.")
        
        # Pull metadata for the main article image
        metadata = trafilatura.extract_metadata(downloaded)
        main_image_url = metadata.image if metadata else None

        # Scan for any video links hidden in the page
        video_url = find_video_url(downloaded)

        markdown_result = trafilatura.extract(
            downloaded, 
            output_format="markdown",
            include_links=data.include_links,
            include_images=False
        )
        
        if not markdown_result:
            raise HTTPException(status_code=422, detail="Failed to extract readable text.")
            
        return {
            "success": True,
            "target_url": data.url,
            "main_image": main_image_url,
            "video_url": video_url,  # NEW: Drops the video link right here
            "content": markdown_result
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
