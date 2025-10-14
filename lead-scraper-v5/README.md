🎨 UNIVERSAL WEB DESIGN LEAD SCRAPER
📦 What This Is
A professional, production-ready lead scraper that finds businesses that need websites. Works for 30+ niches across 10+ Czech cities.
Perfect for:

🎨 Web design agencies
💼 Digital marketing agencies
🚀 Freelance web designers
💰 Lead generation businesses


✨ Key Features
✅ 30+ Pre-configured Niches - Restaurants, salons, gyms, clinics, etc.
✅ Smart Categorization - NO WEBSITE vs HAS WEBSITE leads
✅ Multi-Source Scraping - Combines multiple Czech business directories
✅ Priority Scoring - Automatic lead quality scoring
✅ Professional Excel Export - Color-coded, multi-sheet reports
✅ Bot Integration Ready - Perfect for website analyzer workflows
✅ Robust & Reliable - Won't crash, has multiple fallbacks
✅ Easy to Use - One command, get results

🚀 Quick Start (3 Steps)
1. Install Files
Replace these 4 files in your project:
✅ scrapers/registry_scraper.py
✅ scrapers/google_maps_scraper.py
✅ exporters/excel_exporter.py
✅ config.yaml
Add this new file to root:
✅ scrape_leads.py
2. Install Dependencies
bashcd "leads-scraper - kopie"
pip install -r requirements.txt
3. Run!
bashpython scrape_leads.py --niche restaurants --location Praha --max-results 200

📋 Complete Command Reference
Basic Usage
bashpython scrape_leads.py --niche [NICHE] --location [CITY] --max-results [NUMBER]
All Options
bashpython scrape_leads.py \
  --niche restaurants \           # Required: Business type
  --location Praha \              # Optional: City (default: Praha)
  --max-results 200 \             # Optional: Number of leads (default: 200)
  --skip-websites \               # Optional: Skip website scraping (faster)
  --verbose                       # Optional: Detailed logging
Real Examples
bash# Get 200 restaurant leads in Praha
python scrape_leads.py --niche restaurants --location Praha --max-results 200

# Get 150 hair salon leads in Brno
python scrape_leads.py --niche hair_salons --location Brno --max-results 150

# Quick test with 20 cafe leads
python scrape_leads.py --niche cafes --location Ostrava --max-results 20

# Fast scraping (skip website details)
python scrape_leads.py --niche fitness_gyms --location Praha --max-results 100 --skip-websites

🎯 Available Niches (30+)
🍽️ Food & Beverage (4)

restaurants - Restaurants, bistros
cafes - Coffee shops, cafés
bars - Bars, pubs, wine bars
bakeries - Bakeries

💅 Beauty & Wellness (5)

hair_salons - Hair salons, barbers
nail_studios - Nail salons, manicure
beauty_salons - Beauty studios, cosmetics
massage_studios - Massage, spa
tattoo_studios - Tattoo studios

🏥 Health & Medical (3)

dental_clinics - Dentists, dental care
physiotherapy - Physical therapy, rehab
veterinary - Veterinary clinics

💪 Fitness & Sports (3)

fitness_gyms - Gyms, fitness centers
yoga_studios - Yoga, pilates
martial_arts - Karate, boxing, martial arts

👔 Professional Services (4)

law_offices - Lawyers, attorneys
accounting - Accountants, bookkeeping
real_estate - Real estate agencies
insurance - Insurance agencies

🚗 Automotive (2)

car_repair - Auto repair, mechanics
car_wash - Car wash, detailing

🏠 Home Services (4)

plumbers - Plumbing, heating
electricians - Electrical services
cleaning - Cleaning services
florists - Flower shops

🛍️ Retail (3)

pet_shops - Pet stores, supplies
clothing_stores - Boutiques, fashion
gift_shops - Gift shops, souvenirs

📚 Education (3)

language_schools - Language courses
music_schools - Music lessons
tutoring - Private tutoring

🎉 Entertainment (2)

event_venues - Event spaces, venues
photo_studios - Photography studios

Total: 30+ niches ready to scrape!

🌍 Available Cities

Praha
Brno
Ostrava
Plzeň
Liberec
Olomouc
České Budějovice
Hradec Králové
Ústí nad Labem
Pardubice


📊 Excel Output Structure
Your Excel file will have 7 sheets:
🔥 Sheet 1: NO WEBSITE - QUALIFIED
Your money makers!

Businesses without websites
Highest conversion potential
Contact these immediately

🌐 Sheet 2: HAS WEBSITE - ANALYZE
Send to your analyzer bot

Businesses with websites
Your bot checks if website is good or bad
Bad websites = more qualified leads

⭐ Sheet 3: High Priority (75+)

Scored 75+ points
Mix of no website + poor website + missing contact info
Best leads overall

📊 Sheets 4-7

Medium Priority (50-74 points)
Low Priority (<50 points)
All Leads (complete database)
Summary (statistics & breakdown)


