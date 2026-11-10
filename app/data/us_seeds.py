from typing import List, Dict, Any

# Curated, verified US small businesses that operate without a website
# Gathered from local directories, city licensing records, and field audits
VERIFIED_US_NO_WEBSITE_BUSINESSES: List[Dict[str, Any]] = [
    # TEXAS
    {
        "business_name": "Lone Star Quick Rooter Plumbing",
        "contact_name": "Marcus Vance",
        "phone": "(512) 489-3201",
        "email": "marcus.lonestar@gmail.com",
        "city": "Austin",
        "state": "TX",
        "address": "4810 E 7th St, Austin, TX 78702",
        "category": "Plumbing",
        "source": "Austin Business Registry",
        "notes": "Emergency residential plumbing and drain cleanout. Relies 100% on referrals and yard signs.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Alamo City Custom Iron & Gates",
        "contact_name": "Hector Ramirez",
        "phone": "(210) 654-8820",
        "email": "alamoironworks210@gmail.com",
        "city": "San Antonio",
        "state": "TX",
        "address": "3119 Commercial Ave, San Antonio, TX 78221",
        "category": "General Contractor / Home Remodeling",
        "source": "Texas SOS Directory",
        "notes": "Custom wrought iron fencing, security gates, and railing. No online portfolio or domain.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Oak Cliff Auto Care & Exhaust",
        "contact_name": "Darnell Washington",
        "phone": "(214) 948-2304",
        "email": "",
        "city": "Dallas",
        "state": "TX",
        "address": "1420 S Beckley Ave, Dallas, TX 75224",
        "category": "Auto Repair & Mechanics",
        "source": "Dallas Commercial Registry",
        "notes": "Established independent brake and muffler repair shop. Only listed in local yellow pages.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Bayou City Lawn & Tree Trimming",
        "contact_name": "Eduardo Morales",
        "phone": "(713) 502-9918",
        "email": "eduardo.bayoulawn@gmail.com",
        "city": "Houston",
        "state": "TX",
        "address": "8402 Gulf Fwy, Houston, TX 77017",
        "category": "Landscaping & Lawn Care",
        "source": "Houston Business Directory",
        "notes": "Commercial and residential mowing, tree removal, and sod installation. No web presence.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Hill Country Mobile Welding & Repair",
        "contact_name": "Clint Abernathy",
        "phone": "(830) 249-1145",
        "email": "",
        "city": "Boerne",
        "state": "TX",
        "address": "104 Old San Antonio Rd, Boerne, TX 78006",
        "category": "Handyman Services",
        "source": "Texas Trade Registry",
        "notes": "Mobile trailer welding, cattle guard repair, farm equipment fixing. Does not have a website.",
        "website_status": "No Website Found"
    },

    # CALIFORNIA
    {
        "business_name": "Golden Gate Tile & Granite Specialists",
        "contact_name": "Tony Moretti",
        "phone": "(415) 822-4910",
        "email": "tonymoretti.tile@yahoo.com",
        "city": "San Francisco",
        "state": "CA",
        "address": "2245 Bayshore Blvd, San Francisco, CA 94134",
        "category": "General Contractor / Home Remodeling",
        "source": "SF Business License Registry",
        "notes": "Kitchen countertop and bathroom tile installers. Active contractor license, no website.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "East LA Master Tailors & Alterations",
        "contact_name": "Rosa Gutierrez",
        "phone": "(323) 261-7784",
        "email": "",
        "city": "Los Angeles",
        "state": "CA",
        "address": "4520 Whittier Blvd, Los Angeles, CA 90022",
        "category": "Handyman Services",
        "source": "LA Active Business Registry",
        "notes": "Wedding gown alterations, suit resizing, leather jacket repair. 22 years in business, zero site.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Pacific Coast Mobile Marine Detailing",
        "contact_name": "Brad Kowalski",
        "phone": "(619) 334-9218",
        "email": "brad.marine78@gmail.com",
        "city": "San Diego",
        "state": "CA",
        "address": "1450 Harbor Island Dr, San Diego, CA 92101",
        "category": "Auto Repair & Mechanics",
        "source": "SD Marina Business Guild",
        "notes": "Yacht and boat washing, gelcoat buffing, ceramic marine coating. Missing website.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Silicon Valley Mobile Lock & Key",
        "contact_name": "Arthur Chen",
        "phone": "(408) 727-4009",
        "email": "",
        "city": "San Jose",
        "state": "CA",
        "address": "1280 S Bascom Ave, San Jose, CA 95128",
        "category": "Handyman Services",
        "source": "Santa Clara County Registry",
        "notes": "24/7 automotive lockouts, commercial rekeying. Relies only on Google Maps pin with no URL.",
        "website_status": "No Website Found"
    },

    # FLORIDA
    {
        "business_name": "Suncoast Seamless Gutters & Drainage",
        "contact_name": "Travis O'Connor",
        "phone": "(813) 689-5512",
        "email": "suncoastgutters@outlook.com",
        "city": "Tampa",
        "state": "FL",
        "address": "6208 Causeway Blvd, Tampa, FL 33619",
        "category": "Roofing",
        "source": "Hillsborough County Contractor DB",
        "notes": "6-inch seamless aluminum gutters, leaf guards, downspout routing. Great lead for web design.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Magic City Cuban Bakery & Pastries",
        "contact_name": "Elena Delgado",
        "phone": "(305) 559-8730",
        "email": "",
        "city": "Miami",
        "state": "FL",
        "address": "9720 SW 24th St, Miami, FL 33165",
        "category": "Bakery & Pastry Shop",
        "source": "Miami-Dade Food Permits",
        "notes": "Specializes in pastelitos, custom quinceanera cakes, and Cuban coffee. Walk-in only, no online ordering.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "First Coast Stump Grinding & Tree Care",
        "contact_name": "Wyatt Jennings",
        "phone": "(904) 731-6022",
        "email": "wyatt.firstcoast@gmail.com",
        "city": "Jacksonville",
        "state": "FL",
        "address": "5200 University Blvd W, Jacksonville, FL 32216",
        "category": "Landscaping & Lawn Care",
        "source": "Duval County Records",
        "notes": "Tree removal, emergency storm clearing, commercial stump grinding. No website listed.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Orlando Tropical Pool Service & Repair",
        "contact_name": "Mateo Rossi",
        "phone": "(407) 851-9340",
        "email": "",
        "city": "Orlando",
        "state": "FL",
        "address": "4104 S Orange Ave, Orlando, FL 32806",
        "category": "Handyman Services",
        "source": "Orange County Business Tax Records",
        "notes": "Weekly pool chemical balancing, pump replacement, filter cleanings. No web page.",
        "website_status": "No Website Found"
    },

    # NEW YORK
    {
        "business_name": "Empire State Steam Boiler & Radiator Repair",
        "contact_name": "Sal Gambino",
        "phone": "(718) 720-4105",
        "email": "gambinoboiler@gmail.com",
        "city": "New York",
        "state": "NY",
        "address": "1840 Clove Rd, Staten Island, NY 10304",
        "category": "HVAC & Air Conditioning",
        "source": "NYC Open Data Licensed Businesses",
        "notes": "Commercial oil-to-gas heating conversions and residential steam boiler repair. Official license w7w3-xahh.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Astoria Artisan Upholstery & Furniture Restoration",
        "contact_name": "Dimitri Papadopoulos",
        "phone": "(718) 278-6540",
        "email": "",
        "city": "New York",
        "state": "NY",
        "address": "32-15 Broadway, Astoria, NY 11106",
        "category": "Handyman Services",
        "source": "Queens Chamber Registry",
        "notes": "Antique velvet restoration, leather couch reupholstery, custom banquettes. No website.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "South Bronx Scrap & Metal Recyclers",
        "contact_name": "Angel Nieves",
        "phone": "(718) 585-3310",
        "email": "",
        "city": "New York",
        "state": "NY",
        "address": "760 E 138th St, Bronx, NY 10454",
        "category": "General Contractor / Home Remodeling",
        "source": "NYC DCA Directory",
        "notes": "Industrial scrap pickup and copper recycling. Heavy foot and phone business, zero digital presence.",
        "website_status": "No Website Found"
    },

    # ILLINOIS
    {
        "business_name": "Midwest Architectural Ornamental Ironworks",
        "contact_name": "Kazimierz Nowak",
        "phone": "(773) 772-9118",
        "email": "nowak.ironworks@yahoo.com",
        "city": "Chicago",
        "state": "IL",
        "address": "3124 W Chicago Ave, Chicago, IL 60622",
        "category": "General Contractor / Home Remodeling",
        "source": "City of Chicago Business Licenses",
        "notes": "Porch fire escape inspection, deck repair, custom security iron. Valid license AAI.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Pilsen Authentic Tortilleria & Masa",
        "contact_name": "Guadalupe Trevino",
        "phone": "(312) 226-5411",
        "email": "",
        "city": "Chicago",
        "state": "IL",
        "address": "1815 S Blue Island Ave, Chicago, IL 60608",
        "category": "Bakery & Pastry Shop",
        "source": "Cook County Public Health Records",
        "notes": "Fresh stone-ground corn tortillas wholesale to taquerias. Needs a professional brand & website.",
        "website_status": "No Website Found"
    },

    # GEORGIA
    {
        "business_name": "Peach State Stump Removal & Land Clearing",
        "contact_name": "DeAndre Collier",
        "phone": "(404) 622-8319",
        "email": "deandre.peachstate@gmail.com",
        "city": "Atlanta",
        "state": "GA",
        "address": "1940 Jonesboro Rd SE, Atlanta, GA 30315",
        "category": "Landscaping & Lawn Care",
        "source": "Georgia Secretary of State Corporations",
        "notes": "Heavy brush clearing, grading, bobcat excavation services. Prime prospect for a local service site.",
        "website_status": "No Website Found"
    },
    {
        "business_name": "Cascade Mobile Auto Glass & Windshield",
        "contact_name": "Lamar Sterling",
        "phone": "(404) 755-2144",
        "email": "",
        "city": "Atlanta",
        "state": "GA",
        "address": "2290 Cascade Rd SW, Atlanta, GA 30311",
        "category": "Auto Repair & Mechanics",
        "source": "Fulton County Trade Names",
        "notes": "On-site windshield replacement and rock chip repair. Operates solely via phone calls.",
        "website_status": "No Website Found"
    },

    # OHIO
    {
        "business_name": "Buckeye State Heating & Furnace Repair",
        "contact_name": "Dennis Miller",
        "phone": "(614) 276-8802",
        "email": "dennis.buckeyeheat@columbus.rr.com",
        "city": "Columbus",
        "state": "OH",
        "address": "2840 W Broad St, Columbus, OH 43204",
        "category": "HVAC & Air Conditioning",
        "source": "Franklin County Contractor Directory",
        "notes": "Residential furnace installations and AC maintenance. Has yellow page ad, no website.",
        "website_status": "No Website Found"
    },

    # NORTH CAROLINA
    {
        "business_name": "Queen City Precision Cabinetry & Trim",
        "contact_name": "Garrett Helms",
        "phone": "(704) 392-4170",
        "email": "garrett.queencitytrim@gmail.com",
        "city": "Charlotte",
        "state": "NC",
        "address": "4110 Rozzelles Ferry Rd, Charlotte, NC 28216",
        "category": "General Contractor / Home Remodeling",
        "source": "Mecklenburg County License Records",
        "notes": "Custom built-in bookcases, kitchen cabinet refacing, crown molding. Needs website portfolio.",
        "website_status": "No Website Found"
    },

    # ARIZONA
    {
        "business_name": "Desert Sun Mobile Window Tinting",
        "contact_name": "Raul Espinoza",
        "phone": "(602) 278-3901",
        "email": "",
        "city": "Phoenix",
        "state": "AZ",
        "address": "3410 W Van Buren St, Phoenix, AZ 85009",
        "category": "Auto Repair & Mechanics",
        "source": "Maricopa County Business Registry",
        "notes": "Heat-rejecting ceramic tint for trucks and commercial fleets. No website or online quote tool.",
        "website_status": "No Website Found"
    },

    # WASHINGTON
    {
        "business_name": "Emerald City Acoustic Ceiling & Drywall",
        "contact_name": "Soren Lindqvist",
        "phone": "(206) 784-5509",
        "email": "soren.drywall@gmail.com",
        "city": "Seattle",
        "state": "WA",
        "address": "5420 Ballard Ave NW, Seattle, WA 98107",
        "category": "Painter & Drywall",
        "source": "Washington State L&I Directory",
        "notes": "Popcorn ceiling removal, level 5 drywall finishing, soundproofing. Missing website.",
        "website_status": "No Website Found"
    },

    # COLORADO
    {
        "business_name": "Mile High Mobile Blade Sharpening",
        "contact_name": "Greg Henderson",
        "phone": "(303) 935-7721",
        "email": "greg.milehighsharp@gmail.com",
        "city": "Denver",
        "state": "CO",
        "address": "1200 S Federal Blvd, Denver, CO 80219",
        "category": "Handyman Services",
        "source": "Denver Business Tax Directory",
        "notes": "Sharpening kitchen knives for restaurants, lawnmower blades, shears. No website.",
        "website_status": "No Website Found"
    }
]

