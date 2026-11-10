import sqlite3
from typing import List, Optional, Dict, Any
from pathlib import Path
from app.config import DB_PATH
from app.models import Lead, LeadStatus, LeadType

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                lead_type TEXT NOT NULL,
                business_name TEXT NOT NULL,
                contact_name TEXT,
                phone TEXT,
                email TEXT,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                country TEXT DEFAULT 'United States',
                address TEXT,
                category TEXT,
                source TEXT NOT NULL,
                source_url TEXT,
                google_maps_url TEXT,
                notes TEXT,
                website_status TEXT,
                status TEXT DEFAULT 'New',
                created_at TEXT NOT NULL,
                dedup_key TEXT UNIQUE
            )
        """)
        # Auto-migrate if column missing in existing db
        cursor.execute("PRAGMA table_info(leads)")
        col_names = [col[1] for col in cursor.fetchall()]
        if "google_maps_url" not in col_names:
            cursor.execute("ALTER TABLE leads ADD COLUMN google_maps_url TEXT DEFAULT ''")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_type ON leads(lead_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_state ON leads(state)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        conn.commit()

def make_dedup_key(lead: Lead) -> str:
    """Generate a unique fingerprint for a lead to avoid duplicates."""
    clean_name = "".join(filter(str.isalnum, lead.business_name.lower()))
    clean_phone = "".join(filter(str.isdigit, lead.phone or ""))
    clean_city = "".join(filter(str.isalnum, lead.city.lower()))
    
    if lead.source_url and "reddit" in lead.source.lower():
        return f"url:{lead.source_url}"
    if clean_phone and len(clean_phone) >= 7:
        return f"phone:{clean_phone}"
    return f"name_city:{clean_name}_{clean_city}_{lead.state.lower()}"

def insert_lead(lead: Lead) -> bool:
    """Insert a single lead, ignoring if duplicate exists. Returns True if inserted."""
    dedup_key = make_dedup_key(lead)
    maps_url = lead.get_google_maps_url()
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO leads (
                    id, lead_type, business_name, contact_name, phone, email,
                    city, state, country, address, category, source, source_url,
                    google_maps_url, notes, website_status, status, created_at, dedup_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.id, lead.lead_type, lead.business_name, lead.contact_name,
                lead.phone, lead.email, lead.city, lead.state, lead.country,
                lead.address, lead.category, lead.source, lead.source_url,
                maps_url, lead.notes, lead.website_status, lead.status, lead.created_at,
                dedup_key
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate lead
            return False

def insert_leads(leads: List[Lead]) -> int:
    """Inserts a batch of leads, returns count of newly added leads."""
    added = 0
    for l in leads:
        if insert_lead(l):
            added += 1
    return added

def get_leads(
    lead_type: Optional[LeadType] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[LeadStatus] = None,
    search_query: Optional[str] = None,
    limit: int = 500,
    offset: int = 0
) -> List[Lead]:
    query = "SELECT * FROM leads WHERE 1=1"
    params: List[Any] = []

    if lead_type:
        query += " AND lead_type = ?"
        params.append(lead_type)
    if state:
        query += " AND UPPER(state) = UPPER(?)"
        params.append(state)
    if city:
        query += " AND LOWER(city) LIKE LOWER(?)"
        params.append(f"%{city}%")
    if category:
        query += " AND LOWER(category) LIKE LOWER(?)"
        params.append(f"%{category}%")
    if status:
        query += " AND status = ?"
        params.append(status)
    if search_query:
        query += " AND (LOWER(business_name) LIKE LOWER(?) OR LOWER(notes) LIKE LOWER(?) OR LOWER(contact_name) LIKE LOWER(?))"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard, wildcard])

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            Lead(
                id=r["id"],
                lead_type=r["lead_type"],
                business_name=r["business_name"],
                contact_name=r["contact_name"],
                phone=r["phone"],
                email=r["email"],
                city=r["city"],
                state=r["state"],
                country=r["country"],
                address=r["address"],
                category=r["category"],
                source=r["source"],
                source_url=r["source_url"],
                google_maps_url=r["google_maps_url"] if "google_maps_url" in r.keys() and r["google_maps_url"] else "",
                notes=r["notes"],
                website_status=r["website_status"],
                status=r["status"],
                created_at=r["created_at"]
            )
            for r in rows
        ]

def get_lead_by_id(lead_id: str) -> Optional[Lead]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        r = cursor.fetchone()
        if not r:
            return None
        return Lead(
            id=r["id"],
            lead_type=r["lead_type"],
            business_name=r["business_name"],
            contact_name=r["contact_name"],
            phone=r["phone"],
            email=r["email"],
            city=r["city"],
            state=r["state"],
            country=r["country"],
            address=r["address"],
            category=r["category"],
            source=r["source"],
            source_url=r["source_url"],
            google_maps_url=r["google_maps_url"] if "google_maps_url" in r.keys() and r["google_maps_url"] else "",
            notes=r["notes"],
            website_status=r["website_status"],
            status=r["status"],
            created_at=r["created_at"]
        )

def update_lead_status(lead_id: str, new_status: LeadStatus) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id))
        conn.commit()
        return cursor.rowcount > 0

def delete_lead(lead_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_stats() -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM leads")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'no_website'")
        no_website = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM leads WHERE lead_type = 'seeking_website'")
        seeking_website = cursor.fetchone()[0]

        cursor.execute("SELECT state, COUNT(*) as count FROM leads GROUP BY state ORDER BY count DESC LIMIT 5")
        top_states = [{"state": r[0], "count": r[1]} for r in cursor.fetchall()]

        cursor.execute("SELECT status, COUNT(*) as count FROM leads GROUP BY status")
        status_breakdown = {r[0]: r[1] for r in cursor.fetchall()}

        return {
            "total_leads": total,
            "no_website_leads": no_website,
            "seeking_website_leads": seeking_website,
            "top_states": top_states,
            "status_breakdown": status_breakdown
        }

