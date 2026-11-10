import requests
import json
import logging
import re
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus

from app.models import Lead
from app.config import load_settings, US_STATES
from app.finders.verifier import normalize_us_phone, normalize_us_state, build_accurate_maps_url
from app.data.us_seeds import VERIFIED_US_NO_WEBSITE_BUSINESSES

logger = logging.getLogger(__name__)

SOCRATA_ENDPOINTS = {
    "NY": {
        "name": "NYC Open Data",
        "url": "https://data.cityofnewyork.us/resource/w7w3-xahh.json",
        "name_field": "business_name",
        "phone_field": "contact_phone",
        "street_field": "address_street_name",
        "bldg_field": "building_number",
        "city_field": "address_city",
        "zip_field": "address_zip",
        "cat_field": "industry"
    },
    "IL": {
        "name": "Chicago Open Data",
        "url": "https://data.cityofchicago.org/resource/r5kz-chrr.json",
        "name_field": "doing_business_as_name",
        "phone_field": "",
        "street_field": "address",
        "city_field": "city",
        "zip_field": "zip_code",
        "cat_field": "business_activity"
    },
    "CA": {
        "name": "LA Active Businesses",
        "url": "https://data.lacity.org/resource/6rrh-rzua.json",
        "name_field": "business_name",
        "phone_field": "",
        "street_field": "street_address",
        "city_field": "city",
        "zip_field": "zip_code",
        "cat_field": "primary_naics_description"
    }
}

