import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import (
    CSV_PATH, EXCEL_PATH, US_STATES, TOP_US_CITIES,
    POPULAR_CATEGORIES, load_settings, save_settings
)
from app.models import Lead, LeadType, LeadStatus, LeadSearchParams, StatusUpdateRequest
from app.storage.database import (
    init_db, insert_leads, get_leads, get_lead_by_id,
    update_lead_status, delete_lead, get_stats
)
from app.storage.sheet_manager import sync_sheets, push_to_google_sheet_webhook, GOOGLE_APPS_SCRIPT_TEMPLATE
from app.finders.no_website_finder import NoWebsiteFinder
from app.finders.seeking_website_finder import SeekingWebsiteFinder
from app.outreach.generator import generate_pitch

app = FastAPI(title="US Lead Finder", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

no_web_finder = NoWebsiteFinder()
seeking_web_finder = SeekingWebsiteFinder()

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Seed initial leads if DB is empty so user has immediate rich data
    current_leads = get_leads(limit=1)
    if not current_leads:
        initial_no_web = no_web_finder.search(limit=15)
        initial_seeking = seeking_web_finder.search(limit=10)
        insert_leads(initial_no_web + initial_seeking)
        sync_sheets()

@app.get("/api/meta")
def get_metadata():
    return {
        "states": US_STATES,
        "top_cities": TOP_US_CITIES,
        "popular_categories": POPULAR_CATEGORIES,
        "google_apps_script_template": GOOGLE_APPS_SCRIPT_TEMPLATE
    }

@app.get("/api/stats")
def get_dashboard_stats():
    return get_stats()

@app.get("/api/leads")
def list_leads(
    lead_type: Optional[LeadType] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[LeadStatus] = None,
    search: Optional[str] = None,
    limit: int = 500,
    offset: int = 0
):
    leads = get_leads(
        lead_type=lead_type,
        state=state,
        city=city,
        category=category,
        status=status,
        search_query=search,
        limit=limit,
        offset=offset
    )
    return {"leads": leads, "count": len(leads)}

class NoWebsiteSearchPayload(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    limit: int = 15

@app.post("/api/leads/search-no-website")
def search_no_website_leads(payload: NoWebsiteSearchPayload, background_tasks: BackgroundTasks):
    results = no_web_finder.search(
        city=payload.city,
        state=payload.state,
        category=payload.category,
        limit=payload.limit
    )
    new_count = insert_leads(results)
    # Auto sync to CSV & Excel
    sync_sheets()
    return {
        "status": "success",
        "found_leads": len(results),
        "new_leads_added": new_count,
        "leads": results
    }

class SeekingWebsiteSearchPayload(BaseModel):
    keywords: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    limit: int = 15

@app.post("/api/leads/search-seeking-website")
def search_seeking_website_leads(payload: SeekingWebsiteSearchPayload, background_tasks: BackgroundTasks):
    results = seeking_web_finder.search(
        keywords=payload.keywords,
        city=payload.city,
        state=payload.state,
        category=payload.category,
        limit=payload.limit
    )
    new_count = insert_leads(results)
    # Auto sync to CSV & Excel
    sync_sheets()
    return {
        "status": "success",
        "found_leads": len(results),
        "new_leads_added": new_count,
        "leads": results
    }

@app.put("/api/leads/{lead_id}/status")
def update_status(lead_id: str, payload: StatusUpdateRequest):
    success = update_lead_status(lead_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    sync_sheets()
    return {"status": "success", "lead_id": lead_id, "new_status": payload.status}

@app.delete("/api/leads/{lead_id}")
def remove_lead(lead_id: str):
    success = delete_lead(lead_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    sync_sheets()
    return {"status": "success", "deleted_id": lead_id}

@app.get("/api/leads/{lead_id}/outreach")
def get_outreach_templates(lead_id: str):
    lead = get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    pitch = generate_pitch(lead)
    return {"lead": lead, "pitch": pitch}

@app.get("/api/export/csv")
def download_csv():
    sync_sheets()
    if not CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    return FileResponse(
        path=CSV_PATH,
        filename="us_leads.csv",
        media_type="text/csv"
    )

@app.get("/api/export/excel")
def download_excel():
    sync_sheets()
    if not EXCEL_PATH.exists():
        raise HTTPException(status_code=404, detail="Excel file not found")
    return FileResponse(
        path=EXCEL_PATH,
        filename="us_leads.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.post("/api/sync/google-sheet")
def sync_google_sheet():
    settings = load_settings()
    webhook_url = settings.get("google_sheets_webhook_url")
    if not webhook_url:
        return {"success": False, "message": "No Google Sheets webhook URL configured in settings."}

    leads = get_leads(limit=10000)
    res = push_to_google_sheet_webhook(leads, webhook_url)
    return res

@app.get("/api/settings")
def get_current_settings():
    return load_settings()

@app.post("/api/settings")
def update_settings(new_settings: Dict[str, Any]):
    save_settings(new_settings)
    return {"status": "success", "settings": load_settings()}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    template_path = Path(__file__).parent / "templates" / "index.html"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Lead Finder is running. UI template loading...</h1>")

