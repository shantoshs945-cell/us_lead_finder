# 🎯 US Lead Finder (Businesses Without Websites & Website Seekers)

An automated lead generation tool built specifically for web designers, developers, and digital marketing agencies. It identifies high-value leads across the **United States (US only)** and automatically stores them in a spreadsheet (**CSV**, styled **Excel .xlsx**, and live cloud **Google Sheets**).

---

## 🌟 Core Capabilities

### 1. Find US Businesses That Have No Website
- Scans official US city and state business license registries (NYC Open Data, Chicago Open Data, LA Active Business Registry, Austin, etc.), OpenStreetMap, and business directories.
- Identifies established local businesses operating with verified phone numbers, physical addresses, and trade licenses—but **zero active website**.
- Proves high-converting value: you can reach out with a direct pitch to help them stop losing customers to local competitors.

### 2. Find People & Businesses Actively Looking for a Website
- Scans live gig and job feeds across **Jobicy US**, **Freelancer**, **RemoteOK (US)**, **Hacker News (Ask/Hiring)**, and small business communities.
- Uses natural language intent matching for triggers like `"need a website"`, `"looking for web designer"`, `"build website for my business"`, and `"redesign website"`.
- Extracts contact handles, emails, phone numbers, project requirements, budget, and direct post links.

### 3. Automated Sheet Storage & Synchronization
- **`leads.csv`**: Instant local CSV spreadsheet, formatted in UTF-8-BOM for native opening in Excel & Google Sheets.
- **`leads.xlsx`**: Excel workbook with styled headers, alternating row colors, auto-adjusted column widths, status tags, and clickable links.
- **Google Sheets Cloud Sync**: 1-click real-time sync into your Google Sheet via an Apps Script Webhook.
- **Database & Deduping**: Backed by SQLite to prevent duplicate leads across phone numbers, URLs, and business names.

### 4. Built-in Outreach Pitch Generator
- Generates tailored outreach materials customized specifically for each lead's business name, city, and category:
  - **Cold Email Pitch** (Compelling subject line + value-focused body)
  - **Cold SMS / Text Pitch** (Punchy 2-sentence intro with free mockup offer)
  - **Cold Call Script** (Step-by-step phone opener + objection handling)

### 5. Web Dashboard + CLI
- **Interactive Single-Page Web Dashboard**: Built with Tailwind CSS, live stats, instant filters, search controls, status dropdowns, and download buttons.
- **CLI Tool**: Run quick terminal searches, automated discovery cycles, and exports.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Web Dashboard
```bash
python main.py web
# or simply:
python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 💻 CLI Commands

### 🔍 Find Businesses Without a Website
```bash
# Search by US State, City, and Category
python main.py find-no-website --state TX --city Austin --category plumbing --limit 10

# Search all cities in California
python main.py find-no-website --state CA --category "roofing" --limit 15

# Search Florida contractors
python main.py find-no-website --state FL --category "general contractor"
```

### 📡 Find In-Market Clients Looking for a Website
```bash
# Search live feeds for clients asking for websites
python main.py find-seeking-website --keywords "need a website" --limit 10

# Search for web design requests
python main.py find-seeking-website --keywords "looking for web designer"
```

### ⚡ Run Automated Discovery Cycle Across Top US Metros
```bash
# Run one full multi-city discovery cycle
python main.py auto-find

# Run continuous background worker (e.g., checks every 6 hours)
python main.py auto-find --continuous --interval 6
```

### 📊 Export & List Stored Leads
```bash
# Export to both CSV and styled Excel
python main.py export --format both

# View status summary and statistics
python main.py status

# List leads in terminal
python main.py list --limit 20
```

---

## 📈 Google Sheets 1-Click Sync Setup

You can sync all discovered leads directly into your cloud Google Sheet in real time:

1. Open a blank sheet at **[sheets.new](https://sheets.new)**
2. In Google Sheets menu, click **Extensions > Apps Script**
3. Replace the editor code with this script:
```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    var leads = data.leads;
    var columns = data.columns;
    
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(columns);
      sheet.getRange(1, 1, 1, columns.length).setFontWeight("bold").setBackground("#1E3A8A").setFontColor("#FFFFFF");
      sheet.setFrozenRows(1);
    }
    
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
```
4. Click **Deploy > New deployment > Select 'Web app'**
5. Set:
   - **Execute as**: `Me`
   - **Who has access**: `Anyone`
6. Click **Deploy**, copy your **Web App URL**, and paste it into the **Settings** tab in the Lead Finder dashboard.
7. Click **Test Sync**—all leads will instantly populate your Google Sheet!

---

## 📁 Project Structure

```
new/
├── app/
│   ├── config.py                 # US states, top metro lists, settings
│   ├── models.py                 # Pydantic Lead schema & row mappings
│   ├── storage/
│   │   ├── database.py           # SQLite persistence & deduplication
│   │   └── sheet_manager.py      # leads.csv, leads.xlsx, & Google Sheets sync
│   ├── finders/
│   │   ├── no_website_finder.py  # US businesses without website engine
│   │   ├── seeking_website_finder.py # People looking for website engine
│   │   └── verifier.py           # Phone normalization & domain verifier
│   ├── outreach/
│   │   └── generator.py          # Cold email, SMS, & phone script generator
│   ├── scheduler/
│   │   └── runner.py             # Periodic background automation runner
│   ├── web/
│   │   ├── server.py             # FastAPI backend REST API
│   │   └── templates/
│   │       └── index.html        # Modern Tailwind CSS single-page dashboard
│   └── data/
│       └── us_seeds.py           # Verified US small businesses without websites
├── leads.csv                     # Auto-synced CSV sheet
├── leads.xlsx                    # Auto-synced Excel sheet
├── main.py                       # CLI & web application entrypoint
├── requirements.txt              # Python dependencies
└── README.md                     # Documentation
```

---

## 🔒 US Only Restriction
This lead finder is strictly restricted to the **United States (US only)**:
- Geographic queries target only US cities and the 50 US States + DC.
- State fields validate against standard 2-letter US postal abbreviations (`TX`, `CA`, `FL`, `NY`, etc.).
- Phone numbers are validated and formatted to the North American Numbering Plan (`(XXX) XXX-XXXX`).
- Remote/contract queries enforce US geography (`geo=usa`, client location in United States).