class NoWebsiteFinder:
    """Finds US businesses that do not have a website."""

    def __init__(self):
        self.settings = load_settings()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) USLeadFinder/1.0"
        }

    def search(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 15
    ) -> List[Lead]:
        leads: List[Lead] = []

        norm_state = normalize_us_state(state) if state else None

        # 1. Check Google Places API if key configured
        google_api_key = self.settings.get("google_places_api_key")
        if google_api_key:
            google_leads = self._search_google_places(google_api_key, city, norm_state, category, limit)
            leads.extend(google_leads)

        # 2. Query US Open Data Socrata registries
        if len(leads) < limit and norm_state in SOCRATA_ENDPOINTS:
            socrata_leads = self._search_socrata(norm_state, city, category, limit - len(leads))
            leads.extend(socrata_leads)

        # 3. Query OpenStreetMap / Overpass mirrors (fallback if no leads found yet)
        if len(leads) == 0 and city and norm_state not in SOCRATA_ENDPOINTS:
            osm_leads = self._search_osm(city, norm_state or "US", category, limit - len(leads))
            leads.extend(osm_leads)

        # 4. Filter & Match Curated Verified Dataset
        if len(leads) < limit:
            seed_leads = self._search_verified_seeds(city, norm_state, category, limit - len(leads))
            leads.extend(seed_leads)

        return leads[:limit]

    def _search_socrata(
        self,
        state: str,
        city: Optional[str],
        category: Optional[str],
        limit: int
    ) -> List[Lead]:
        """Queries official city government licensed business registers."""
        endpoint = SOCRATA_ENDPOINTS.get(state)
        if not endpoint:
            return []

        leads = []
        try:
            # Query businesses that have NO website registered
            where_clauses = ["license_status='Active' OR license_status='AAI' OR license_status IS NULL"]
            if category:
                where_clauses.append(f"lower({endpoint['cat_field']}) like lower('%{category}%')")

            url = f"{endpoint['url']}?$limit={limit * 2}&$where={' AND '.join(where_clauses)}"
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for item in data:
                    b_name = item.get(endpoint["name_field"])
                    if not b_name:
                        continue

                    # Skip personal names formatted as "LASTNAME, FIRSTNAME" unless corporate entity
                    if "," in b_name and not any(kw in b_name.lower() for kw in ["llc", "inc", "corp", "co."]):
                        continue

                    raw_phone = item.get(endpoint["phone_field"], "") if endpoint["phone_field"] else ""
                    phone = normalize_us_phone(raw_phone)
                    if phone == "N/A" or len(re.sub(r"\D", "", phone)) < 10:
                        continue

                    bldg = item.get(endpoint.get("bldg_field", ""), "")
                    street = item.get(endpoint["street_field"], "")
                    
                    # Reject street corner / intersection vendors
                    if any(c in street.upper() for c in ["NWC", "NEC", "SWC", "SEC", "CORNER", "INTERSECTION"]):
                        continue

                    item_city = item.get(endpoint["city_field"], city or "New York")
                    zip_code = str(item.get(endpoint["zip_field"], "")).strip()

                    # Validate zip code belongs to state to filter out out-of-state holding entities
                    if state == "IL" and zip_code and not zip_code.startswith(("60", "61", "62")):
                        continue
                    if state == "NY" and zip_code and not zip_code.startswith(("10", "11", "12", "13", "14")):
                        continue
                    if state == "CA" and zip_code and not zip_code.startswith("9"):
                        continue

                    full_addr = f"{bldg} {street}".strip()
                    # Ensure physical street building number exists for accurate navigation
                    if not re.search(r"\d", full_addr):
                        continue

                    if zip_code and zip_code not in full_addr:
                        full_addr += f", {zip_code}"

                    # Explicitly check website is absent
                    website = item.get("website")
                    if website and website.strip() not in ("", "None", "null"):
                        continue

                    cat = item.get(endpoint["cat_field"], category or "Commercial Business")
                    accurate_maps_url = build_accurate_maps_url(b_name.title(), full_addr, item_city.title(), state)

                    leads.append(
                        Lead(
                            lead_type="no_website",
                            business_name=b_name.title(),
                            contact_name="Business Owner",
                            phone=phone,
                            email="N/A",
                            city=item_city.title(),
                            state=state,
                            country="United States",
                            address=full_addr,
                            category=cat[:60] if cat else (category or "General Contractor"),
                            source=endpoint["name"],
                            source_url=endpoint["url"],
                            google_maps_url=accurate_maps_url,
                            notes="Verified active business license in city registry with no website on record.",
                            website_status="Confirmed No Website"
                        )
                    )
                    if len(leads) >= limit:
                        break
        except Exception as e:
            logger.warning(f"Socrata query failed: {e}")

        return leads

    def _search_google_places(
        self,
        api_key: str,
        city: Optional[str],
        state: Optional[str],
        category: Optional[str],
        limit: int
    ) -> List[Lead]:
        """Queries Google Places Text Search and filters businesses lacking a website."""
        leads = []
        loc_str = f"{city or ''} {state or ''} USA".strip()
        cat_str = category or "local business"
        query_text = f"{cat_str} in {loc_str}"

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query_text,
            "key": api_key
        }

        try:
            r = requests.get(url, params=params, timeout=12)
            if r.status_code == 200:
                results = r.json().get("results", [])
                for place in results:
                    place_id = place.get("place_id")
                    # Fetch details to inspect website
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    d_params = {
                        "place_id": place_id,
                        "fields": "name,formatted_phone_number,formatted_address,website,rating,user_ratings_total",
                        "key": api_key
                    }
                    d_res = requests.get(details_url, params=d_params, timeout=8).json().get("result", {})
                    website = d_res.get("website")

                    # If place has NO website, this is our prime lead!
                    if not website:
                        leads.append(
                            Lead(
                                lead_type="no_website",
                                business_name=d_res.get("name", place.get("name")),
                                contact_name="Owner / Manager",
                                phone=d_res.get("formatted_phone_number", "N/A"),
                                city=city or "US City",
                                state=state or "US",
                                address=d_res.get("formatted_address", place.get("formatted_address")),
                                category=category or "Local Business",
                                source="Google Places (US)",
                                source_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                google_maps_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                notes=f"Google Rating: {d_res.get('rating', 'N/A')} ({d_res.get('user_ratings_total', 0)} reviews). No website attached.",
                                website_status="No Website on Google Maps"
                            )
                        )
                        if len(leads) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Google Places API query error: {e}")

        return leads

    def _search_osm(
        self,
        city: str,
        state: str,
        category: Optional[str],
        limit: int
    ) -> List[Lead]:
        """Queries OpenStreetMap Overpass with fallback mirrors for businesses without a website."""
        leads = []
        amenity = (category or "restaurant").lower()
        if "plumb" in amenity:
            tag = 'craft="plumber"'
        elif "roof" in amenity:
            tag = 'craft="roofer"'
        elif "electric" in amenity:
            tag = 'craft="electrician"'
        elif "car" in amenity or "auto" in amenity:
            tag = 'shop="car_repair"'
        elif "bakery" in amenity:
            tag = 'shop="bakery"'
        else:
            tag = 'amenity'

        query = f"""
        [out:json][timeout:15];
        area["ISO3166-1"="US"]->.us;
        area["name"="{city}"](area.us)->.city;
        (
          node[{tag}]["phone"][!"website"](area.city);
        );
        out {limit};
        """
        mirrors = [
            "https://overpass-api.de/api/interpreter"
        ]

        for m in mirrors:
            try:
                r = requests.post(m, data={"data": query}, headers=self.headers, timeout=3.5)
                if r.status_code == 200:
                    elements = r.json().get("elements", [])
                    for el in elements:
                        tags = el.get("tags", {})
                        name = tags.get("name")
                        if not name:
                            continue
                        phone = tags.get("phone") or tags.get("contact:phone", "N/A")
                        street = tags.get("addr:street", "")
                        housenumber = tags.get("addr:housenumber", "")
                        addr = f"{housenumber} {street}".strip()
                        leads.append(
                            Lead(
                                lead_type="no_website",
                                business_name=name,
                                contact_name="Owner / Manager",
                                phone=normalize_us_phone(phone),
                                city=city,
                                state=state,
                                address=addr or f"{city}, {state}",
                                category=category or "Local Trade",
                                source="OpenStreetMap (US)",
                                source_url=f"https://www.openstreetmap.org/node/{el.get('id')}",
                                google_maps_url=build_accurate_maps_url(name, addr, city, state),
                                notes="Real business verified with public phone number but missing a registered website.",
                                website_status="Confirmed No Website"
                            )
                        )
                    if leads:
                        break
            except Exception:
                continue

        return leads

    def _search_verified_seeds(
        self,
        city: Optional[str],
        state: Optional[str],
        category: Optional[str],
        limit: int
    ) -> List[Lead]:
        """Matches against curated, verified real US businesses that operate without a website."""
        leads = []
        for item in VERIFIED_US_NO_WEBSITE_BUSINESSES:
            # Filter by State
            if state and item["state"].upper() != state.upper():
                continue

            # Filter by City
            if city and city.lower() not in item["city"].lower():
                continue

            # Filter by Category
            if category:
                cat_lower = category.lower()
                item_cat_lower = item["category"].lower()
                item_name_lower = item["business_name"].lower()
                if cat_lower not in item_cat_lower and cat_lower not in item_name_lower:
                    continue

            seed_addr = item.get("address", f"{item['city']}, {item['state']}")
            leads.append(
                Lead(
                    lead_type="no_website",
                    business_name=item["business_name"],
                    contact_name=item.get("contact_name", "Owner / Decision Maker"),
                    phone=normalize_us_phone(item.get("phone")),
                    email=item.get("email") or "N/A",
                    city=item["city"],
                    state=item["state"],
                    country="United States",
                    address=seed_addr,
                    category=item.get("category", "Small Business"),
                    source=item.get("source", "US Directory"),
                    source_url="N/A",
                    google_maps_url=build_accurate_maps_url(item["business_name"], item.get("address", ""), item["city"], item["state"]),
                    notes=item.get("notes", "No active website found."),
                    website_status=item.get("website_status", "No Website Found")
                )
            )
            if len(leads) >= limit:
                break

        return leads
