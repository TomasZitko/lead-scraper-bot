#!/usr/bin/env python3
"""
PRODUCTION LEAD SCRAPER - Final Version
Complete extraction • Database memory • Never lose progress
"""
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

try:
    from colorama import Fore, Style, init
    import yaml
    from tqdm import tqdm
    from database_manager import DatabaseManager
    from config_districts import get_search_areas
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    from utils.logger import setup_logger
    init(autoreset=True)
except ImportError as e:
    print(f"Error: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║   🎯 PRODUCTION LEAD SCRAPER                                     ║
║   Complete Extraction • Database Memory • Zero Duplicates        ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def print_dashboard(db: DatabaseManager, niche: str = None, city: str = None):
    """Show scraping dashboard"""
    stats = db.get_progress_stats(niche, city)
    
    print(f"\n{Fore.YELLOW}📊 DASHBOARD{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Total Businesses: {Fore.GREEN}{stats['total_businesses']}{Style.RESET_ALL}")
    
    if stats['by_city']:
        print(f"\n{Fore.CYAN}Top Cities:{Style.RESET_ALL}")
        for city_stat in stats['by_city'][:5]:
            print(f"  • {city_stat['city']}: {city_stat['count']} businesses")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


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
        description="Production Lead Scraper - Never lose progress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 500 restaurants in Praha
  python scrape_leads_PRO.py --niche restaurants --location Praha --max-results 500
  
  # View dashboard
  python scrape_leads_PRO.py --dashboard
  
  # Force re-scrape (ignore history)
  python scrape_leads_PRO.py --niche restaurants --location Praha --max-results 500 --force-rescrape
        """
    )

    parser.add_argument('--niche', type=str, help='Business niche (required unless --dashboard)')
    parser.add_argument('--location', type=str, default='Praha', help='City name (default: Praha)')
    parser.add_argument('--max-results', type=int, default=200, help='Target leads (default: 200)')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--force-rescrape', action='store_true', help='Ignore scraping history')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard and exit')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Setup
    logger = setup_logger(verbose=args.verbose)
    config = load_config()
    db = DatabaseManager()

    # Dashboard mode
    if args.dashboard:
        print_dashboard(db, args.niche, args.location)
        db.close()
        return 0

    # Validate niche
    if not args.niche:
        print(f"{Fore.RED}Error: --niche required (or use --dashboard){Style.RESET_ALL}")
        parser.print_help()
        return 1

    if args.niche not in config['niches']:
        print(f"{Fore.RED}Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        return 1

    logger.info(f"🚀 Starting scraper: {args.max_results} {args.niche} in {args.location}")

    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']
    
    # Get search areas
    search_areas = get_search_areas(args.location)
    results_per_area = max(10, args.max_results // len(search_areas))
    
    # Show config
    print_dashboard(db, args.niche, args.location)
    
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}")
    print(f"🗺️  {Fore.CYAN}Areas:{Style.RESET_ALL} {len(search_areas)} areas × ~{results_per_area} results/area")
    print(f"💾 {Fore.CYAN}Database:{Style.RESET_ALL} Auto-save with deduplication\n")

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

        prioritizer = LeadPrioritizer(
            scoring_config=config['scoring'],
            logger=logger
        )
        
        exporter = ExcelExporter(logger=logger)

        # Start session
        session_id = db.start_session(args.niche, args.location)
        logger.info(f"Started session #{session_id}")

        # STEP 1: Google Maps Search
        print(f"\n{Fore.CYAN}━━━ STEP 1: Google Maps Search ━━━{Style.RESET_ALL}")
        print(f"   Extracting from {len(search_areas)} areas\n")
        
        all_businesses = []
        new_count = 0
        existing_count = 0
        
        with tqdm(total=len(search_areas), desc="   Areas", unit="area") as pbar:
            for area in search_areas:
                
                for keyword in keywords[:2]:
                    
                    # Check if already scraped
                    if not args.force_rescrape and db.is_area_scraped(args.niche, args.location, area, keyword):
                        logger.info(f"⊘ Skipping {area} ({keyword}) - already scraped")
                        continue
                    
                    try:
                        pbar.set_description(f"   {area} ({keyword})")
                        
                        # Search
                        businesses = google_scraper.search_businesses_on_maps(
                            keyword,
                            area,
                            max_results=results_per_area
                        )
                        
                        # Add to database
                        for business in businesses:
                            business['niche'] = args.niche
                            business['city'] = args.location
                            
                            exists = db.business_exists(
                                business.get('business_name', ''),
                                business.get('address'),
                                business.get('google_place_id')
                            )
                            
                            if exists:
                                existing_count += 1
                            else:
                                new_count += 1
                            
                            db.add_business(business)
                            all_businesses.append(business)
                        
                        # Mark as scraped
                        db.mark_area_scraped(args.niche, args.location, area, keyword, len(businesses))
                        
                        if len(all_businesses) >= args.max_results:
                            break
                        
                        time.sleep(3)
                        
                    except Exception as e:
                        logger.warning(f"Error in {area} for {keyword}: {e}")
                        continue
                
                pbar.update(1)
                
                if len(all_businesses) >= args.max_results:
                    break
                
                time.sleep(2)

        # Deduplicate
        unique_businesses = []
        seen = set()
        for b in all_businesses:
            key = (b.get('business_name', '').lower(), b.get('address', ''))
            if key not in seen:
                seen.add(key)
                unique_businesses.append(b)
        
        unique_businesses = unique_businesses[:args.max_results]
        
        print(f"\n   ✓ Found {Fore.GREEN}{len(unique_businesses)}{Style.RESET_ALL} unique businesses")
        print(f"   📊 {Fore.CYAN}{new_count}{Style.RESET_ALL} new | {Fore.YELLOW}{existing_count}{Style.RESET_ALL} existing")

        if not unique_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
            db.end_session(session_id, 0, 'no_results')
            db.close()
            return 1

        # STEP 2: Website scraping
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            websites = [b for b in unique_businesses if b.get('website') and not b.get('email')]
            if websites:
                print(f"   Scraping {len(websites)} websites\n")
                unique_businesses = website_scraper.scrape_websites(unique_businesses)
            else:
                print(f"   ✓ All processed")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL}")

        # STEP 3: Prioritize
        print(f"\n{Fore.CYAN}━━━ STEP 3: Priority Scoring ━━━{Style.RESET_ALL}")
        unique_businesses = prioritizer.score_leads(unique_businesses)
        
        no_website = sum(1 for b in unique_businesses if not b.get('website'))
        has_website = sum(1 for b in unique_businesses if b.get('website'))
        high_priority = sum(1 for b in unique_businesses if b.get('priority_score', 0) >= 75)
        
        print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} WITHOUT website")
        print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} WITH website")
        print(f"   ⭐ {Fore.YELLOW}{high_priority}{Style.RESET_ALL} high-priority")

        # STEP 4: Export
        print(f"\n{Fore.CYAN}━━━ STEP 4: Export ━━━{Style.RESET_ALL}")
        output_file = exporter.export(
            unique_businesses,
            niche=args.niche,
            location=args.location
        )

        # Update session
        db.end_session(session_id, len(unique_businesses), 'completed')

        # Cleanup
        google_scraper.close()
        website_scraper.close()
        db.close()

        # Summary
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✨ SCRAPING COMPLETE!")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"📊 Total: {Fore.CYAN}{len(unique_businesses)}{Style.RESET_ALL}")
        print(f"🔥 No Website: {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"⏱️  Time: {Fore.CYAN}{minutes}m {seconds}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")

        print(f"💡 {Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        print(f"   • Open Excel file")
        print(f"   • Sheet '🔥 NO WEBSITE' = Qualified leads")
        print(f"   • To export ALL data: python master_exporter.py\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Interrupted{Style.RESET_ALL}")
        db.end_session(session_id, len(all_businesses), 'interrupted')
        return 130
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        db.end_session(session_id, 0, 'error', str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())