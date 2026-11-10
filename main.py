import argparse
import sys
import uvicorn
from typing import Optional

from app.storage.database import init_db, insert_leads, get_leads, get_stats
from app.storage.sheet_manager import sync_sheets, export_to_csv, export_to_excel
from app.finders.no_website_finder import NoWebsiteFinder
from app.finders.seeking_website_finder import SeekingWebsiteFinder
from app.outreach.generator import generate_pitch
from app.scheduler.runner import run_lead_generation_cycle, run_continuous_scheduler
from app.config import CSV_PATH, EXCEL_PATH

def cmd_web(args):
    """Launch the interactive web dashboard."""
    port = args.port or 8000
    host = args.host or "127.0.0.1"
    print(f"\n=======================================================")
    print(f"🚀 Launching US Lead Finder Web Dashboard...")
    print(f"📍 Local Web App: http://{host}:{port}")
    print(f"📊 Auto-syncing: leads.csv & leads.xlsx")
    print(f"=======================================================\n")
    uvicorn.run("app.web.server:app", host=host, port=port, reload=False)

def cmd_find_no_website(args):
    """Search for US businesses that do not have a website."""
    init_db()
    finder = NoWebsiteFinder()
    print(f"\n🔎 Searching US businesses without a website...")
    print(f"   State: {args.state or 'All US'}")
    print(f"   City: {args.city or 'All Cities'}")
    print(f"   Category: {args.category or 'All Services'}")
    print(f"   Limit: {args.limit}")

    leads = finder.search(
        city=args.city,
        state=args.state,
        category=args.category,
        limit=args.limit
    )

    new_count = insert_leads(leads)
    sync_result = sync_sheets()

    print(f"\n✅ Found {len(leads)} businesses without a website ({new_count} new saved).")
    print(f"📁 Updated CSV Sheet: {sync_result['csv_path']}")
    print(f"📁 Updated Excel Sheet: {sync_result['excel_path']}")

    print("\nSample Discovered Leads:")
    for i, l in enumerate(leads[:5], 1):
        print(f" {i}. {l.business_name} ({l.city}, {l.state})")
        print(f"    📞 Phone: {l.phone} | 🏢 Category: {l.category}")
        print(f"    📍 Address: {l.address or 'N/A'}")
        print(f"    ⚠️  Status: {l.website_status}")
        print()

def cmd_find_seeking_website(args):
    """Search for US people/clients looking for a website."""
    init_db()
    finder = SeekingWebsiteFinder()
    print(f"\n📡 Scanning for US clients looking for a website...")
    print(f"   Keywords: {args.keywords}")
    print(f"   Limit: {args.limit}")

    leads = finder.search(
        keywords=args.keywords,
        city=args.city,
        state=args.state,
        category=args.category,
        limit=args.limit
    )

    new_count = insert_leads(leads)
    sync_result = sync_sheets()

    print(f"\n✅ Found {len(leads)} in-market requests ({new_count} new saved).")
    print(f"📁 Updated CSV Sheet: {sync_result['csv_path']}")
    print(f"📁 Updated Excel Sheet: {sync_result['excel_path']}")

    print("\nSample Discovered Leads:")
    for i, l in enumerate(leads[:5], 1):
        print(f" {i}. {l.business_name} ({l.city}, {l.state})")
        print(f"    👤 Contact: {l.contact_name} | ✉️  Email: {l.email}")
        print(f"    🔗 Source: {l.source} ({l.source_url or 'N/A'})")
        print(f"    📝 Note: {l.notes[:100]}...")
        print()

def cmd_export(args):
    """Export stored leads to CSV and/or Excel spreadsheet."""
    init_db()
    leads = get_leads(limit=10000)
    fmt = args.format.lower()
    print(f"\n📊 Exporting {len(leads)} stored leads...")

    if fmt in ("csv", "both"):
        p = export_to_csv(leads)
        print(f"   📄 CSV Sheet created: {p}")
    if fmt in ("excel", "xlsx", "both"):
        p = export_to_excel(leads)
        print(f"   📑 Excel Sheet (.xlsx) created: {p}")

    print("✅ Export complete!")

