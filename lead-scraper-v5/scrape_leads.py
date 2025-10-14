#!/usr/bin/env python3
"""
Universal Web Design Lead Scraper
Scrape any niche for potential web design clients using Google Maps
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
    from utils.logger import setup_logger
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.deduplicator import Deduplicator
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    init(autoreset=True)
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    """Print banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║   🎨 WEB DESIGN LEAD SCRAPER                 ║
║   Find Businesses That Need Websites         ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
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
        description="Universal Web Design Lead Scraper - Find businesses that need websites",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrape_leads.py --niche restaurants --location Praha --max-results 20
  python scrape_leads.py --niche hair_salons --location Brno --max-results 15
  python scrape_leads.py --niche cafes --location Ostrava --max-results 10
  
Available niches (from config.yaml):
  - restaurants, cafes, bars, bakeries
  - hair_salons, nail_studios, beauty_salons
  - dental_clinics, fitness_gyms, law_offices
  (and 20+ more!)
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
        help='City name (default: Praha). Options: Praha, Brno, Ostrava, Plzeň, Liberec, Olomouc'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=20,
        help='Maximum number of leads to scrape (default: 20, recommended: 10-50 for testing)'
    )
    parser.add_argument(
        '--skip-websites',
        action='store_true',
        help='Skip website scraping step (faster, but less email/social data)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Validate niche
    if args.niche not in config['niches']:
        print(f"{Fore.RED}❌ Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available niches: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Tip: Add custom niches in config.yaml{Style.RESET_ALL}")
        return 1

    # Get niche configuration
    niche_config = config['niches'][args.niche]
    # Use Czech keywords primarily
    keywords = niche_config['keywords_cz']

    # Display configuration
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche.replace('_', ' ').title()} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
    print(f"⚙️  {Fore.CYAN}Skip Websites:{Style.RESET_ALL} {args.skip_websites}\n")

    # Setup logger
    logger = setup_logger(verbose=args.verbose)
    start_time = time.time()

    try:
        # Initialize components
        print(f"{Fore.YELLOW}⚙️  Initializing Google Maps scraper...{Style.RESET_ALL}")
        
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

        # Step 1: Search Google Maps for businesses
        print(f"\n{Fore.CYAN}━━━ STEP 1: Searching Google Maps ━━━{Style.RESET_ALL}")
        
        all_businesses = []
        
        # Search with each keyword
        for keyword in keywords[:2]:  # Use first 2 keywords for speed
            try:
                print(f"   Searching for: {keyword}...")
                businesses = google_scraper.search_businesses_on_maps(
                    keyword, 
                    args.location, 
                    max_results=args.max_results
                )
                all_businesses.extend(businesses)
                
                if len(all_businesses) >= args.max_results:
                    break
                    
                time.sleep(3)  # Be nice to Google
                
            except Exception as e:
                logger.warning(f"Error searching for {keyword}: {e}")
                continue

        # Deduplicate immediately
        all_businesses = deduplicator.deduplicate(all_businesses)[:args.max_results]
        
        print(f"   ✓ Found {Fore.GREEN}{len(all_businesses)}{Style.RESET_ALL} unique businesses")

        if not all_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found on Google Maps{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 This might happen if:{Style.RESET_ALL}")
            print(f"   • Google is blocking automated requests")
            print(f"   • Try different location or niche")
            print(f"   • Run again in a few minutes")
            return 1

        # Step 2: Scrape Websites (optional)
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Scraping Websites for Details ━━━{Style.RESET_ALL}")
            websites_to_scrape = [b for b in all_businesses if b.get('website')]
            if websites_to_scrape:
                print(f"   Scraping {len(websites_to_scrape)} websites...")
                all_businesses = website_scraper.scrape_websites(all_businesses)
                with_email = sum(1 for b in all_businesses if b.get('email'))
                with_social = sum(1 for b in all_businesses if b.get('instagram') or b.get('facebook'))
                print(f"   ✓ Found {Fore.GREEN}{with_email}{Style.RESET_ALL} emails")
                print(f"   ✓ Found {Fore.GREEN}{with_social}{Style.RESET_ALL} social media profiles")
            else:
                print(f"   ⚠️  No websites to scrape")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Scraping Websites ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL} (use without --skip-websites for more data)")

        # Step 3: Clean data
        print(f"\n{Fore.CYAN}━━━ STEP 3: Cleaning Data ━━━{Style.RESET_ALL}")
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
        print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} leads WITH website (Need analysis)")
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

        print(f"\n{Fore.GREEN}{'='*50}")
        print(f"✨ SCRAPING COMPLETE! ✨")
        print(f"{'='*50}{Style.RESET_ALL}")
        print(f"📊 Total Leads: {Fore.CYAN}{len(all_businesses)}{Style.RESET_ALL}")
        print(f"🔥 No Website (Qualified): {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"🌐 Has Website (Analyze): {Fore.BLUE}{has_website}{Style.RESET_ALL}")
        print(f"⭐ High Priority: {Fore.YELLOW}{high_priority}{Style.RESET_ALL}")
        print(f"💾 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"⏱️  Time: {Fore.CYAN}{minutes}m {seconds}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}\n")

        print(f"📋 {Fore.YELLOW}NEXT STEPS:{Style.RESET_ALL}")
        print(f"   1. Open the Excel file")
        print(f"   2. Sheet '🔥 NO WEBSITE' = Your qualified leads!")
        print(f"   3. Sheet '🌐 HAS WEBSITE' = Send to your website analyzer")
        print(f"   4. Combine all qualified leads and start selling!")
        print(f"\n✅ Happy selling! 💰\n")

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