#!/usr/bin/env python3
"""
PROFESSIONAL WEB DESIGN LEAD SCRAPER - FINAL VERSION
Complete data extraction • Memory system • Progress tracking • Zero duplicates
"""
import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from colorama import Fore, Style, init
    import yaml
    from tqdm import tqdm
    from database_manager import DatabaseManager
    from config_districts import get_search_areas, estimate_search_count
    from scrapers.google_maps_scraper import EnhancedGoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    init(autoreset=True)
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


def setup_master_logger(verbose: bool = False) -> logging.Logger:
    """Setup consolidated master logger"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Master log file
    master_log = logs_dir / "master.log"
    
    # Create logger
    logger = logging.getLogger("LeadScraperPro")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # File handler (all logs)
    fh = logging.FileHandler(master_log, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Console handler (important logs only)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def print_banner():
    """Print professional banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║   🎯 PROFESSIONAL WEB DESIGN LEAD SCRAPER - FINAL VERSION       ║
║   Complete Extraction • Memory System • Zero Duplicates          ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_dashboard(db: DatabaseManager, niche: str = None, city: str = None):
    """Print scraping dashboard"""
    stats = db.get_progress_stats(niche, city)
    
    print(f"\n{Fore.YELLOW}📊 SCRAPING DASHBOARD{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Total Businesses in Database: {Fore.GREEN}{stats['total_businesses']}{Style.RESET_ALL}")
    
    if stats['by_city']:
        print(f"\n{Fore.CYAN}Top Cities:{Style.RESET_ALL}")
        for city_stat in stats['by_city'][:5]:
            print(f"  • {city_stat['city']}: {city_stat['count']} businesses")
    
    if stats['recent_sessions']:
        print(f"\n{Fore.CYAN}Recent Sessions:{Style.RESET_ALL}")
        for session in stats['recent_sessions'][:3]:
            time_str = session['started_at'][:19]  # YYYY-MM-DD HH:MM:SS
            print(f"  • {time_str} | {session['niche']} in {session['location']} | {session['businesses_found']} found")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.yaml not found{Style.RESET_ALL}")
        sys.exit(1)


