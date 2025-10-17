#!/usr/bin/env python3
"""
FINAL POLISHED LEAD SCRAPER
- Czech registry lookup for businesses without websites
- Better social media extraction
- Clean Excel output organized by area
- Filter by niche in Excel
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
    from scrapers.registry_enhancer import RegistryEnhancer
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
║   🎯 FINAL POLISHED LEAD SCRAPER             ║
║   Registry Lookup • Clean Excel • Perfect    ║
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

    parser = argparse.ArgumentParser(description="Final polished scraper")
    parser.add_argument('--niche', type=str, required=True, help='Business niche')
    parser.add_argument('--location', type=str, default='Praha', help='City/Area')
    parser.add_argument('--max-results', type=int, default=500, help='Target (default: 500)')
    parser.add_argument('--skip-registry', action='store_true', help='Skip registry lookup')
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
    print(f"🗺️  {Fore.CYAN}Areas:{Style.RESET_ALL} {len(areas)} areas × ~{results_per_area} per area")
    print(f"✨ {Fore.CYAN}Features:{Style.RESET_ALL} Registry lookup, social media extraction")
    print(f"📁 {Fore.CYAN}Output:{Style.RESET_ALL} Clean Excel with niche filtering\n")

    # Setup
    logger = setup_logger(verbose=args.verbose)
    
    google_scraper = GoogleMapsScraper(timeout=30, logger=logger)
    website_scraper = WebsiteScraper(timeout=30, delay=2, logger=logger)
    registry_enhancer = RegistryEnhancer(logger=logger)
    deduplicator = Deduplicator(logger=logger)
    prioritizer = LeadPrioritizer(scoring_config=config['scoring'], logger=logger)
    exporter = ExcelExporter(logger=logger)

    all_businesses = []
    
    print(f"{Fore.YELLOW}🔍 Step 1: Google Maps Scraping{Style.RESET_ALL}\n")
    
    # Scrape areas
    with tqdm(total=len(areas), desc="   Areas", unit="area") as pbar:
        for area in areas:
            
            for keyword in keywords[:1]:
                try:
                    pbar.set_description(f"   {area}")
                    
                    businesses = google_scraper.search_businesses_on_maps(
                        keyword,
                        area,
                        max_results=results_per_area
                    )
                    
                    # Tag with niche
                    for b in businesses:
                        b['niche'] = args.niche
                    
                    all_businesses.extend(businesses)
                    
                    if len(all_businesses) >= args.max_results:
                        break
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error in {area}: {e}")
                    continue
            
            pbar.update(1)
            
            # Periodic dedup
            if len(all_businesses) > 200:
                all_businesses = deduplicator.deduplicate(all_businesses)
            
            if len(all_businesses) >= args.max_results:
                break
            
            time.sleep(3)
    
    # Final dedup
    all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
    
    print(f"\n   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")
    
    if not all_businesses:
        print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
        return 1
    
    # Step 2: Website scraping
    print(f"\n{Fore.YELLOW}🌐 Step 2: Website Scraping{Style.RESET_ALL}")
    websites = [b for b in all_businesses if b.get('website')]
    if websites:
        print(f"   Scraping {len(websites)} websites for emails & social...\n")
        all_businesses = website_scraper.scrape_websites(all_businesses)
    
    # Step 3: Registry enhancement
    if not args.skip_registry:
        print(f"\n{Fore.YELLOW}🇨🇿 Step 3: Czech Registry Lookup{Style.RESET_ALL}")
        
        # Find businesses needing enhancement
        needs_enhancement = [
            b for b in all_businesses 
            if not b.get('website') or not b.get('email') or not b.get('phone')
        ]
        
        if needs_enhancement:
            print(f"   Looking up {len(needs_enhancement)} businesses in registry...\n")
            
            with tqdm(total=len(needs_enhancement), desc="   Registry", unit="biz") as pbar:
                for business in needs_enhancement:
                    try:
                        registry_enhancer.enhance_business(business)
                        pbar.update(1)
                    except:
                        pbar.update(1)
                        continue
            
            # Count improvements
            found_websites = sum(1 for b in needs_enhancement if b.get('website'))
            found_emails = sum(1 for b in needs_enhancement if b.get('email'))
            
            print(f"\n   ✓ Found {Fore.GREEN}{found_websites}{Style.RESET_ALL} websites")
            print(f"   ✓ Found {Fore.GREEN}{found_emails}{Style.RESET_ALL} emails")
    else:
        print(f"\n{Fore.YELLOW}🇨🇿 Step 3: Registry Lookup - SKIPPED{Style.RESET_ALL}")
    
    # Step 4: Prioritize
    print(f"\n{Fore.YELLOW}📊 Step 4: Priority Scoring{Style.RESET_ALL}")
    all_businesses = prioritizer.score_leads(all_businesses)
    
    # Stats
    no_website = sum(1 for b in all_businesses if not b.get('website'))
    has_website = sum(1 for b in all_businesses if b.get('website'))
    with_email = sum(1 for b in all_businesses if b.get('email'))
    with_social = sum(1 for b in all_businesses if b.get('instagram') or b.get('facebook'))
    
    print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} without website (QUALIFIED)")
    print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} with website")
    print(f"   ✉️  {Fore.GREEN}{with_email}{Style.RESET_ALL} with email")
    print(f"   📱 {Fore.MAGENTA}{with_social}{Style.RESET_ALL} with social media")
    
    # Step 5: Export
    print(f"\n{Fore.YELLOW}💾 Step 5: Exporting to Clean Excel{Style.RESET_ALL}")
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
    print(f"✉️  With Email: {Fore.GREEN}{with_email}{Style.RESET_ALL}")
    print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}💡 How to use the Excel:{Style.RESET_ALL}")
    print(f"   1. Open '📊 ALL LEADS' sheet")
    print(f"   2. Click filter button on 'Type' column")
    print(f"   3. Choose niche to filter")
    print(f"   4. Start selling! 💰\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())