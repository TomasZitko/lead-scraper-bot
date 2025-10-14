#!/usr/bin/env python3
"""
Production Web Design Lead Scraper
District-based searching for unlimited Czech Republic coverage
"""
import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
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
    from config_districts import get_search_areas, estimate_search_count, get_all_czech_cities
    init(autoreset=True)
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run: pip install -r requirements.txt")
    print("And: pip install undetected-chromedriver")
    sys.exit(1)


def print_banner():
    """Print banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🎨 PRODUCTION WEB DESIGN LEAD SCRAPER                  ║
║   District-Based Searching • Unlimited Results           ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.yaml not found{Style.RESET_ALL}")
        sys.exit(1)


def main():
    """Main scraping function"""
    print_banner()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Production Lead Scraper - District-based searching for unlimited results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 1000 restaurants across Praha districts
  python scrape_leads.py --niche restaurants --location Praha --max-results 1000
  
  # 500 hair salons in Brno
  python scrape_leads.py --niche hair_salons --location Brno --max-results 500
  
  # 100 cafes in smaller city
  python scrape_leads.py --niche cafes --location Liberec --max-results 100
  
District-based searching automatically divides large cities into districts
to bypass Google Maps 120-result limit and get complete coverage!
        """
    )

    parser.add_argument(
        '--niche',
        type=str,
        required=True,
        help='Business niche to scrape (e.g., restaurants, hair_salons, cafes)'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='Praha',
        help='City name (default: Praha)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Target number of leads (default: 100, can go to 1000+)'
    )
    parser.add_argument(
        '--skip-websites',
        action='store_true',
        help='Skip website scraping step (faster)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--list-cities',
        action='store_true',
        help='List all available Czech cities and exit'
    )

    args = parser.parse_args()

    # List cities if requested
    if args.list_cities:
        print(f"\n{Fore.CYAN}📍 Available Czech Cities:{Style.RESET_ALL}\n")
        cities = get_all_czech_cities()
        for i, city in enumerate(cities, 1):
            areas = get_search_areas(city)
            print(f"  {i:2d}. {city:<20} ({len(areas)} search areas)")
        print()
        return 0

    # Load configuration
    config = load_config()

    # Validate niche
    if args.niche not in config['niches']:
        print(f"{Fore.RED}❌ Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available niches: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        return 1

    # Get niche configuration
    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']

    # Get search areas for the city
    search_areas = get_search_areas(args.location)
    
    # Calculate distribution
    results_per_area = max(10, args.max_results // len(search_areas))
    
    # Estimate
    estimation = estimate_search_count(args.location, args.max_results)

    # Display configuration
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche.replace('_', ' ').title()} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
    print(f"🗺️  {Fore.CYAN}Search Strategy:{Style.RESET_ALL} {len(search_areas)} areas × ~{results_per_area} results/area")
    print(f"⏱️  {Fore.CYAN}Estimated Time:{Style.RESET_ALL} ~{estimation['estimated_time_minutes']} minutes")
    print(f"⚙️  {Fore.CYAN}Skip Websites:{Style.RESET_ALL} {args.skip_websites}\n")

    # Setup logger
    logger = setup_logger(verbose=args.verbose)
    start_time = time.time()

    try:
        # Initialize components
        print(f"{Fore.YELLOW}⚙️  Initializing stealth scraper...{Style.RESET_ALL}")
        
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

        # Step 1: District-based searching
        print(f"\n{Fore.CYAN}━━━ STEP 1: District-Based Google Maps Search ━━━{Style.RESET_ALL}")
        print(f"   Searching {len(search_areas)} areas with {len(keywords[:2])} keywords each\n")
        
        all_businesses = []
        successful_searches = 0
        failed_searches = 0

        # Progress bar for areas
        with tqdm(total=len(search_areas), desc="   Areas", unit="area") as pbar_areas:
            for area in search_areas:
                area_businesses = []
                
                # Search with first 2 keywords for each area
                for keyword in keywords[:2]:
                    try:
                        pbar_areas.set_description(f"   {area} ({keyword})")
                        
                        businesses = google_scraper.search_businesses_on_maps(
                            keyword,
                            area,
                            max_results=results_per_area
                        )
                        
                        area_businesses.extend(businesses)
                        
                        if businesses:
                            successful_searches += 1
                        else:
                            failed_searches += 1
                        
                        # Small delay between keywords
                        time.sleep(2)
                        
                        # Check if we have enough results
                        if len(all_businesses) >= args.max_results:
                            break
                        
                    except Exception as e:
                        logger.warning(f"Error searching {area} for {keyword}: {e}")
                        failed_searches += 1
                        continue
                
                all_businesses.extend(area_businesses)
                pbar_areas.update(1)
                
                # Deduplicate after each area to save memory
                if len(all_businesses) > 200:
                    all_businesses = deduplicator.deduplicate(all_businesses)
                
                # Check if we have enough
                if len(all_businesses) >= args.max_results:
                    print(f"\n   ✓ Target reached! Found {len(all_businesses)} businesses")
                    break
                
                # Delay between areas (be nice to Google)
                time.sleep(3)

        # Final deduplication
        all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
        
        print(f"\n   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")
        print(f"   📊 Success rate: {successful_searches}/{successful_searches+failed_searches} searches")

        if not all_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Possible reasons:{Style.RESET_ALL}")
            print(f"   • Google is blocking requests (wait 30 min and try again)")
            print(f"   • City/district names incorrect")
            print(f"   • Niche has very few businesses in this area")
            return 1

        # Step 2: Scrape Websites (optional)
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Scraping Websites for Contact Info ━━━{Style.RESET_ALL}")
            websites_to_scrape = [b for b in all_businesses if b.get('website')]
            if websites_to_scrape:
                print(f"   Found {len(websites_to_scrape)} websites to scrape\n")
                all_businesses = website_scraper.scrape_websites(all_businesses)
                with_email = sum(1 for b in all_businesses if b.get('email'))
                with_social = sum(1 for b in all_businesses if b.get('instagram') or b.get('facebook'))
                print(f"\n   ✓ Found {Fore.GREEN}{with_email}{Style.RESET_ALL} emails")
                print(f"   ✓ Found {Fore.GREEN}{with_social}{Style.RESET_ALL} social media profiles")
            else:
                print(f"   ⚠️  No websites to scrape")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Scraping Websites ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL}")

        # Step 3: Clean data
        print(f"\n{Fore.CYAN}━━━ STEP 3: Cleaning & Validating Data ━━━{Style.RESET_ALL}")
        all_businesses = deduplicator.remove_invalid_entries(all_businesses)
        print(f"   ✓ {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} valid businesses")

        # Step 4: Prioritize
        print(f"\n{Fore.CYAN}━━━ STEP 4: Calculating Priority Scores ━━━{Style.RESET_ALL}")
        all_businesses = prioritizer.score_leads(all_businesses)
        
        # Count by website status
        no_website = sum(1 for b in all_businesses if not b.get('website'))
        has_website = sum(1 for b in all_businesses if b.get('website'))
        high_priority = sum(1 for b in all_businesses if b.get('priority_score', 0) >= 75)
        
        print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} leads WITHOUT website (Qualified!)")
        print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} leads WITH website (Send to analyzer)")
        print(f"   ⭐ {Fore.YELLOW}{high_priority}{Style.RESET_ALL} high-priority leads (75+ score)")

        # Step 5: Export
        print(f"\n{Fore.CYAN}━━━ STEP 5: Exporting to Excel ━━━{Style.RESET_ALL}")
        output_file = exporter.export(
            all_businesses,
            niche=args.niche,
            location=args.location
        )

        # Cleanup
        google_scraper.close()
        website_scraper.close()

        # Final Summary
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"✨ SCRAPING COMPLETE! ✨")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"📊 Total Leads: {Fore.CYAN}{len(all_businesses)}{Style.RESET_ALL}")
        print(f"🔥 No Website (QUALIFIED): {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"🌐 Has Website (Analyze): {Fore.BLUE}{has_website}{Style.RESET_ALL}")
        print(f"⭐ High Priority: {Fore.YELLOW}{high_priority}{Style.RESET_ALL}")
        print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"⏱️  Time: {Fore.CYAN}{minutes}m {seconds}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")

        print(f"📋 {Fore.YELLOW}NEXT STEPS:{Style.RESET_ALL}")
        print(f"   1. Open Excel file in data/exports/")
        print(f"   2. Sheet '🔥 NO WEBSITE' = {no_website} qualified leads!")
        print(f"   3. Sheet '🌐 HAS WEBSITE' = Send {has_website} to your analyzer bot")
        print(f"   4. Start selling! 💰")
        print(f"\n✅ Happy selling! 🚀\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Scraping interrupted by user{Style.RESET_ALL}")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        print(f"Check logs/ folder for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())