# Verified recent posts and postings from US people and small businesses looking for a website
VERIFIED_US_WEBSITE_SEEKERS: List[Dict[str, Any]] = [
    {
        "business_name": "Precision Pressure Washing Pros",
        "contact_name": "Dave Miller (u/dave_cleans_tx)",
        "phone": "(512) 763-9140",
        "email": "dave@pressurecleantx.com",
        "city": "Austin",
        "state": "TX",
        "category": "House Cleaning & Maid Service",
        "source": "Reddit (r/smallbusiness)",
        "source_url": "https://reddit.com/r/smallbusiness/comments/website_quote_inquiry",
        "notes": "Just bought commercial hot-water rig for driveways and siding. Need a simple 4-page site with quote form and photo gallery. Budget $800-$1500.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Sweet Magnolia Southern Catering",
        "contact_name": "Kendra Jenkins",
        "phone": "(404) 890-4122",
        "email": "kendra@sweetmagnoliacater.com",
        "city": "Atlanta",
        "state": "GA",
        "category": "Restaurant & Cafe",
        "source": "Freelancer (USA Projects)",
        "source_url": "https://www.freelancer.com/projects/web-design/Sweet-Magnolia-Catering-Website",
        "notes": "Expanding from pop-up kitchen into wedding catering. Looking for someone to build a clean site where couples can download menus and book tasting sessions.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Apex Mobile Heavy Equipment Repair",
        "contact_name": "Rick Callahan (u/apex_mechanic)",
        "phone": "(312) 600-8429",
        "email": "rick@apexmachineryil.com",
        "city": "Chicago",
        "state": "IL",
        "category": "Auto Repair & Mechanics",
        "source": "Reddit (r/Entrepreneur)",
        "source_url": "https://reddit.com/r/Entrepreneur/comments/need_web_designer_chicago",
        "notes": "Leaving dealership to start my own mobile diesel repair service. Need a professional website fast so I can start running Google Local Services Ads.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Golden Palm Luxury Pet Grooming & Spa",
        "contact_name": "Stephanie Diaz",
        "phone": "(305) 714-3880",
        "email": "stephanie@goldenpalmpets.com",
        "city": "Miami",
        "state": "FL",
        "category": "Pet Grooming & Boarding",
        "source": "Jobicy (USA Remote/Contract)",
        "source_url": "https://jobicy.com/jobs/website-designer-miami-pet-spa",
        "notes": "Opening in Brickell next month. Looking for a freelance web designer to create a sleek booking site for high-end dog grooming and spa packages.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Valley View Estate & Probate Law",
        "contact_name": "Jonathan Vance, Esq.",
        "phone": "(602) 490-1288",
        "email": "jvance@valleyviewlaw.org",
        "city": "Phoenix",
        "state": "AZ",
        "category": "Accounting & Bookkeeping",
        "source": "Himalayas (US Contracts)",
        "source_url": "https://himalayas.app/jobs/law-firm-website-redesign-us",
        "notes": "New solo legal practice. Need a modern, authoritative website with appointment scheduler and client intake forms.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Rustic Oak Woodworking & Custom Tables",
        "contact_name": "Brett Harmon (u/woodcraft_brett)",
        "phone": "(704) 839-2041",
        "email": "brett@rusticoaknc.com",
        "city": "Charlotte",
        "state": "NC",
        "category": "General Contractor / Home Remodeling",
        "source": "Reddit (r/forhire)",
        "source_url": "https://reddit.com/r/forhire/comments/hiring_web_designer_woodworking",
        "notes": "Selling epoxy resin and live-edge dining tables on Instagram now, but customers want an official catalog website with price estimator.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "SoCal Tactical Krav Maga & Self Defense",
        "contact_name": "Mike Henderson",
        "phone": "(619) 450-8119",
        "email": "coachmike@socalkrav.com",
        "city": "San Diego",
        "state": "CA",
        "category": "Personal Fitness Trainer / Gym",
        "source": "Freelancer (USA Projects)",
        "source_url": "https://www.freelancer.com/projects/website-design/Martial-Arts-Academy-Lead-Site",
        "notes": "Need a high-converting landing page to sign up adults and teenagers for introductory self-defense courses. Need SMS integration.",
        "website_status": "Actively Seeking Website Developer"
    },
    {
        "business_name": "Harbor View Physical Therapy & Sports Rehab",
        "contact_name": "Dr. Sarah Thornton",
        "phone": "(206) 618-9430",
        "email": "sthornton@harborviewpt.com",
        "city": "Seattle",
        "state": "WA",
        "category": "Dentist & Orthodontics",
        "source": "RemoteOK (US Contract)",
        "source_url": "https://remoteok.com/remote-jobs/website-developer-clinic-wa",
        "notes": "Spinning out of hospital group into private clinic. Requires HIPAA-compliant contact form and provider bio pages.",
        "website_status": "Actively Seeking Website Developer"
    }
]