def cmd_list(args):
    """List stored leads."""
    init_db()
    leads = get_leads(lead_type=args.type, limit=args.limit)
    print(f"\n--- Stored Leads ({len(leads)}) ---")
    for l in leads:
        tag = "[NO WEBSITE]" if l.lead_type == "no_website" else "[SEEKING SITE]"
        print(f"{tag:<16} {l.business_name:<36} | {l.phone:<16} | {l.city}, {l.state:<2} | {l.status}")

def cmd_status(args):
    """Print lead finder database statistics."""
    init_db()
    stats = get_stats()
    print("\n--- US Lead Finder Stats ---")
    print(f" Total Leads in Sheet:       {stats['total_leads']}")
    print(f" Businesses with No Website: {stats['no_website_leads']}")
    print(f" People Seeking a Website:   {stats['seeking_website_leads']}")
    print("\nTop US States:")
    for s in stats["top_states"]:
        print(f"  - {s['state']}: {s['count']} leads")
    print("\nOutreach Status Breakdown:")
    for st, c in stats["status_breakdown"].items():
        print(f"  - {st}: {c}")

def cmd_auto_find(args):
    """Run an automated lead discovery cycle or standing scheduler."""
    init_db()
    if args.continuous:
        run_continuous_scheduler(interval_hours=args.interval)
    else:
        print("\n⚡ Running automated lead generation cycle across US metros...")
        added = run_lead_generation_cycle()
        print(f"✅ Cycle complete. Added {added} fresh leads to leads.csv and leads.xlsx.")

def main():
    parser = argparse.ArgumentParser(description="US Lead Finder - Web Design & Development Clients")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # web
    p_web = subparsers.add_parser("web", help="Start the interactive web dashboard")
    p_web.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    p_web.add_argument("--host", type=str, default="127.0.0.1", help="Web server host")

    # find-no-website
    p_noweb = subparsers.add_parser("find-no-website", help="Find US businesses that don't have a website")
    p_noweb.add_argument("--state", type=str, help="US state code (e.g. TX, CA, NY)")
    p_noweb.add_argument("--city", type=str, help="US city name (e.g. Austin, Dallas, Miami)")
    p_noweb.add_argument("--category", type=str, help="Business category (e.g. plumber, roofing, bakery)")
    p_noweb.add_argument("--limit", type=int, default=15, help="Number of leads to fetch")

    # find-seeking-website
    p_seek = subparsers.add_parser("find-seeking-website", help="Find people looking for a website in the US")
    p_seek.add_argument("--keywords", type=str, default="need a website", help="Intent keywords")
    p_seek.add_argument("--state", type=str, help="US state code")
    p_seek.add_argument("--city", type=str, help="US city name")
    p_seek.add_argument("--category", type=str, help="Category filter")
    p_seek.add_argument("--limit", type=int, default=15, help="Number of leads to fetch")

    # export
    p_exp = subparsers.add_parser("export", help="Export leads to CSV or Excel sheet")
    p_exp.add_argument("--format", choices=["csv", "excel", "both"], default="both", help="Export format")

    # list
    p_list = subparsers.add_parser("list", help="List stored leads")
    p_list.add_argument("--type", choices=["no_website", "seeking_website"], help="Filter by lead type")
    p_list.add_argument("--limit", type=int, default=25, help="Limit output")

    # status
    subparsers.add_parser("status", help="Show summary metrics")

    # auto-find
    p_auto = subparsers.add_parser("auto-find", help="Run automated discovery cycle across US")
    p_auto.add_argument("--continuous", action="store_true", help="Keep running periodically in background")
    p_auto.add_argument("--interval", type=int, default=6, help="Hours between cycles if continuous (default: 6)")

    args = parser.parse_args()

    if not args.command:
        # Default behavior if no argument given is to launch web UI
        args.port = 8000
        args.host = "127.0.0.1"
        cmd_web(args)
        return

    commands = {
        "web": cmd_web,
        "find-no-website": cmd_find_no_website,
        "find-seeking-website": cmd_find_seeking_website,
        "export": cmd_export,
        "list": cmd_list,
        "status": cmd_status,
        "auto-find": cmd_auto_find
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
