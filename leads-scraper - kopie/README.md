# 🇨🇿 Czech Business Lead Scraper

A professional multi-niche business lead scraper for Czech businesses. Generate prioritized lead lists for web design agencies by scraping business registries, Google Maps, and individual websites.

## ✨ Features

- **Multi-Source Scraping**: Combines data from Czech business registry, Google Maps, and individual websites
- **Smart Deduplication**: Removes duplicates using fuzzy matching and IČO validation
- **Priority Scoring**: Automatically scores leads based on opportunity (no website = highest priority)
- **Professional Excel Export**: Multiple sheets with color-coded priorities and summary statistics
- **Czech Language Support**: Handles Czech characters and business-specific patterns
- **Robust Error Handling**: Retry logic, rate limiting, and graceful degradation
- **CLI Interface**: Easy-to-use command-line interface with progress tracking

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Chrome/Chromium (for Selenium-based Google Maps scraping)

### Setup

1. **Clone or download this repository**

2. **Navigate to the project directory**
   ```bash
   cd leads-scraper
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google Maps API key if you have one
   ```

## 🚀 Usage

### Basic Usage

Scrape restaurants in Praha:
```bash
python main.py --niche restaurants --location Praha
```

### Multiple Niches

Scrape multiple niches at once:
```bash
python main.py --niche "restaurants,cafes,hair_salons" --location Brno
```

### All Configured Niches

Scrape all niches defined in config.yaml:
```bash
python main.py --all-niches --location Ostrava
```

### Limit Results

Limit the number of results per niche:
```bash
python main.py --niche cafes --location Praha --max-results 50
```

### Skip Website Scraping

Skip the website scraping step (faster, but less email/social media data):
```bash
python main.py --niche restaurants --location Brno --skip-websites
```

### Custom Output Filename

Specify a custom output filename:
```bash
python main.py --niche hair_salons --location Praha --output my_leads.xlsx
```

### Verbose Logging

Enable detailed logging output:
```bash
python main.py --niche restaurants --location Praha --verbose
```

## 📋 Configuration

Edit `config.yaml` to customize:

- **Niches**: Add or modify business niches with Czech and English keywords
- **Locations**: Configure default cities to scrape
- **Scraping Settings**: Adjust delays, timeouts, and retry attempts
- **Scoring Weights**: Modify priority scoring criteria
- **Output Columns**: Choose which fields to include in Excel export

### Example Niche Configuration

```yaml
niches:
  restaurants:
    keywords_cz: ["restaurace", "restaurant", "hostinec"]
    keywords_en: ["restaurant", "bistro"]
  your_custom_niche:
    keywords_cz: ["vaše klíčová slova"]
    keywords_en: ["your keywords"]
```

## 📊 Output Format

The scraper generates an Excel file with multiple sheets:

1. **High Priority (75+)**: Businesses with high opportunity scores
2. **Medium Priority (50-74)**: Moderate opportunity businesses
3. **Low Priority (<50)**: Lower priority leads
4. **All Leads**: Complete dataset
5. **Summary**: Statistics and distribution

### Priority Scoring

Leads are scored based on:
- **No website**: +100 points (IMMEDIATE OPPORTUNITY)
- **Poor website quality**: +75 points (HIGH PRIORITY)
- **No email**: +50 points
- **No social media**: +25 points
- **No Google reviews**: +20 points
- **Low Google rating**: -10 points

## 📁 Project Structure

```
leads-scraper/
├── main.py                      # CLI controller
├── config.yaml                  # Configuration
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── .env.example                 # Environment template
├── scrapers/
│   ├── registry_scraper.py     # Czech registry scraper
│   ├── google_maps_scraper.py  # Google Maps enrichment
│   └── website_scraper.py      # Website scraping
├── processors/
│   ├── data_merger.py          # Merge data sources
│   ├── deduplicator.py         # Remove duplicates
│   └── prioritizer.py          # Score leads
├── utils/
│   ├── email_extractor.py      # Extract emails
│   ├── validators.py           # Validate data
│   └── logger.py               # Logging
├── exporters/
│   └── excel_exporter.py       # Export to Excel
├── data/
│   ├── raw/                    # Raw scraping data
│   ├── processed/              # Processed data
│   └── exports/                # Excel exports
└── logs/                       # Application logs
```

## 🔧 Advanced Options

### Google Maps API

For better Google Maps data, you can use the official API:

1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Places API
3. Add your API key to `.env`:
   ```
   GOOGLE_MAPS_API_KEY=your_api_key_here
   ```
4. Set `use_google_api: true` in `config.yaml`

### Custom Configuration File

Use a different configuration file:
```bash
python main.py --niche restaurants --location Praha --config custom_config.yaml
```

## 🛠️ Troubleshooting

### Selenium Issues

If Selenium fails to initialize:
1. Ensure Chrome/Chromium is installed
2. The scraper will automatically download ChromeDriver
3. Check that you have internet connectivity

### Empty Results

If no businesses are found:
1. Check your keywords in `config.yaml`
2. Try different location names
3. The Czech business registry might be temporarily unavailable
4. Check logs in `logs/` directory for detailed errors

### Rate Limiting

If you encounter rate limiting:
1. Increase `delay_between_requests` in `config.yaml`
2. Reduce `max_results_per_niche`
3. Use the `--skip-websites` flag

## 📝 Examples

### Quick Test Run

Test with a small dataset:
```bash
python main.py --niche restaurants --location Praha --max-results 10
```

### Full Production Run

Complete scraping with all data:
```bash
python main.py --all-niches --location Praha --max-results 500 --verbose
```

### Target High-Value Leads

Focus on businesses most likely to need websites:
```bash
python main.py --niche "hair_salons,nail_studios" --location Brno --max-results 200
```

## 🎯 Best Practices

1. **Start Small**: Test with `--max-results 10` before full runs
2. **Be Respectful**: Don't scrape too aggressively (respect rate limits)
3. **Regular Updates**: Re-run monthly to keep leads fresh
4. **Verify Data**: Always manually verify high-priority leads
5. **GDPR Compliance**: Use scraped data responsibly and in compliance with regulations

## 📄 License

This tool is for educational and business development purposes. Always respect website terms of service and applicable laws when scraping data.

## 🤝 Support

For issues or questions:
1. Check the `logs/` directory for detailed error logs
2. Review this README and configuration files
3. Ensure all dependencies are correctly installed

## 🚀 Future Enhancements

Potential improvements:
- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Resume capability for interrupted scraping
- [ ] Multi-threading for faster processing
- [ ] Web dashboard for results
- [ ] Email validation API integration
- [ ] Automated email outreach capability

---

**Made with ❤️ for web design agencies seeking quality leads in Czech Republic**
