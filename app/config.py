import os
import json
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR
DB_PATH = BASE_DIR / "leads.db"
CSV_PATH = BASE_DIR / "leads.csv"
EXCEL_PATH = BASE_DIR / "leads.xlsx"
SETTINGS_PATH = BASE_DIR / "settings.json"

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia"
}

TOP_US_CITIES = [
    {"city": "New York", "state": "NY"},
    {"city": "Los Angeles", "state": "CA"},
    {"city": "Chicago", "state": "IL"},
    {"city": "Houston", "state": "TX"},
    {"city": "Phoenix", "state": "AZ"},
    {"city": "Philadelphia", "state": "PA"},
    {"city": "San Antonio", "state": "TX"},
    {"city": "San Diego", "state": "CA"},
    {"city": "Dallas", "state": "TX"},
    {"city": "Austin", "state": "TX"},
    {"city": "Jacksonville", "state": "FL"},
    {"city": "Fort Worth", "state": "TX"},
    {"city": "San Jose", "state": "CA"},
    {"city": "Columbus", "state": "OH"},
    {"city": "Charlotte", "state": "NC"},
    {"city": "Indianapolis", "state": "IN"},
    {"city": "San Francisco", "state": "CA"},
    {"city": "Seattle", "state": "WA"},
    {"city": "Denver", "state": "CO"},
    {"city": "Nashville", "state": "TN"},
    {"city": "Miami", "state": "FL"},
    {"city": "Atlanta", "state": "GA"},
    {"city": "Las Vegas", "state": "NV"},
    {"city": "Orlando", "state": "FL"},
    {"city": "Tampa", "state": "FL"},
]

POPULAR_CATEGORIES = [
    "Plumbing",
    "Roofing",
    "Landscaping & Lawn Care",
    "Electrician",
    "HVAC & Air Conditioning",
    "Auto Repair & Mechanics",
    "Bakery & Pastry Shop",
    "Barbershop & Hair Salon",
    "House Cleaning & Maid Service",
    "General Contractor / Home Remodeling",
    "Painter & Drywall",
    "Dentist & Orthodontics",
    "Pest Control",
    "Restaurant & Cafe",
    "Handyman Services",
    "Towing Service",
    "Photography",
    "Accounting & Bookkeeping",
    "Pet Grooming & Boarding",
    "Personal Fitness Trainer / Gym"
]

DEFAULT_SETTINGS = {
    "google_places_api_key": "",
    "google_sheets_webhook_url": "",
    "reddit_client_id": "",
    "reddit_client_secret": "",
    "auto_verify_websites": True,
    "default_export_format": "both"  # "csv", "excel", "both"
}

def load_settings() -> Dict[str, Any]:
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                res = DEFAULT_SETTINGS.copy()
                res.update(saved)
                return res
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(new_settings: Dict[str, Any]) -> None:
    current = load_settings()
    current.update(new_settings)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)

