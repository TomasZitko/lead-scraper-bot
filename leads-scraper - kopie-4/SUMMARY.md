🕵️ STEALTH GOOGLE MAPS SCRAPER - Complete Guide
🎯 What's New
Advanced anti-detection techniques based on scraping best practices:
✅ Undetected ChromeDriver - Bypasses Google's bot detection
✅ Random User Agents - Rotates browser fingerprints
✅ Human-Like Behavior - Random delays, scrolling, mouse simulation
✅ Multiple Selectors - Adapts when Google changes HTML
✅ Smart Fallbacks - Works even if partially blocked
✅ Stealth JavaScript - Hides automation markers

📦 Installation
Step 1: Install Stealth Packages
powershellpip install undetected-chromedriver>=3.5.5
Or install all at once:
powershellpip install -r requirements_stealth.txt
Step 2: Replace Google Maps Scraper
Replace your file:

scrapers/google_maps_scraper.py
With: google_maps_scraper_stealth.py (rename it)


🚀 Quick Start
Test Run (Visible Browser)
powershellpy -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 10
You'll see:

Chrome browser opens (visible)
Navigates to Google Maps like a human
Scrolls through results
Extracts business data
Browser closes automatically


🎮 How It Works
1. Stealth Browser Initialization
🕵️  Initializing stealth browser...
✅ Stealth browser initialized successfully!
The scraper:

Uses undetected-chromedriver (hard to detect)
Randomizes window size (1200-1920 x 800-1080)
Rotates user agents
Injects anti-detection JavaScript
Removes automation markers

2. Human-Like Navigation
🔍 Searching Google Maps: restaurace Praha
The scraper:

Goes to Google.com first (like a human)
Waits 2-4 seconds randomly
Then goes to Google Maps
Simulates mouse movements
Random scrolling

3. Smart Extraction
✓ Found results with selector: div[role='feed']
✓ Found 15 businesses
The scraper:

Tries multiple CSS selectors (Google changes them)
Scrolls like a human (2-4 second delays)
Extracts visible listings
Handles stale elements
Falls back if needed

4. Data Extraction
✅ Found 15 businesses
📊 Exporting to Excel...

⚙️ Configuration Options
Basic Usage
powershell# Default: 20 results
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 20

# Smaller batch
py -3.13 scrape_leads.py --niche cafes --location Brno --max-results 10

# Larger batch (be careful)
py -3.13 scrape_leads.py --niche hair_salons --location Praha --max-results 50
With Website Scraping
powershell# Full data extraction
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 20

# Skip website scraping (faster)
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 20 --skip-websites

🎯 Success Rates
Expected Results:
Max ResultsSuccess RateTimeNotes1090-100%2-3 minBest for testing2080-95%4-6 minRecommended5060-80%10-15 minMay trigger detection100+40-60%20+ minHigh risk of blocks
Why Success Varies:

Time of day - Night = better (less traffic)
Location popularity - Praha = more results
Previous usage - New IP = better
Keyword - Popular terms work better


🛡️ Anti-Detection Features
1. Undetected ChromeDriver
pythonself.driver = uc.Chrome(options=options)

Latest anti-detection techniques
Regular updates for new Google blocks
Better than regular Selenium

2. Stealth JavaScript
javascriptObject.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

Hides automation markers
Makes bot appear like real browser
Injected on every page load

3. Human-Like Behavior
pythontime.sleep(random.uniform(2, 4))  # Random delays
self._simulate_mouse_movement()    # Random scrolling

Random delays (2-5 seconds)
Random scrolling patterns
Mouse movement simulation

4. Multiple Selectors
pythonpossible_selectors = [
    "div[role='feed']",
    "div.m6QErb",
    "div[aria-label*='Results']",
]

Tries multiple CSS selectors
Adapts when Google changes HTML
Falls back to page source if needed

5. Smart Rate Limiting
pythonfor scroll_iteration in range(5):
    time.sleep(random.uniform(2, 4))

5 scroll iterations max
2-4 second delays between scrolls
Mimics human browsing speed


🚨 When You Get Blocked
Signs of Blocking:
⚠️ Could not find results container
⚠️ Using fallback search method
What to Do:
Option 1: Wait and Retry (BEST)
powershell# Wait 10-30 minutes
# Then try again
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 10
Option 2: Change IP (If VPN available)
1. Connect to VPN
2. Change location
3. Try again
Option 3: Use Smaller Batches
powershell# Instead of 50, do 5x batches of 10
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 10
# Wait 5 minutes
py -3.13 scrape_leads.py --niche cafes --location Praha --max-results 10
# Wait 5 minutes
py -3.13 scrape_leads.py --niche bars --location Praha --max-results 10
Option 4: Manual Mode
Just use the scraper to learn the process
Then do manual research on Firmy.cz

