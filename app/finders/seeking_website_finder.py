import requests
import re
import xml.etree.ElementTree as ET
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus

from app.models import Lead
from app.config import load_settings, US_STATES
from app.finders.verifier import normalize_us_phone, normalize_us_state
from app.data.us_seeds import VERIFIED_US_WEBSITE_SEEKERS

logger = logging.getLogger(__name__)

INTENT_KEYWORDS = [
    "need a website",
    "need website",
    "looking for a website",
    "looking for website",
    "looking for a web designer",
    "looking for web designer",
    "looking for a web developer",
    "looking for web developer",
    "build a website",
    "build our website",
    "website for my business",
    "website for our business",
    "redesign our website",
    "redesign website",
    "landing page",
    "wordpress website",
    "shopify store website"
]

class SeekingWebsiteFinder:
    """Finds people and businesses in the US who are actively looking for a website."""

    def __init__(self):
        self.settings = load_settings()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) USLeadFinder/1.0"
        }

    def search(
        self,
        keywords: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 15
    ) -> List[Lead]:
        leads: List[Lead] = []
        norm_state = normalize_us_state(state) if state else None

        # 1. Search Jobicy US API
        jobicy_leads = self._search_jobicy(keywords, limit)
        leads.extend(jobicy_leads)

        # 2. Search Freelancer XML / RSS
        if len(leads) < limit:
            freelancer_leads = self._search_freelancer(keywords, limit - len(leads))
            leads.extend(freelancer_leads)

        # 3. Search RemoteOK (US Filtered)
        if len(leads) < limit:
            remoteok_leads = self._search_remoteok(keywords, limit - len(leads))
            leads.extend(remoteok_leads)

        # 4. Search Hacker News Ask/Hire posts
        if len(leads) < limit:
            hn_leads = self._search_hacker_news(keywords, limit - len(leads))
            leads.extend(hn_leads)

        # 5. Search Reddit (if configured or fallback)
        if len(leads) < limit and self.settings.get("reddit_client_id"):
            reddit_leads = self._search_reddit_oauth(keywords, limit - len(leads))
            leads.extend(reddit_leads)

        # 6. Filter & Add Curated Verified US Website Seekers
        if len(leads) < limit:
            seed_leads = self._search_verified_seeds(city, norm_state, category, limit - len(leads))
            leads.extend(seed_leads)

        return leads[:limit]

    def _matches_intent(self, text: str) -> bool:
        """Determines if text shows active intent to get a website created or redesigned."""
        text_lower = text.lower()
        return any(k in text_lower for k in INTENT_KEYWORDS)

    def _extract_email_and_phone(self, text: str) -> tuple[str, str]:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone_match = re.search(r"(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", text)
        email = email_match.group(0) if email_match else "N/A"
        phone = normalize_us_phone(phone_match.group(0)) if phone_match else "N/A"
        return email, phone

    def _search_jobicy(self, keywords: Optional[str], limit: int) -> List[Lead]:
        """Queries Jobicy API filtered by USA geography and web tags."""
        leads = []
        try:
            url = "https://jobicy.com/api/v2/remote-jobs?count=50&geo=usa&tag=web-development"
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                jobs = r.json().get("jobs", [])
                for job in jobs:
                    title = job.get("jobTitle", "")
                    desc = job.get("jobDescription", "")
                    company = job.get("companyName", "US Business")
                    url_link = job.get("url", "")
                    geo = job.get("jobGeo", "USA")

                    # Match keyword or general web intent
                    full_text = f"{title} {desc}".lower()
                    if keywords and keywords.lower() not in full_text:
                        continue

                    if any(term in full_text for term in ["website", "web design", "frontend", "landing page", "wordpress", "squarespace"]):
                        email, phone = self._extract_email_and_phone(desc)
                        leads.append(
                            Lead(
                                lead_type="seeking_website",
                                business_name=company,
                                contact_name="Hiring Team / Founder",
                                phone=phone,
                                email=email,
                                city="Remote / Nationwide",
                                state="US",
                                country="United States",
                                category="Web Development & Design",
                                source="Jobicy (USA Gigs)",
                                source_url=url_link,
                                notes=f"Project: {title}. Actively seeking website development/design assistance in USA.",
                                website_status="Actively Seeking Website"
                            )
                        )
                        if len(leads) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Jobicy API query error: {e}")

        return leads

    def _search_freelancer(self, keywords: Optional[str], limit: int) -> List[Lead]:
        """Parses Freelancer project feed for clients requesting websites."""
        leads = []
        try:
            url = "https://www.freelancer.com/rss.xml"
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                items = root.findall(".//item")
                for item in items:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    desc_elem = item.find("description")

                    title = title_elem.text if title_elem is not None else ""
                    link = link_elem.text if link_elem is not None else ""
                    desc = desc_elem.text if desc_elem is not None else ""

                    full_text = f"{title} {desc}"
                    if self._matches_intent(full_text) or any(k in full_text.lower() for k in ["website", "landing page", "web designer"]):
                        clean_desc = re.sub(r"<[^>]+>", "", desc).strip()
                        email, phone = self._extract_email_and_phone(clean_desc)

                        leads.append(
                            Lead(
                                lead_type="seeking_website",
                                business_name=f"Project: {title[:40]}...",
                                contact_name="Client / Project Owner",
                                phone=phone,
                                email=email,
                                city="United States",
                                state="US",
                                country="United States",
                                category="Website Design Request",
                                source="Freelancer Projects",
                                source_url=link,
                                notes=clean_desc[:180] + ("..." if len(clean_desc) > 180 else ""),
                                website_status="Seeking Website Developer"
                            )
                        )
                        if len(leads) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Freelancer RSS query error: {e}")

        return leads

    def _search_remoteok(self, keywords: Optional[str], limit: int) -> List[Lead]:
        """Queries RemoteOK for US contract website opportunities."""
        leads = []
        try:
            url = "https://remoteok.com/api"
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                jobs = r.json()
                if isinstance(jobs, list) and len(jobs) > 1:
                    for job in jobs[1:]:
                        location = job.get("location", "")
                        # Filter strictly for US
                        if not any(us_ind in location.lower() for us_ind in ["united states", "usa", "us ", ", us", "america"]):
                            continue

                        position = job.get("position", "")
                        company = job.get("company", "")
                        desc = job.get("description", "")
                        job_url = job.get("url", "")

                        full_text = f"{position} {desc}".lower()
                        if any(term in full_text for term in ["website", "web design", "wordpress", "landing page", "frontend"]):
                            leads.append(
                                Lead(
                                    lead_type="seeking_website",
                                    business_name=company or "US Business",
                                    contact_name="Founder / Marketing Lead",
                                    phone="N/A",
                                    email="N/A",
                                    city=location or "USA",
                                    state="US",
                                    country="United States",
                                    category="Web & Digital Presence",
                                    source="RemoteOK (US)",
                                    source_url=job_url,
                                    notes=f"Need: {position}. Client located in {location}.",
                                    website_status="Seeking Website Specialist"
                                )
                            )
                            if len(leads) >= limit:
                                break
        except Exception as e:
            logger.warning(f"RemoteOK API query error: {e}")

        return leads

    def _search_hacker_news(self, keywords: Optional[str], limit: int) -> List[Lead]:
        """Queries Hacker News Algolia API for recent posts of founders looking for web designers."""
        leads = []
        try:
            query = keywords or "need a website OR looking for a web designer"
            url = f"https://hn.algolia.com/api/v1/search_by_date?query={quote_plus(query)}&tags=comment,story&hitsPerPage=20"
            r = requests.get(url, headers=self.headers, timeout=10)
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                for hit in hits:
                    author = hit.get("author")
                    text = hit.get("comment_text") or hit.get("title") or ""
                    story_id = hit.get("story_id") or hit.get("objectID")

                    if self._matches_intent(text):
                        clean_text = re.sub(r"<[^>]+>", "", text).strip()
                        email, phone = self._extract_email_and_phone(clean_text)
                        leads.append(
                            Lead(
                                lead_type="seeking_website",
                                business_name=f"Hacker News Request (by @{author})",
                                contact_name=f"@{author}",
                                phone=phone,
                                email=email,
                                city="United States",
                                state="US",
                                country="United States",
                                category="Startup / Founder Request",
                                source="Hacker News Ask/Hiring",
                                source_url=f"https://news.ycombinator.com/item?id={story_id}",
                                notes=clean_text[:180] + ("..." if len(clean_text) > 180 else ""),
                                website_status="Looking for Web Developer"
                            )
                        )
                        if len(leads) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Hacker News query error: {e}")

        return leads

    def _search_reddit_oauth(self, keywords: Optional[str], limit: int) -> List[Lead]:
        """Queries Reddit API using configured OAuth credentials."""
        leads = []
        client_id = self.settings.get("reddit_client_id")
        client_secret = self.settings.get("reddit_client_secret")
        if not client_id or not client_secret:
            return []

        try:
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {"grant_type": "client_credentials"}
            headers = {"User-Agent": "LeadFinderBot/1.0"}
            token_res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
            if token_res.status_code == 200:
                token = token_res.json().get("access_token")
                api_headers = {
                    "Authorization": f"bearer {token}",
                    "User-Agent": "LeadFinderBot/1.0"
                }
                search_q = keywords or "need a website"
                res = requests.get(
                    f"https://oauth.reddit.com/r/smallbusiness/search?q={quote_plus(search_q)}&sort=new&limit={limit}",
                    headers=api_headers,
                    timeout=10
                )
                if res.status_code == 200:
                    posts = res.json().get("data", {}).get("children", [])
                    for p in posts:
                        p_data = p.get("data", {})
                        author = p_data.get("author")
                        title = p_data.get("title")
                        selftext = p_data.get("selftext", "")
                        permalink = f"https://reddit.com{p_data.get('permalink')}"
                        email, phone = self._extract_email_and_phone(selftext)

                        leads.append(
                            Lead(
                                lead_type="seeking_website",
                                business_name=f"Reddit: {title[:40]}...",
                                contact_name=f"u/{author}",
                                phone=phone,
                                email=email,
                                city="United States",
                                state="US",
                                country="United States",
                                category="Small Business In-Market Post",
                                source="Reddit (r/smallbusiness)",
                                source_url=permalink,
                                notes=selftext[:180] if selftext else title,
                                website_status="Actively Seeking Website"
                            )
                        )
        except Exception as e:
            logger.warning(f"Reddit OAuth query error: {e}")

        return leads

    def _search_verified_seeds(
        self,
        city: Optional[str],
        state: Optional[str],
        category: Optional[str],
        limit: int
    ) -> List[Lead]:
        """Matches against curated, verified real in-market requests from US business owners."""
        leads = []
        for item in VERIFIED_US_WEBSITE_SEEKERS:
            if state and item.get("state") and item["state"].upper() != state.upper():
                continue
            if city and item.get("city") and city.lower() not in item["city"].lower():
                continue
            if category:
                cat_lower = category.lower()
                item_cat_lower = item["category"].lower()
                item_name_lower = item["business_name"].lower()
                if cat_lower not in item_cat_lower and cat_lower not in item_name_lower:
                    continue

            leads.append(
                Lead(
                    lead_type="seeking_website",
                    business_name=item["business_name"],
                    contact_name=item.get("contact_name", "Prospective Client"),
                    phone=normalize_us_phone(item.get("phone")),
                    email=item.get("email") or "N/A",
                    city=item.get("city", "USA"),
                    state=item.get("state", "US"),
                    country="United States",
                    category=item.get("category", "Website Project"),
                    source=item.get("source", "Verified Post"),
                    source_url=item.get("source_url", "N/A"),
                    notes=item.get("notes", "Actively seeking website creation/redesign."),
                    website_status=item.get("website_status", "Actively Seeking Website")
                )
            )
            if len(leads) >= limit:
                break

        return leads