def main():
    """Main professional scraping function"""
    print_banner()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Professional Lead Scraper - Complete data extraction with memory",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--niche', type=str, required=True, help='Business niche')
    parser.add_argument('--location', type=str, default='Praha', help='City name')
    parser.add_argument('--max-results', type=int, default=100, help='Target number of leads')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--force-rescrape', action='store_true', help='Rescrape already scraped areas')
    parser.add_argument('--dashboard', action='store_true', help='Show dashboard and exit')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    # Setup
    logger = setup_master_logger(verbose=args.verbose)
    logger.info(f"🚀 Starting Professional Lead Scraper")
    logger.info(f"Target: {args.max_results} {args.niche} in {args.location}")
    
    config = load_config()
    db = DatabaseManager()

    # Show dashboard if requested
    if args.dashboard:
        print_dashboard(db, args.niche, args.location)
        return 0

    # Validate niche
    if args.niche not in config['niches']:
        print(f"{Fore.RED}❌ Unknown niche: {args.niche}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
        return 1

    niche_config = config['niches'][args.niche]
    keywords = niche_config['keywords_cz']
    
    # Get search areas
    search_areas = get_search_areas(args.location)
    results_per_area = max(10, args.max_results // len(search_areas))
    
    # Show current stats
    print_dashboard(db, args.niche, args.location)
    
    # Display configuration
    print(f"🎯 {Fore.CYAN}Target:{Style.RESET_ALL} {args.max_results} {args.niche.replace('_', ' ').title()} in {args.location}")
    print(f"📋 {Fore.CYAN}Keywords:{Style.RESET_ALL} {', '.join(keywords[:3])}")
    print(f"🗺️  {Fore.CYAN}Strategy:{Style.RESET_ALL} {len(search_areas)} areas × ~{results_per_area} results/area")
    print(f"🧠 {Fore.CYAN}Memory:{Style.RESET_ALL} Database-backed deduplication")
    print(f"📁 {Fore.CYAN}Logs:{Style.RESET_ALL} logs/master.log\n")

    start_time = time.time()

    try:
        # Initialize components
        print(f"{Fore.YELLOW}⚙️  Initializing enhanced scraper...{Style.RESET_ALL}")
        
        google_scraper = EnhancedGoogleMapsScraper(
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

        # STEP 1: Enhanced Google Maps Search
        print(f"\n{Fore.CYAN}━━━ STEP 1: Enhanced Google Maps Search (Complete Data) ━━━{Style.RESET_ALL}")
        print(f"   Extracting websites, phones, ratings from {len(search_areas)} areas\n")
        
        all_businesses = []
        new_businesses = 0
        existing_businesses = 0
        successful_searches = 0
        
        with tqdm(total=len(search_areas), desc="   Areas", unit="area") as pbar:
            for area in search_areas:
                
                for keyword in keywords[:2]:  # Use first 2 keywords
                    
                    # Check if already scraped (unless force rescrape)
                    if not args.force_rescrape and db.is_area_scraped(args.niche, args.location, area, keyword):
                        logger.info(f"⊘ Skipping {area} ({keyword}) - already scraped recently")
                        continue
                    
                    try:
                        pbar.set_description(f"   {area} ({keyword})")
                        
                        # Scrape
                        businesses = google_scraper.search_businesses_on_maps(
                            keyword,
                            area,
                            max_results=results_per_area
                        )
                        
                        # Add to database (auto-deduplicates)
                        for business in businesses:
                            business['niche'] = args.niche
                            business['city'] = args.location
                            
                            # Check if new
                            exists = db.business_exists(
                                business.get('business_name', ''),
                                business.get('address'),
                                business.get('google_place_id')
                            )
                            
                            if exists:
                                existing_businesses += 1
                            else:
                                new_businesses += 1
                            
                            # Add/update in database
                            db.add_business(business)
                            all_businesses.append(business)
                        
                        # Mark area as scraped
                        db.mark_area_scraped(args.niche, args.location, area, keyword, len(businesses))
                        
                        if businesses:
                            successful_searches += 1
                        
                        # Check if enough
                        if len(all_businesses) >= args.max_results:
                            break
                        
                        time.sleep(3)  # Be nice to Google
                        
                    except Exception as e:
                        logger.warning(f"Error searching {area} for {keyword}: {e}")
                        continue
                
                pbar.update(1)
                
                if len(all_businesses) >= args.max_results:
                    break
                
                time.sleep(2)

        # Get unique businesses
        unique_businesses = []
        seen_ids = set()
        for b in all_businesses:
            bid = (b.get('business_name', '').lower(), b.get('address', ''))
            if bid not in seen_ids:
                seen_ids.add(bid)
                unique_businesses.append(b)
        
        unique_businesses = unique_businesses[:args.max_results]
        
        print(f"\n   ✓ Found {Fore.GREEN}{len(unique_businesses)}{Style.RESET_ALL} unique businesses")
        print(f"   📊 {Fore.CYAN}{new_businesses}{Style.RESET_ALL} new | {Fore.YELLOW}{existing_businesses}{Style.RESET_ALL} existing in database")
        print(f"   ✅ Success rate: {successful_searches} searches")

        if not unique_businesses:
            print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
            db.end_session(session_id, 0, 'no_results')
            return 1

        # STEP 2: Additional website scraping (if needed)
        if not args.skip_websites:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Additional Website Scraping ━━━{Style.RESET_ALL}")
            websites_to_scrape = [b for b in unique_businesses if b.get('website') and not b.get('email')]
            if websites_to_scrape:
                print(f"   Scraping {len(websites_to_scrape)} websites for additional info\n")
                unique_businesses = website_scraper.scrape_websites(unique_businesses)
            else:
                print(f"   ✓ All websites already processed")
        else:
            print(f"\n{Fore.CYAN}━━━ STEP 2: Website Scraping ━━━{Style.RESET_ALL}")
            print(f"   {Fore.YELLOW}⊘ SKIPPED{Style.RESET_ALL}")

        # STEP 3: Prioritize
        print(f"\n{Fore.CYAN}━━━ STEP 3: Calculating Priority Scores ━━━{Style.RESET_ALL}")
        unique_businesses = prioritizer.score_leads(unique_businesses)
        
        # Stats
        no_website = sum(1 for b in unique_businesses if not b.get('website'))
        has_website = sum(1 for b in unique_businesses if b.get('website'))
        high_priority = sum(1 for b in unique_businesses if b.get('priority_score', 0) >= 75)
        
        print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} WITHOUT website (Qualified!)")
        print(f"   🌐 {Fore.BLUE}{has_website}{Style.RESET_ALL} WITH website")
        print(f"   ⭐ {Fore.YELLOW}{high_priority}{Style.RESET_ALL} high-priority (75+ score)")

        # STEP 4: Export
        print(f"\n{Fore.CYAN}━━━ STEP 4: Exporting to Excel ━━━{Style.RESET_ALL}")
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

        # Final summary
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✨ SCRAPING COMPLETE! ✨")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"📊 Total Leads: {Fore.CYAN}{len(unique_businesses)}{Style.RESET_ALL}")
        print(f"🔥 No Website (QUALIFIED): {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"🌐 Has Website: {Fore.BLUE}{has_website}{Style.RESET_ALL}")
        print(f"⭐ High Priority: {Fore.YELLOW}{high_priority}{Style.RESET_ALL}")
        print(f"📁 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
        print(f"📝 Logs: {Fore.CYAN}logs/master.log{Style.RESET_ALL}")
        print(f"⏱️  Time: {Fore.CYAN}{minutes}m {seconds}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")

        print(f"🎯 {Fore.YELLOW}Database Status:{Style.RESET_ALL}")
        print(f"   • {new_businesses} new businesses added")
        print(f"   • {existing_businesses} existing businesses updated")
        print(f"   • Zero duplicates guaranteed!\n")

        print(f"✅ Open {Fore.CYAN}{output_file}{Style.RESET_ALL} and start selling! 💰\n")

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  Scraping interrupted{Style.RESET_ALL}")
        db.end_session(session_id, len(all_businesses), 'interrupted')
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        db.end_session(session_id, 0, 'error', str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())

