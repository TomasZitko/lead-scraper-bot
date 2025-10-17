#!/usr/bin/env python3
"""
Simple Lead Scraper - No Database Version
Quick testing and small scraping jobs
"""
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from colorama import Fore, Style, init
    import yaml
    from utils.logger import setup_logger
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.deduplicator import Deduplicator
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    init(autoreset=True)
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🎨 SIMPLE LEAD SCRAPER                                 ║
║   Quick Testing • No Database • Fast Results             ║
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
        description="Simple Lead Scraper - Quick testing without database",
        epilog="""
Examples:
  # Quick test - 20 restaurants
  python scrape_leads.py --niche restaurants --location Praha --max-results 20
  
  # Skip website scraping for speed
  python scrape_leads.py --niche cafes --location Brno --max-results 50 --skip-websites
        """
    )

    parser.add_argument('--niche', type=str, required=True, help='Business niche')
    parser.add_argument('--location', type=str, default='Praha', help='City (default: Praha)')
    parser.add_argument('--max-results', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Validate niche
    if args.niche not in config['niches']:
        print(f"{Fore.RED}Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        return 1

    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']

    # Display config
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}")
    print(f"⚡ {Fore.CYAN}Mode:{Style.RESET_ALL} Simple (no database)\n")

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
        
        prioritizer = LeadPrioritizer(
            scoring_config=config['scoring'],
            logger=logger
        )
        
        exporter = ExcelExporter(logger=logger)

        # STEP 1: Search Google Maps
        print(f"\n{Fore.CYAN}━━━ STEP 1: Google Maps Search ━━━{Style.RESET_ALL}")
        
        all_businesses = []
        
        # Search with first 2 keywords
        for keyword in keywords[:2]:
            try:
                print(f"   Searching: {keyword}...")
                businesses = google_scraper.search_businesses_on_maps(
                    keyword,
                    args.location,
                    max_results=args.max_results
                )
                all_businesses.extend(businesses)
                
                if len(all_businesses) >= args.max_results:
                    break
                
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Error for {keyword}: {e}")
                continue

        # Deduplicate
        all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
        
        print(f"   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")

        if not all_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
            return 1

        # STEP 2: Scrape websites
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            websites = [b for b in all_businesses if b.get('website')]
            if websites:
                print(f"   Scraping {len(websites)} websites...")
                all_businesses = website_scraper.scrape_websites(all_businesses)
                emails = sum(1 for b in all_businesses if b.get('email'))
                print(f"   ✓ Found {Fore.GREEN}{emails}{Style.RESET_ALL} emails")
            else:
                print(f"   ⚠️  No websites to scrape")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL}")

        # STEP 3: Clean
        print(f"\n{Fore.CYAN}━━━ STEP 3: Cleaning ━━━{Style.RESET_ALL}")
        all_businesses = deduplicator.remove_invalid_entries(all_businesses)
        print(f"   ✓ {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} valid businesses")

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