💡 Pro Tips
1. Best Times to Scrape
🌙 Night (10 PM - 6 AM) - Less Google traffic
🌅 Early morning (6-8 AM) - Before peak hours
❌ Avoid: 9 AM - 5 PM (peak business hours)
2. Optimal Batch Sizes
✅ 10-20 results per run
⚠️ 30-50 results occasionally  
❌ 100+ results (high risk)
3. Location Strategy
powershell# Spread across cities to avoid detection
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 15
# Wait 5 minutes
py -3.13 scrape_leads.py --niche restaurants --location Brno --max-results 15
# Wait 5 minutes
py -3.13 scrape_leads.py --niche restaurants --location Ostrava --max-results 15
4. Keyword Variety
powershell# Use Czech keywords (less competition)
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 15
py -3.13 scrape_leads.py --niche cafes --location Praha --max-results 15
py -3.13 scrape_leads.py --niche bars --location Praha --max-results 15

🔧 Advanced Configuration
Headless Mode (Runs Hidden)
Edit google_maps_scraper.py:
python# Find this line:
# options.add_argument('--headless=new')

# Uncomment it:
options.add_argument('--headless=new')
Pro: Faster, runs in background
Con: Slightly easier to detect
Proxy Support (Advanced)
Install:
powershellpip install selenium-wire
Edit scraper to add:
pythonfrom seleniumwire import webdriver

# Add proxy config
proxy_options = {
    'proxy': {
        'http': 'http://proxy-server:port',
        'https': 'https://proxy-server:port',
    }
}
When to use:

You're scraping 100+ results/day
You get blocked frequently
You need residential proxies


📊 Expected Output
Successful Run:
╔══════════════════════════════════════════════╗
║   🎨 WEB DESIGN LEAD SCRAPER                 ║
║   Find Businesses That Need Websites         ║
╚══════════════════════════════════════════════╝

🎯 Target: 20 Restaurants in Praha
📋 Keywords: restaurace, restaurant...

🕵️  Initializing stealth browser...
✅ Stealth browser initialized successfully!

━━━ STEP 1: Searching Google Maps ━━━
   Searching for: restaurace...
🔍 Searching Google Maps: restaurace Praha
✓ Found results with selector: div[role='feed']
✅ Found 18 businesses

   Searching for: restaurant...
🔍 Searching Google Maps: restaurant Praha
✓ Found results with selector: div[role='feed']
✅ Found 15 businesses

   ✓ Found 20 unique businesses

━━━ STEP 2: Scraping Websites ━━━
   Scraping 12 websites...
   ✓ Found 5 emails
   ✓ Found 8 social media profiles

━━━ STEP 3: Cleaning Data ━━━
   ✓ 20 valid businesses

━━━ STEP 4: Calculating Priority Scores ━━━
   🔥 8 leads WITHOUT website (Qualified!)
   🌐 12 leads WITH website (Need analysis)
   ⭐ 14 high-priority leads (75+ score)

━━━ STEP 5: Exporting to Excel ━━━
   ✓ Saved: data/exports/restaurants_Praha_2025-10-11_15-30.xlsx

✨ SCRAPING COMPLETE! ✨
📊 Total Leads: 20
🔥 No Website: 8
🌐 Has Website: 12
⏱️  Time: 4m 32s

✅ Happy selling! 💰

🎯 Realistic Expectations
What Works:
✅ 10-20 results per run - Reliable
✅ 2-3 runs per day - Safe limit
✅ Different cities/niches - Spreads load
✅ Visible browser mode - More human-like
✅ Random delays - Mimics real behavior
What Doesn't:
❌ 100+ results at once - Gets blocked
❌ Continuous scraping - Triggers detection
❌ Same niche/location repeatedly - Pattern detected
❌ No delays - Obviously a bot
❌ Headless mode - Easier to detect

🚀 Recommended Workflow
Daily Routine:
powershell# Morning (8 AM)
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 15

# Wait 3-4 hours

# Lunch (12 PM)
py -3.13 scrape_leads.py --niche cafes --location Brno --max-results 15

# Wait 3-4 hours

# Evening (4 PM)
py -3.13 scrape_leads.py --niche hair_salons --location Ostrava --max-results 15

# Total: 45 verified leads per day!
Weekly Goal:

45 leads/day × 5 days = 225 leads/week
~100 without websites = 100 qualified leads
10% conversion = 10 clients/week 💰


🎯 Bottom Line
This Stealth Scraper:
✅ Works better than basic Selenium
✅ Harder to detect with anti-bot techniques
✅ More reliable with smart fallbacks
✅ Real data from Google Maps
But Remember:
⚠️ Not 100% undetectable
⚠️ Use reasonable limits (10-20 per run)
⚠️ Take breaks between runs
⚠️ Combine with manual research
Best Strategy:
1. Scrape 20 leads per run (stealth mode)
2. Wait 3-4 hours
3. Scrape different niche/city
4. Repeat 2-3x per day
5. Get 40-60 leads/day reliably! 🚀

🎉 Ready to Start!
powershell# Install stealth package
pip install undetected-chromedriver

# Replace the scraper file

# Test run
py -3.13 scrape_leads.py --niche restaurants --location Praha --max-results 10

# Watch it work! 🕵️
This is as good as it gets for free scraping! 🚀