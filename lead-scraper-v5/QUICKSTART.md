🎨 Universal Web Design Lead Scraper - Quick Start
🚀 One Command to Rule Them All
Get 200 leads for ANY niche in 3 steps:
bash# 1. Navigate to project
cd "leads-scraper - kopie"

# 2. Run scraper (pick any niche!)
python scrape_leads.py --niche restaurants --location Praha --max-results 200

# 3. Open Excel file in data/exports/

📋 Available Niches (30+)
🍽️ Food & Beverage
bash--niche restaurants
--niche cafes
--niche bars
--niche bakeries
💅 Beauty & Wellness
bash--niche hair_salons
--niche nail_studios
--niche beauty_salons
--niche massage_studios
--niche tattoo_studios
🏥 Health & Medical
bash--niche dental_clinics
--niche physiotherapy
--niche veterinary
💪 Fitness & Sports
bash--niche fitness_gyms
--niche yoga_studios
--niche martial_arts
👔 Professional Services
bash--niche law_offices
--niche accounting
--niche real_estate
--niche insurance
🚗 Automotive
bash--niche car_repair
--niche car_wash
🏠 Home Services
bash--niche plumbers
--niche electricians
--niche cleaning
--niche florists
🛍️ Retail
bash--niche pet_shops
--niche clothing_stores
--niche gift_shops
📚 Education
bash--niche language_schools
--niche music_schools
--niche tutoring
🎉 Entertainment
bash--niche event_venues
--niche photo_studios

🌍 Available Locations
Praha, Brno, Ostrava, Plzeň, Liberec, Olomouc,
České Budějovice, Hradec Králové, Ústí nad Labem, Pardubice

💡 Usage Examples
Basic Usage
bashpython scrape_leads.py --niche restaurants --location Praha --max-results 200
Different City
bashpython scrape_leads.py --niche hair_salons --location Brno --max-results 150
Quick Test (Small Sample)
bashpython scrape_leads.py --niche cafes --location Ostrava --max-results 20
Skip Website Scraping (Faster)
bashpython scrape_leads.py --niche nail_studios --location Praha --max-results 100 --skip-websites
Verbose Logging (Debug)
bashpython scrape_leads.py --niche fitness_gyms --location Brno --max-results 50 --verbose

📊 What You Get
Excel File Structure:
SheetDescription🔥 NO WEBSITE - QUALIFIEDBusinesses without websites = Ready to sell!🌐 HAS WEBSITE - ANALYZEBusinesses with websites = Send to your botHigh Priority (75+)Best leads by scoreMedium PriorityGood follow-up targetsLow PriorityLower conversion potentialAll LeadsComplete databaseSummaryStatistics & breakdown

🎯 Workflow
1. Pick a niche → Run scraper
   python scrape_leads.py --niche [YOUR_NICHE] --location Praha --max-results 200

2. Wait 10-15 minutes → Get Excel file

3. Open Excel → Two categories:
   🔥 NO WEBSITE = Qualified leads (contact immediately!)
   🌐 HAS WEBSITE = Send to analyzer bot

4. Bot analyzes websites → Finds bad ones

5. Combine qualified leads → Start selling! 💰

⚙️ Command Options
FlagDescriptionExample--nicheBusiness type to scrape (required)--niche restaurants--locationCity name (default: Praha)--location Brno--max-resultsNumber of leads (default: 200)--max-results 150--skip-websitesSkip website scraping (faster)--skip-websites--verboseDetailed logging--verbose

🎁 Add Custom Niches
Edit config.yaml and add your own:
yamlniches:
  your_custom_niche:
    keywords_cz: ["české klíčové slovo", "další slovo"]
    keywords_en: ["english keyword", "another keyword"]
Then run:
bashpython scrape_leads.py --niche your_custom_niche --location Praha --max-results 200

🔥 Pro Tips
Target Multiple Niches
bash# Run multiple times for different niches
python scrape_leads.py --niche restaurants --location Praha --max-results 200
python scrape_leads.py --niche cafes --location Praha --max-results 200
python scrape_leads.py --niche bars --location Praha --max-results 200
Cover Multiple Cities
bash# Same niche, different cities
python scrape_leads.py --niche hair_salons --location Praha --max-results 200
python scrape_leads.py --niche hair_salons --location Brno --max-results 200
python scrape_leads.py --niche hair_salons --location Ostrava --max-results 200
Fast Testing
bash# Test with small sample first
python scrape_leads.py --niche your_niche --location Praha --max-results 10

✅ Success Output
╔══════════════════════════════════════════════╗
║   EXPORT SUMMARY                              ║
╚══════════════════════════════════════════════╝
🔥 NO WEBSITE (Qualified Leads): 127
🌐 HAS WEBSITE (Send to Analyzer): 73
📊 Total Leads: 200

📋 NEXT STEPS:
   1. Open the Excel file
   2. Sheet '🔥 NO WEBSITE' = Your qualified leads!
   3. Sheet '🌐 HAS WEBSITE' = Send to your analyzer
   4. Combine all qualified leads and start selling!

✅ Happy selling! 💰

🛠️ Troubleshooting
ProblemSolutionUnknown nicheCheck available niches above or add to config.yamlNo resultsTry different city or smaller --max-resultsToo slowUse --skip-websites flagErrorsCheck logs/ folder for details

📁 Output Location
All Excel files saved in:
data/exports/[niche]_[location]_[date-time].xlsx
Example:
data/exports/restaurants_Praha_2025-10-11_14-30.xlsx

🎯 Best Target Niches for Web Design
Highest Conversion:

Restaurants (always need better websites)
Hair Salons (visual business, needs online presence)
Dental Clinics (trust + professionalism = must have website)
Real Estate (property listings need websites)
Law Offices (credibility requires professional site)

Good Conversion:

Cafes, Bars, Bakeries (food businesses)
Nail Studios, Beauty Salons (beauty industry)
Fitness Gyms, Yoga Studios (fitness sector)
Plumbers, Electricians (local services)
Event Venues, Photo Studios (creative services)


🚀 Ready to Go!
Pick a niche, pick a city, and start scraping:
bashpython scrape_leads.py --niche restaurants --location Praha --max-results 200
Then watch the qualified leads roll in! 💰