#!/usr/bin/env python3
"""
SMART LEAD SCRAPER - Combines multiple areas intelligently
Creates ONE Excel per city/niche combo
"""
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from colorama import Fore, Style, init
    import yaml
    from tqdm import tqdm
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.deduplicator import Deduplicator
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    from utils.logger import setup_logger
    from config_districts import get_search_areas
    init(autoreset=True)
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║   🎯 SMART LEAD SCRAPER                      ║
║   Intelligent Area Scraping • One Excel      ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def load_config() -> dict:
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        print(f"{Fore.RED}Error: config.yaml not found{Style.RESET_ALL}")
        sys.exit(1)


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Smart area-based scraper")
    parser.add_argument('--niche', type=str, required=True, help='Business niche')
    parser.add_argument('--location', type=str, default='Praha', help='City')
    parser.add_argument('--max-results', type=int, default=500, help='Total target (default: 500)')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--verbose', action='store_true', help='Verbose')
    args = parser.parse_args()

    # Load config
    config = load_config()

    if args.niche not in config['niches']:
        print(f"{Fore.RED}Unknown niche: {args.niche}{Style.RESET_ALL}")
        return 1

    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']
    
    # Get areas
    areas = get_search_areas(args.location)
    results_per_area = max(50, args.max_results // len(areas))

    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:2])}")
    print(f"🗺️  {Fore.CYAN}Strategy:{Style.RESET_ALL} {len(areas)} areas × ~{results_per_area} results")
    print(f"📁 {Fore.CYAN}Output:{Style.RESET_ALL} One combined Excel file\n")

    # Setup
    logger = setup_logger(verbose=args.verbose)
    
    google_scraper = GoogleMapsScraper(timeout=30, logger=logger)
    website_scraper = WebsiteScraper(timeout=30, delay=2, logger=logger)
    deduplicator = Deduplicator(logger=logger)
    prioritizer = LeadPrioritizer(scoring_config=config['scoring'], logger=logger)
    exporter = ExcelExporter(logger=logger)

    all_businesses = []
    
    print(f"{Fore.YELLOW}🔍 Scraping areas...{Style.RESET_ALL}\n")
    
    # Process areas with progress bar
    with tqdm(total=len(areas), desc="   Areas", unit="area") as pbar:
        for area in areas:
            
            # Search with first keyword
            for keyword in keywords[:1]:
                try:
                    pbar.set_description(f"   {area} ({keyword})")
                    
                    businesses = google_scraper.search_businesses_on_maps(
                        keyword,
                        area,
                        max_results=results_per_area
                    )
                    
                    all_businesses.extend(businesses)
                    
                    if len(all_businesses) >= args.max_results:
                        break
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error in {area}: {e}")
                    continue
            
            pbar.update(1)
            
            # Deduplicate periodically
            if len(all_businesses) > 200:
                all_businesses = deduplicator.deduplicate(all_businesses)
            
            if len(all_businesses) >= args.max_results:
                print(f"\n   ✓ Target reached!")
                break
            
            time.sleep(3)
    
    # Final deduplication
    all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
    
    print(f"\n   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")
    
    if not all_businesses:
        print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
        return 1
    
    # Website scraping
    if not args.skip_websites:
        print(f"\n{Fore.YELLOW}🌐 Scraping websites...{Style.RESET_ALL}")
        websites = [b for b in all_businesses if b.get('website')]
        if websites:
            print(f"   Found {len(websites)} websites to scrape\n")
            all_businesses = website_scraper.scrape_websites(all_businesses)
            emails = sum(1 for b in all_businesses if b.get('email'))
            print(f"\n   ✓ Found {Fore.GREEN}{emails}{Style.RESET_ALL} emails")
    
    # Prioritize
    print(f"\n{Fore.YELLOW}📊 Scoring leads...{Style.RESET_ALL}")
    all_businesses = prioritizer.score_leads(all_businesses)
    
    # Stats
    no_website = sum(1 for b in all_businesses if not b.get('website'))
    has_website = sum(1 for b in all_businesses if b.get('website'))
    high_priority = sum(1 for b in all_businesses if b.get('priority_score', 0) >= 75)
    
    print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} without website (QUALIFIED)")
    print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} with website")
    print(f"   ⭐ {Fore.YELLOW}{high_priority}{Style.RESET_ALL} high-priority")
    
    # Export
    print(f"\n{Fore.YELLOW}💾 Exporting to Excel...{Style.RESET_ALL}")
    output_file = exporter.export(
        all_businesses,
        niche=args.niche,
        location=args.location
    )
    
    # Cleanup
    google_scraper.close()
    website_scraper.close()
    
    # Summary
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"✨ SCRAPING COMPLETE!")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"📊 Total: {Fore.CYAN}{len(all_businesses)}{Style.RESET_ALL}")
    print(f"🔥 No Website: {Fore.GREEN}{no_website}{Style.RESET_ALL}")
    print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())