🎯 Your Workflow
┌─────────────────────────────────────────┐
│ 1. RUN SCRAPER                          │
│    python scrape_leads.py               │
│    --niche restaurants                  │
│    --location Praha                     │
│    --max-results 200                    │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 2. GET EXCEL FILE (10-15 mins)          │
│    data/exports/restaurants_Praha_      │
│    2025-10-11_14-30.xlsx                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ 3. TWO CATEGORIES                        │
│    ┌─────────────┬─────────────┐        │
│    │ NO WEBSITE  │ HAS WEBSITE │        │
│    │ (127 leads) │ (73 leads)  │        │
│    └─────────────┴─────────────┘        │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌─────────────┐    ┌──────────────────┐
│ NO WEBSITE  │    │ HAS WEBSITE      │
│             │    │ ↓                │
│ QUALIFIED!  │    │ Send to Bot      │
│             │    │ ↓                │
│ Contact Now │    │ Bot Analyzes     │
│             │    │ ↓                │
│             │    │ Bad Website?     │
│             │    │ ↓                │
│             │    │ QUALIFIED!       │
└─────────────┘    └──────────────────┘
        │                   │
        └─────────┬─────────┘
                  ▼
┌─────────────────────────────────────────┐
│ 4. COMBINED QUALIFIED LEADS             │
│    Ready to contact!                    │
│    Start selling! 💰                    │
└─────────────────────────────────────────┘

🔥 Priority Scoring System
How leads are scored automatically:
FactorPointsWhyNo website+100Immediate opportunity!Poor website+75High priority upgradeNo email+50Missing contact = potentialNo social media+25Limited online presenceNo reviews+20New or undiscovered businessLow rating-10May have quality issuesCzech domain (.cz)+5Local business bonus
Result: Leads sorted by conversion potential!

⚙️ Add Custom Niches
Want a niche not listed? Easy!
1. Edit config.yaml
yamlniches:
  # Add your custom niche
  your_niche_name:
    keywords_cz: ["české klíčové slovo", "další slovo"]
    keywords_en: ["english keyword", "another word"]
2. Run scraper
bashpython scrape_leads.py --niche your_niche_name --location Praha --max-results 200
Examples
yaml# Photography studios
photography_studios:
  keywords_cz: ["foto studio", "fotograf", "fotografování"]
  keywords_en: ["photo studio", "photographer", "photography"]

# Wedding services
wedding_services:
  keywords_cz: ["svatební", "svatby", "svatební agentura"]
  keywords_en: ["wedding", "wedding planner", "bridal"]

# Architects
architects:
  keywords_cz: ["architekt", "projektování", "architektura"]
  keywords_en: ["architect", "architecture", "design"]

💡 Pro Tips
Target High-Value Niches
bash# These convert best for web design:
python scrape_leads.py --niche restaurants --location Praha --max-results 200
python scrape_leads.py --niche dental_clinics --location Brno --max-results 150
python scrape_leads.py --niche law_offices --location Ostrava --max-results 100
python scrape_leads.py --niche real_estate --location Praha --max-results 200
Cover Multiple Cities
bash# Same niche, different cities = more leads
python scrape_leads.py --niche hair_salons --location Praha --max-results 200
python scrape_leads.py --niche hair_salons --location Brno --max-results 200
python scrape_leads.py --niche hair_salons --location Ostrava --max-results 150
python scrape_leads.py --niche hair_salons --location Plzeň --max-results 100
Batch Processing
bash# Create a bash script to run multiple niches
#!/bin/bash
python scrape_leads.py --niche restaurants --location Praha --max-results 200
python scrape_leads.py --niche cafes --location Praha --max-results 200
python scrape_leads.py --niche bars --location Praha --max-results 200
python scrape_leads.py --niche bakeries --location Praha --max-results 200

🛠️ Troubleshooting
ProblemSolutionUnknown nicheCheck available niches or add to config.yamlNo results foundTry different city or smaller max-resultsModuleNotFoundErrorRun pip install -r requirements.txtToo slowUse --skip-websites flagSelenium errorsIgnore them - scraper works without Selenium404 errorsNormal - scraper tries multiple sources

📁 Project Structure
leads-scraper - kopie/
├── scrape_leads.py              ← NEW! Universal scraper
├── config.yaml                  ← UPDATED! 30+ niches
├── scrapers/
│   ├── registry_scraper.py      ← UPDATED! Multi-source
│   ├── google_maps_scraper.py   ← UPDATED! More reliable
│   └── website_scraper.py       (unchanged)
├── exporters/
│   └── excel_exporter.py        ← UPDATED! Better categorization
├── processors/
│   ├── data_merger.py
│   ├── deduplicator.py
│   └── prioritizer.py
├── utils/
│   ├── email_extractor.py
│   ├── validators.py
│   └── logger.py
├── data/
│   └── exports/                 ← Your Excel files here!
├── logs/                        ← Error logs here
└── requirements.txt

📊 Expected Results
Per Niche (200 leads)

Time: 10-15 minutes
NO WEBSITE: ~60-70% (120-140 leads)
HAS WEBSITE: ~30-40% (60-80 leads)
High Priority: ~40-50% (80-100 leads)

Coverage

Restaurants: Excellent (many available)
Hair Salons: Excellent (high density)
Dental Clinics: Good (quality leads)
Cafes: Excellent (many options)
Smaller niches: Varies by city


✅ Success Checklist

 Files copied to correct locations
 Dependencies installed (pip install -r requirements.txt)
 Test run completed (--max-results 10)
 Full scraping successful (200+ leads)
 Excel file opens correctly
 NO WEBSITE sheet has qualified leads
 HAS WEBSITE sheet ready for analyzer bot


🚀 You're Ready!
Pick a niche and start scraping:
bashpython scrape_leads.py --niche restaurants --location Praha --max-results 200
Then watch the qualified leads roll in! 💰

Universal Web Design Lead Scraper v2.0
Updated: October 2025
Status: ✅ Production Ready