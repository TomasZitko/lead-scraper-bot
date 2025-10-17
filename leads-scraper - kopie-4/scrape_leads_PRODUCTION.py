#!/usr/bin/env python3
"""
Production District-Based Lead Scraper
Unlimited coverage using district segmentation
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
    from utils.logger import setup_logger
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.deduplicator import Deduplicator
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    from config_districts import get_search_areas, get_all_czech_cities
    init(autoreset=True)
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🎨 PRODUCTION DISTRICT-BASED SCRAPER                   ║
║   Unlimited Coverage • No Database • District Strategy   ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def load_config() -> dict:
    """Load configuration"""
    try:
        with open("config.yaml", 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.yaml not found{Style.RESET_ALL}")
        sys.exit(1)


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="District-Based Scraper - Get unlimited results",
        epilog="""
Examples:
  # 1000 restaurants across Praha districts
  python scrape_leads_PRODUCTION.py --niche restaurants --location Praha --max-results 1000
  
  # List all available cities
  python scrape_leads_PRODUCTION.py --list-cities
        """
    )

    parser.add_argument('--niche', type=str, help='Business niche')
    parser.add_argument('--location', type=str, default='Praha', help='City')
    parser.add_argument('--max-results', type=int, default=200, help='Target results')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--list-cities', action='store_true', help='List cities and exit')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # List cities
    if args.list_cities:
        print(f"\n{Fore.CYAN}📍 Available Cities:{Style.RESET_ALL}\n")
        cities = get_all_czech_cities()
        for i, city in enumerate(cities, 1):
            areas = get_search_areas(city)
            print(f"  {i:2d}. {city:<20} ({len(areas)} areas)")
        print()
        return 0

    # Validate niche
    if not args.niche:
        print(f"{Fore.RED}Error: --niche required{Style.RESET_ALL}")
        parser.print_help()
        return 1

    # Load config
    config = load_config()

    if args.niche not in config['niches']:
        print(f"{Fore.RED}Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        return 1

    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']
    
    # Get search areas
    search_areas = get_search_areas(args.location)
    results_per_area = max(10, args.max_results // len(search_areas))

    # Display config
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}")
    print(f"🗺️  {Fore.CYAN}Strategy:{Style.RESET_ALL} {len(search_areas)} areas × ~{results_per_area} results\n")

    # Setup
    logger = setup_logger(verbose=args.verbose)
    start_time = time.time()

    try:
        # Initialize
        print(f"{Fore.YELLOW}⚙️  Initializing...{Style.RESET_ALL}")
        
        google_scraper = GoogleMapsScraper(
            timeout=config['scraping']['timeout'],
            logger=logger
        )

        website_scraper = WebsiteScraper(
            timeout=config['scraping']['timeout'],
            delay=config['scraping']['delay_between_requests'],
            logger=logger
        )

        deduplicator = Deduplicator(logger=logger)
        prioritizer = LeadPrioritizer(scoring_config=config['scoring'], logger=logger)
        exporter = ExcelExporter(logger=logger)

        # STEP 1: District-based search
        print(f"\n{Fore.CYAN}━━━ STEP 1: District-Based Search ━━━{Style.RESET_ALL}")
        print(f"   Searching {len(search_areas)} areas\n")
        
        all_businesses = []
        
        with tqdm(total=len(search_areas), desc="   Areas", unit="area") as pbar:
            for area in search_areas:
                
                for keyword in keywords[:2]:
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
                        logger.warning(f"Error in {area} for {keyword}: {e}")
                        continue
                
                pbar.update(1)
                
                # Deduplicate periodically
                if len(all_businesses) > 200:
                    all_businesses = deduplicator.deduplicate(all_businesses)
                
                if len(all_businesses) >= args.max_results:
                    break
                
                time.sleep(3)

        # Final deduplication
        all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
        
        print(f"\n   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")

        if not all_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
            return 1

        # STEP 2: Website scraping
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            websites = [b for b in all_businesses if b.get('website')]
            if websites:
                print(f"   Scraping {len(websites)} websites\n")
                all_businesses = website_scraper.scrape_websites(all_businesses)
                emails = sum(1 for b in all_businesses if b.get('email'))
                print(f"\n   ✓ Found {Fore.GREEN}{emails}{Style.RESET_ALL} emails")
            else:
                print(f"   ⚠️  No websites")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL}")

        # STEP 3: Clean
        print(f"\n{Fore.CYAN}━━━ STEP 3: Cleaning ━━━{Style.RESET_ALL}")
        all_businesses = deduplicator.remove_invalid_entries(all_businesses)
        print(f"   ✓ {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} valid")

        # STEP 4: Prioritize
        print(f"\n{Fore.CYAN}━━━ STEP 4: Priority Scoring ━━━{Style.RESET_ALL}")
        all_businesses = prioritizer.score_leads(all_businesses)
        
        no_website = sum(1 for b in all_businesses if not b.get('website'))
        has_website = sum(1 for b in all_businesses if b.get('website'))
        high_priority = sum(1 for b in all_businesses if b.get('priority_score', 0) >= 75)
        
        print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} WITHOUT website")
        print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} WITH website")
        print(f"   ⭐ {Fore.YELLOW}{high_priority}{Style.RESET_ALL} high-priority")

        # STEP 5: Export
        print(f"\n{Fore.CYAN}━━━ STEP 5: Export ━━━{Style.RESET_ALL}")
        output_file = exporter.export(
            all_businesses,
            niche=args.niche,
            location=args.location
        )

        # Cleanup
        google_scraper.close()
        website_scraper.close()

        # Summary
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"✨ COMPLETE!")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"📊 Total: {Fore.CYAN}{len(all_businesses)}{Style.RESET_ALL}")
        print(f"🔥 No Website: {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"⏱️  Time: {Fore.CYAN}{minutes}m {seconds}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Interrupted{Style.RESET_ALL}")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())