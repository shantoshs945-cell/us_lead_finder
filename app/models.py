from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from urllib.parse import quote_plus
import uuid

LeadType = Literal["no_website", "seeking_website"]
LeadStatus = Literal["New", "Contacted", "Follow Up", "Meeting Booked", "Won", "Archived"]

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    lead_type: LeadType
    business_name: str
    contact_name: Optional[str] = "Owner / Decision Maker"
    phone: Optional[str] = "N/A"
    email: Optional[str] = "N/A"
    city: str
    state: str
    country: str = "United States"
    address: Optional[str] = ""
    category: str = "General"
    source: str
    source_url: Optional[str] = ""
    google_maps_url: Optional[str] = ""
    notes: Optional[str] = ""
    website_status: str = "No Website"
    status: LeadStatus = "New"
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def get_google_maps_url(self) -> str:
        """Returns explicitly set google_maps_url or auto-generates a valid Google Maps search URL."""
        if self.google_maps_url and self.google_maps_url.strip():
            return self.google_maps_url
        parts = [self.business_name]
        if self.address and self.address.strip():
            parts.append(self.address)
        if self.city and self.city.strip():
            parts.append(self.city)
        if self.state and self.state.strip():
            parts.append(self.state)
        query = " ".join(parts).strip()
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"

    def to_sheet_row(self) -> dict:
        """Flattens lead for spreadsheet display and CSV/Excel export."""
        return {
            "Lead ID": self.id,
            "Type": "No Website" if self.lead_type == "no_website" else "Looking for Website",
            "Business / Project": self.business_name,
            "Contact Person": self.contact_name or "N/A",
            "Phone Number": self.phone or "N/A",
            "Email Address": self.email or "N/A",
            "City": self.city,
            "State": self.state,
            "Country": self.country,
            "Full Address": self.address or f"{self.city}, {self.state}",
            "Google Maps Link": self.get_google_maps_url(),
            "Industry / Category": self.category,
            "Website Status": self.website_status,
            "Lead Source": self.source,
            "Source URL": self.source_url or "N/A",
            "Notes / Request Details": self.notes or "",
            "Outreach Status": self.status,
            "Date Found": self.created_at
        }

class LeadSearchParams(BaseModel):
    lead_type: Optional[LeadType] = None
    city: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[str] = None
    limit: int = 15

class StatusUpdateRequest(BaseModel):
    status: LeadStatus

class GoogleSheetSyncRequest(BaseModel):
    webhook_url: Optional[str] = None

