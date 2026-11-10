import time
import logging
from typing import Optional
from app.finders.no_website_finder import NoWebsiteFinder
from app.finders.seeking_website_finder import SeekingWebsiteFinder
from app.storage.database import insert_leads, get_stats
from app.storage.sheet_manager import sync_sheets
from app.config import TOP_US_CITIES

logger = logging.getLogger(__name__)

def run_lead_generation_cycle() -> int:
    """Executes a full lead discovery cycle across US sources and appends to sheets."""
    no_web_finder = NoWebsiteFinder()
    seeking_web_finder = SeekingWebsiteFinder()

    total_added = 0

    # 1. Search for businesses without a website across key US cities
    for metro in TOP_US_CITIES[:5]:
        city = metro["city"]
        state = metro["state"]
        found = no_web_finder.search(city=city, state=state, limit=5)
        added = insert_leads(found)
        total_added += added

    # 2. Search for people seeking websites
    for kw in ["need a website", "looking for web designer"]:
        found = seeking_web_finder.search(keywords=kw, limit=8)
        added = insert_leads(found)
        total_added += added

    # Sync all sheets
    sync_sheets()
    stats = get_stats()
    print(f"Cycle completed: {total_added} new leads added. Total in sheet: {stats['total_leads']}")
    return total_added

def run_continuous_scheduler(interval_hours: int = 6):
    """Runs periodic lead finding in a loop."""
    print(f"Starting lead finder background worker (interval: every {interval_hours} hours)...")
    while True:
        try:
            run_lead_generation_cycle()
        except Exception as e:
            logger.error(f"Error during scheduled cycle: {e}")
        time.sleep(interval_hours * 3600)

if __name__ == "__main__":
    run_lead_generation_cycle()
