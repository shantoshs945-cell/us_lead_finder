import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from app.config import CSV_PATH, EXCEL_PATH, load_settings
from app.models import Lead
from app.storage.database import get_leads

SHEET_COLUMNS = [
    "Lead ID",
    "Type",
    "Business / Project",
    "Contact Person",
    "Phone Number",
    "Email Address",
    "City",
    "State",
    "Country",
    "Full Address",
    "Google Maps Link",
    "Industry / Category",
    "Website Status",
    "Lead Source",
    "Source URL",
    "Notes / Request Details",
    "Outreach Status",
    "Date Found"
]

def export_to_csv(leads: Optional[List[Lead]] = None, filepath: Path = CSV_PATH) -> str:
    """Exports all or given leads to a CSV file (encoded with utf-8-sig for Excel/Google Sheets compatibility)."""
    if leads is None:
        leads = get_leads(limit=10000)

    rows = [l.to_sheet_row() for l in leads]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SHEET_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    return str(filepath)

def export_to_excel(leads: Optional[List[Lead]] = None, filepath: Path = EXCEL_PATH) -> str:
    """Exports leads to a professionally styled Excel spreadsheet (.xlsx)."""
    if leads is None:
        leads = get_leads(limit=10000)

    rows = [l.to_sheet_row() for l in leads]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "US Leads"

    # Header styling
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark blue
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Thin borders
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )

    # Write headers
    for col_num, col_name in enumerate(SHEET_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_num, value=col_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    # Alternate row colors
    alt_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    regular_font = Font(name="Calibri", size=10)

    # Status formatting colors
    status_colors = {
        "New": "E0F2FE",          # Soft blue
        "Contacted": "FEF3C7",    # Soft yellow
        "Follow Up": "FFEDD5",    # Soft orange
        "Meeting Booked": "DCFCE7",# Soft green
        "Won": "86EFAC",          # Bright green
        "Archived": "F3F4F6"      # Soft gray
    }

    type_colors = {
        "No Website": "FEE2E2",          # Soft red/rose (Opportunity!)
        "Looking for Website": "DCFCE7"  # Soft green (High intent!)
    }

    for row_idx, r in enumerate(rows, 2):
        is_even = (row_idx % 2 == 0)
        ws.row_dimensions[row_idx].height = 22

        for col_idx, col_name in enumerate(SHEET_COLUMNS, 1):
            val = r.get(col_name, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=val)
            cell.font = regular_font
            cell.border = thin_border
            cell.alignment = Alignment(vertical="center")

            # Apply alternating fill
            if is_even:
                cell.fill = alt_fill

            # Highlight status column
            if col_name == "Outreach Status" and val in status_colors:
                cell.fill = PatternFill(start_color=status_colors[val], fill_type="solid")
                cell.font = Font(name="Calibri", size=10, bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Highlight Type column
            if col_name == "Type" and val in type_colors:
                cell.fill = PatternFill(start_color=type_colors[val], fill_type="solid")
                cell.font = Font(name="Calibri", size=10, bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Link URLs (Source URL & Google Maps Link)
            if col_name in ("Source URL", "Google Maps Link") and val and str(val).startswith("http"):
                cell.hyperlink = val
                cell.font = Font(name="Calibri", size=10, color="2563EB", underline="single")

    # Auto-adjust column widths
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        # Cap width between 12 and 45
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    # Freeze header row
    ws.freeze_panes = "A2"

    wb.save(filepath)
    return str(filepath)

def sync_sheets(leads: Optional[List[Lead]] = None) -> Dict[str, Any]:
    """Generates and updates CSV, Excel, and JSON sheets."""
    if leads is None:
        leads = get_leads(limit=10000)

    csv_path = export_to_csv(leads)
    excel_path = export_to_excel(leads)

    # Also sync leads.json for GitHub Pages static hosting
    json_path = Path(csv_path).parent / "leads.json"
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([l.model_dump() for l in leads], f, indent=2)
    except Exception:
        pass

    settings = load_settings()
    webhook_url = settings.get("google_sheets_webhook_url")
    google_sync_result = None

    if webhook_url:
        google_sync_result = push_to_google_sheet_webhook(leads, webhook_url)

    return {
        "csv_path": csv_path,
        "excel_path": excel_path,
        "total_records": len(leads),
        "google_sheets_synced": bool(webhook_url),
        "google_sync_status": google_sync_result
    }

def push_to_google_sheet_webhook(leads: List[Lead], webhook_url: str) -> Dict[str, Any]:
    """
    Sends leads data to a Google Apps Script Webhook.
    User's Google Apps Script receives the JSON payload and appends rows to their Google Sheet.
    """
    try:
        payload = {
            "columns": SHEET_COLUMNS,
            "leads": [l.to_sheet_row() for l in leads]
        }
        r = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        return {
            "success": r.status_code in (200, 201, 302),
            "status_code": r.status_code,
            "response": r.text[:200]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

GOOGLE_APPS_SCRIPT_TEMPLATE = """
/**
 * GOOGLE APPS SCRIPT FOR 1-CLICK SHEET SYNC
 * Instructions:
 * 1. In your Google Sheet, click Extensions > Apps Script
 * 2. Delete existing code and paste this script
 * 3. Click Deploy > New deployment > Select 'Web app'
 * 4. Set 'Execute as: Me' and 'Who has access: Anyone'
 * 5. Copy the Web App URL and paste it into the Lead Finder settings!
 */
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    var leads = data.leads;
    var columns = data.columns;
    
    // Setup headers if sheet is empty
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(columns);
      sheet.getRange(1, 1, 1, columns.length).setFontWeight("bold").setBackground("#1E3A8A").setFontColor("#FFFFFF");
      sheet.setFrozenRows(1);
    }
    
    // Append rows
    for (var i = 0; i < leads.length; i++) {
      var lead = leads[i];
      var row = [];
      for (var j = 0; j < columns.length; j++) {
        row.push(lead[columns[j]] || "");
      }
      sheet.appendRow(row);
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: "success", count: leads.length}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
"""

