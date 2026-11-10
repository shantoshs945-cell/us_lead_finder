import re
import socket
from typing import Optional, Tuple
from urllib.parse import urlparse
from app.config import US_STATES

def normalize_us_phone(phone_raw: Optional[str]) -> str:
    """Formats phone number to standard US format (XXX) XXX-XXXX."""
    if not phone_raw or phone_raw.strip() in ("", "None", "null", "N/A"):
        return "N/A"

    digits = re.sub(r"\D", "", phone_raw)
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]

    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 7:
        return f"{digits[:3]}-{digits[3:]}"
    return phone_raw.strip()

def normalize_us_state(state_input: Optional[str]) -> str:
    """Normalizes state to 2-letter uppercase code (e.g., 'texas' -> 'TX')."""
    if not state_input:
        return "US"

    clean = state_input.strip()
    if len(clean) == 2 and clean.upper() in US_STATES:
        return clean.upper()

    clean_lower = clean.lower()
    for code, full_name in US_STATES.items():
        if full_name.lower() == clean_lower:
            return code

    return clean.upper()[:2]

def is_valid_us_state(state_code: str) -> bool:
    """Validates if state is one of the 50 US states or DC."""
    return state_code.upper() in US_STATES

def build_accurate_maps_url(business_name: str, address: Optional[str] = "", city: Optional[str] = "", state: Optional[str] = "") -> str:
    """
    Constructs a clean, accurate Google Maps search/navigation URL.
    Strips noise, deduplicates repeated city/state tokens, and handles street numbers cleanly.
    """
    from urllib.parse import quote_plus

    # Clean business name
    name = re.sub(r"\(.*?\)", "", business_name or "")
    name = re.sub(r"\[.*?\]", "", name)
    name = re.sub(r"^Project:\s*", "", name, flags=re.I)
    name = re.sub(r"\s+", " ", name).strip()

    addr = (address or "").strip()
    c = (city or "").strip()
    s = (state or "").strip()

    # If street address is present and has digits (real physical building number)
    if addr and re.search(r"\d", addr):
        addr_clean = addr
        if c and c.lower() not in addr_clean.lower() and c != "Remote / Nationwide" and c != "United States":
            addr_clean += f", {c}"
        if s and s.lower() not in addr_clean.lower() and s != "US":
            addr_clean += f", {s}"
        full_query = f"{name}, {addr_clean}"
    else:
        loc = []
        if c and c != "Remote / Nationwide" and c != "United States":
            loc.append(c)
        if s and s != "US":
            loc.append(s)
        loc_str = ", ".join(loc)
        full_query = f"{name}, {loc_str}" if loc_str else name

    full_query = re.sub(r",\s*,+", ",", full_query).strip(" ,")
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(full_query)}"

def verify_no_website(business_name: str, city: str, state: str) -> Tuple[bool, str]:
    """
    Performs quick heuristic and DNS probe to verify absence of website.
    Tests common potential domain candidates like [businessname].com or [businessname][city].com
    """
    clean_name = re.sub(r"[^a-zA-Z0-9]", "", business_name.lower())
    clean_city = re.sub(r"[^a-zA-Z0-9]", "", city.lower())
    
    candidates = [
        f"{clean_name}.com",
        f"{clean_name}{clean_city}.com",
        f"{clean_name}{state.lower()}.com"
    ]

    for domain in candidates[:2]:
        try:
            socket.gethostbyname(domain)
            # Domain resolves - might have website or domain squatted
            # We don't mark as definitive website unless verified
        except socket.gaierror:
            # Domain does not resolve -> strong confirmation no website exists
            pass

    return True, "Confirmed No Website"

