# 🚀 Quick Start Guide

## Installation Steps

1. **Navigate to the project directory**
   ```bash
   cd /mnt/c/Users/tomas_48vauln/Documents/leads-scraper
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or using Python 3 explicitly:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Test the installation**
   ```bash
   python main.py --help
   ```

## First Run

### Quick Test (Recommended)

Test with a small dataset to ensure everything works:
```bash
python main.py --niche restaurants --location Praha --max-results 5 --skip-websites
```

This will:
- Scrape 5 restaurants in Praha
- Skip website scraping for speed
- Generate an Excel file in `data/exports/`

### Full Featured Test

Once the quick test works, try with website scraping:
```bash
python main.py --niche cafes --location Brno --max-results 10
```

## Expected Output

You should see:
1. ✅ Banner and configuration summary
2. ✅ Progress for each scraping step
3. ✅ Summary with counts and timing
4. ✅ Excel file in `data/exports/` directory

## Troubleshooting

### ModuleNotFoundError

If you see "No module named 'X'", run:
```bash
pip install -r requirements.txt
```

### Selenium/ChromeDriver Issues

The scraper will automatically download ChromeDriver. If it fails:
1. Ensure you have Chrome or Chromium installed
2. Check internet connectivity
3. Use `--skip-websites` flag to bypass Selenium

### No Results Found

- Try different keywords in `config.yaml`
- Check if the website rejstrik-firem.kurzy.cz is accessible
- Review logs in `logs/` directory

## Next Steps

Once testing is successful:
1. Review and customize `config.yaml` for your niches
2. Add Google Maps API key to `.env` for better results (optional)
3. Run full production scraping with higher `--max-results`

## Production Run Example

```bash
python main.py --all-niches --location Praha --max-results 500 --verbose
```

---

**Happy Scraping! 🎯**
