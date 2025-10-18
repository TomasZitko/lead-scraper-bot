# 🎯 COMPLETE COMMAND REFERENCE

## 📋 Table of Contents
1. [Basic Scraping](#basic-scraping)
2. [Advanced Scraping](#advanced-scraping)
3. [Database Management](#database-management)
4. [Reset & History](#reset--history)
5. [Export Commands](#export-commands)
6. [Emergency Recovery](#emergency-recovery)
7. [All Available Niches](#all-available-niches)
8. [Common Workflows](#common-workflows)

---

## 🚀 Basic Scraping

### Scrape Single Niche (FINAL Version)
```bash
# Basic command
python scrape_leads_FINAL.py --niche restaurants --location Praha --max-results 500

# With all options
python scrape_leads_FINAL.py --niche restaurants --location Praha --max-results 500 --skip-registry

# Skip website scraping (faster)
python scrape_leads_FINAL.py --niche restaurants --location Praha --max-results 500 --skip-websites

# Skip both (fastest)
python scrape_leads_FINAL.py --niche restaurants --location Praha --max-results 500 --skip-websites --skip-registry
```

### Scrape Single Niche (SMART Version)
```bash
# Basic command
python scrape_city_SMART.py --city Praha --niche restaurants

# With options
python scrape_city_SMART.py --city Praha --niche restaurants --skip-websites --skip-registry

# Control results per area
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 100
```

### Scrape Multiple Niches at Once
```bash
# Multiple niches in one command
python scrape_city_SMART.py --city Praha --niche restaurants,cafes,bars

# Food category
python scrape_city_SMART.py --city Praha --niche restaurants,cafes,bars,bakeries

# Beauty category
python scrape_city_SMART.py --city Praha --niche hair_salons,nail_studios,beauty_salons,massage_studios

# Fitness category
python scrape_city_SMART.py --city Praha --niche fitness_gyms,personal_trainers,yoga_studios,crossfit
```

### Scrape ENTIRE City (All Niches)
```bash
# Complete city scrape (3-4 hours)
python scrape_city_SMART.py --city Liberec --complete

# Complete city with custom results per area
python scrape_city_SMART.py --city Praha --complete --results-per-area 50

# Complete city, skip website scraping (faster)
python scrape_city_SMART.py --city Brno --complete --skip-websites
```

---

## ⚙️ Advanced Scraping

### Quick Test Scraping
```bash
# 5-minute test with small results
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 10 --skip-websites --skip-registry

# Test multiple niches quickly
python scrape_city_SMART.py --city Praha --niche restaurants,cafes --results-per-area 10 --skip-websites
```

### High-Quality Scraping
```bash
# Maximum quality (emails, social, registry)
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 100

# All niches with full quality
python scrape_city_SMART.py --city Praha --complete --results-per-area 80
```

### Verbose Mode (Debugging)
```bash
# See detailed logs
python scrape_city_SMART.py --city Praha --niche restaurants --verbose

# Debug with FINAL version
python scrape_leads_FINAL.py --niche restaurants --location Praha --max-results 100 --verbose
```

---

## 💾 Database Management

### View Database Statistics
```bash
# View overall stats
python db_admin.py stats

# View stats for specific niche
python db_admin.py stats --niche restaurants

# View stats for specific city
python db_admin.py stats --city Praha
```

### List All Data
```bash
# List all cities in database
python db_admin.py cities

# List all niches in database
python db_admin.py niches
```

### Export from Database
```bash
# Export all data to Excel
python db_admin.py export

# Export specific city
python db_admin.py export --city Praha

# Export specific niche
python db_admin.py export --niche restaurants

# Export specific city + niche
python db_admin.py export --city Praha --niche restaurants

# Custom output file
python db_admin.py export --city Praha --output my_leads.xlsx
```

---

## 🔄 Reset & History

### Reset Specific Area
```bash
# Reset one city (allows re-scraping)
python db_admin.py reset-city --city Praha

# Reset one niche in one city
python db_admin.py reset-niche --niche restaurants --city Praha

# Reset niche in ALL cities
python db_admin.py reset-niche --niche restaurants
```

### Reset Specific District/Area
```bash
# Reset specific area using db_tools
python db_tools.py reset --niche restaurants --city Praha --area "Praha 1"

# Reset entire city
python db_tools.py reset --niche restaurants --city Praha
```

### Complete Database Reset
```bash
# DANGER: Delete EVERYTHING (cannot be undone!)
python db_admin.py reset-all

# You'll be prompted to type "DELETE EVERYTHING" to confirm
```

### View Scraping History
```bash
# View recent scraping sessions
python db_admin.py stats

# View database progress
python db_tools.py stats

# Check specific city/niche
python db_tools.py stats --niche restaurants --city Praha
```

---

## 📤 Export Commands

### Master Export (Everything)
```bash
# Export ALL data to one master Excel
python master_exporter.py

# Export all data for specific city
python master_exporter.py --city Praha

# Export all data for specific niche
python master_exporter.py --niche restaurants

# Custom filename
python master_exporter.py --output MASTER_LEADS.xlsx
```

### Quick Export from Database
```bash
# Export to CSV (simple)
python db_tools.py export --niche restaurants --city Praha

# Custom output
python db_tools.py export --niche restaurants --city Praha --output praha_restaurants.csv
```

---

## 🆘 Emergency Recovery

### Check Last Session
```bash
# See what happened in last scrape
python emergency_recovery.py check
```

### Recover Data
```bash
# Recover ALL data
python emergency_recovery.py recover

# Recover specific niche
python emergency_recovery.py recover --niche restaurants

# Recover specific city
python emergency_recovery.py recover --city Praha

# Recover to CSV
python emergency_recovery.py recover --format csv

# Recover websites only (TXT file)
python emergency_recovery.py recover --format txt
```

### Emergency CSV Backup
```bash
# If Excel export fails, get CSV backup
python emergency_recovery.py recover --niche restaurants --city Praha --format csv
```

---

## 🎯 All Available Niches

### Food & Beverage
```bash
--niche restaurants
--niche cafes
--niche bars
--niche bakeries
```

### Beauty & Wellness
```bash
--niche hair_salons
--niche nail_studios
--niche beauty_salons
--niche massage_studios
--niche tattoo_studios
```

### Health & Medical
```bash
--niche dental_clinics
--niche physiotherapy
--niche veterinary
```

### Fitness & Sports
```bash
--niche fitness_gyms
--niche personal_trainers    # ⭐ NEW!
--niche yoga_studios
--niche martial_arts
--niche crossfit             # ⭐ NEW!
```

### Professional Services
```bash
--niche law_offices
--niche accounting
--niche real_estate
--niche insurance
--niche marketing_agencies   # ⭐ NEW!
--niche web_design          # ⭐ NEW!
```

### Automotive
```bash
--niche car_repair
--niche car_wash
--niche car_rental          # ⭐ NEW!
```

### Home Services
```bash
--niche plumbers
--niche electricians
--niche cleaning
--niche florists
--niche interior_design     # ⭐ NEW!
```

### Retail
```bash
--niche pet_shops
--niche clothing_stores
--niche gift_shops
--niche jewelry_stores      # ⭐ NEW!
```

### Education
```bash
--niche language_schools
--niche music_schools
--niche tutoring
--niche driving_schools     # ⭐ NEW!
```

### Entertainment & Events
```bash
--niche event_venues
--niche photo_studios
--niche wedding_services    # ⭐ NEW!
--niche dj_services        # ⭐ NEW!
```

### Accommodation
```bash
--niche hotels             # ⭐ NEW!
--niche hostels            # ⭐ NEW!
--niche apartments         # ⭐ NEW!
```

---

## 🔥 Common Workflows

### Workflow 1: Complete City Over One Day
```bash
# Morning (9 AM) - Food
python scrape_city_SMART.py --city Liberec --niche restaurants,cafes,bars

# Lunch (12 PM) - Beauty & Health
python scrape_city_SMART.py --city Liberec --niche hair_salons,beauty_salons,massage_studios,dental_clinics

# Afternoon (3 PM) - Fitness & Services
python scrape_city_SMART.py --city Liberec --niche fitness_gyms,personal_trainers,yoga_studios,law_offices

# Evening (6 PM) - Retail & More
python scrape_city_SMART.py --city Liberec --niche pet_shops,clothing_stores,gift_shops,florists

# Result: ONE Excel file with everything!
```

### Workflow 2: Overnight Complete Scrape
```bash
# Before bed
python scrape_city_SMART.py --city Praha --complete

# Wake up to 8,000+ leads! ☕
```

### Workflow 3: Quick Daily Leads
```bash
# Monday - Restaurants
python scrape_city_SMART.py --city Brno --niche restaurants --results-per-area 30

# Tuesday - Cafes
python scrape_city_SMART.py --city Brno --niche cafes --results-per-area 30

# Wednesday - Fitness
python scrape_city_SMART.py --city Brno --niche fitness_gyms,personal_trainers --results-per-area 30

# ~300 leads per day, accumulates in one Brno file!
```

### Workflow 4: Multi-City Campaign
```bash
# Praha - Complete
python scrape_city_SMART.py --city Praha --complete

# Wait for completion, then:
# Brno - Complete
python scrape_city_SMART.py --city Brno --complete

# Wait for completion, then:
# Ostrava - Complete
python scrape_city_SMART.py --city Ostrava --complete

# Export master file with everything
python master_exporter.py
```

### Workflow 5: Test Before Big Scrape
```bash
# Test with small sample
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 10 --skip-websites --skip-registry

# Check results in Excel
# If good, run full scrape:
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 50
```

### Workflow 6: Personal Trainers Campaign
```bash
# Scrape all fitness-related businesses
python scrape_city_SMART.py --city Praha --niche personal_trainers,fitness_gyms,yoga_studios,crossfit

# Or just personal trainers
python scrape_city_SMART.py --city Praha --niche personal_trainers

# Export just fitness leads
python db_admin.py export --niche personal_trainers --city Praha
```

---

## 🔍 Filtering & Finding Leads

### In Excel
```bash
# After scraping, open Excel:
# 1. Go to "📊 ALL LEADS" sheet
# 2. Click filter on "Type" column
# 3. Select niche (e.g., "personal_trainers")
# 4. Filter by "Website" = empty for qualified leads
```

### From Command Line
```bash
# Get only businesses without websites
python db_admin.py export --city Praha --niche personal_trainers
# Then filter Excel to "Website" empty column

# Or use emergency recovery for quick export
python emergency_recovery.py recover --niche personal_trainers --city Praha
```

---

## ⚡ Speed Optimization

### Fastest Scraping (No Extra Processing)
```bash
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 30 --skip-websites --skip-registry
# ~5-8 minutes for 300-500 leads
```

### Balanced (Good Quality, Reasonable Speed)
```bash
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 50
# ~15-20 minutes for 500-800 leads with emails
```

### Maximum Quality (Best Data)
```bash
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 100
# ~30-40 minutes for 1000-1500 leads with full data
```

---

## 🛠️ Maintenance Commands

### Check What's Been Scraped
```bash
# View database stats
python db_admin.py stats

# View cities
python db_admin.py cities

# View niches
python db_admin.py niches
```

### Clean Up Old Data
```bash
# Reset specific area if you want fresh data
python db_admin.py reset-city --city Praha

# Or reset specific niche
python db_admin.py reset-niche --niche restaurants
```

### Backup Your Data
```bash
# Export everything to master file (backup)
python master_exporter.py --output BACKUP_$(date +%Y%m%d).xlsx

# Or use emergency recovery
python emergency_recovery.py recover --format csv
```

---

## 💡 Pro Tips

### 1. Build Cities Over Time
```bash
# Don't do everything at once!
# Day 1: Food niches
# Day 2: Beauty niches
# Day 3: Services
# All accumulate in same city file!
```

### 2. Use Database to Never Lose Progress
```bash
# Even if Excel fails, data is in database
python emergency_recovery.py recover
```

### 3. Test Before Big Scrapes
```bash
# Always test with small sample first
python scrape_city_SMART.py --city Praha --niche restaurants --results-per-area 10 --skip-websites
```

### 4. Reset When Needed
```bash
# If scrape was poor quality, reset and try again
python db_admin.py reset-niche --niche restaurants --city Praha
```

### 5. Export Anytime
```bash
# You can export from database anytime
python master_exporter.py --city Praha
```

---

## 🎯 Quick Reference Card

```bash
# SCRAPING
python scrape_city_SMART.py --city [CITY] --niche [NICHE]
python scrape_city_SMART.py --city [CITY] --complete

# DATABASE
python db_admin.py stats
python db_admin.py cities
python db_admin.py niches

# EXPORT
python db_admin.py export --city [CITY]
python master_exporter.py

# RESET
python db_admin.py reset-city --city [CITY]
python db_admin.py reset-niche --niche [NICHE]

# RECOVERY
python emergency_recovery.py check
python emergency_recovery.py recover

# OPTIONS
--skip-websites          # Faster scraping
--skip-registry         # Skip Czech registry lookup
--results-per-area 50   # Control results
--verbose              # Debug mode
```

---

## ✅ You're Ready!

**Start with:**
```bash
# Test personal trainers in Praha
python scrape_city_SMART.py --city Praha --niche personal_trainers --results-per-area 20
```

**Then scale up:**
```bash
# Full personal trainers scrape
python scrape_city_SMART.py --city Praha --niche personal_trainers

# Or complete city
python scrape_city_SMART.py --city Praha --complete
```

Happy scraping! 🚀

# Start the master plan
python scrape_czech_republic.py --start

# It will scrape ALL cities automatically
# Can stop anytime with Ctrl+C
# Resume anytime with:
python scrape_czech_republic.py --resume

# Do Praha your way
python scrape_city_SMART.py --city Praha --complete

# Or do it in parts
python scrape_city_SMART.py --city Praha --niche restaurants,cafes,bars
python scrape_city_SMART.py --city Praha --niche hair_salons,beauty_salons
# etc...