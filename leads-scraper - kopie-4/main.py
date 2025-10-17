#!/usr/bin/env python3
"""
Czech Business Lead Scraper - Original CLI
Main controller with all features
"""
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import yaml
from colorama import Fore, Style
from tqdm import tqdm

# Import modules
from utils.logger import setup_logger
from scrapers.registry_scraper import RegistryScraper
from scrapers.google_maps_scraper import GoogleMapsScraper
from scrapers.website_scraper import WebsiteScraper
from processors.data_merger import DataMerger
from processors.deduplicator import Deduplicator
from processors.prioritizer import LeadPrioritizer
from exporters.excel_exporter import ExcelExporter


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.yaml not found{Style.RESET_ALL}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"{Fore.RED}Error parsing config: {e}{Style.RESET_ALL}")
        sys.exit(1)


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║   🇨🇿 Czech Business Lead Scraper            ║
║   Professional Lead Generation Tool          ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def print_summary(businesses: list, output_file: str, elapsed_time: float):
    """Print execution summary"""
    print(f"\n{Fore.GREEN}✨ SCRAPING COMPLETE!{Style.RESET_ALL}")
    print("━" * 50)
    print(f"📊 Total Businesses: {Fore.CYAN}{len(businesses)}{Style.RESET_ALL}")
    print(f"💾 File: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
    print(f"⏱️  Time: {Fore.CYAN}{format_time(elapsed_time)}{Style.RESET_ALL}")
    print("━" * 50)

    # Priority breakdown
    high_priority = sum(1 for b in businesses if b.get('priority_score', 0) >= 75)
    medium_priority = sum(1 for b in businesses if 50 <= b.get('priority_score', 0) < 75)
    low_priority = sum(1 for b in businesses if b.get('priority_score', 0) < 50)

    print(f"\n📈 Priority Breakdown:")
    print(f"  🔴 High (75+):    {high_priority}")
    print(f"  🟡 Medium (50-74): {medium_priority}")
    print(f"  🟢 Low (<50):      {low_priority}")


def format_time(seconds: float) -> str:
    """Format elapsed time"""
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs}s"


def main():
    """Main application entry point"""
    print_banner()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Czech Business Lead Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--niche', type=str, help='Niche or comma-separated niches')
    parser.add_argument('--location', type=str, default='Praha', help='City (default: Praha)')
    parser.add_argument('--all-niches', action='store_true', help='Scrape all niches')
    parser.add_argument('--max-results', type=int, help='Max results per niche')
    parser.add_argument('--output', type=str, help='Custom output filename')
    parser.add_argument('--skip-websites', action='store_true', help='Skip website scraping')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file')

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Setup logger
    logger = setup_logger(verbose=args.verbose)

    # Determine niches
    if args.all_niches:
        niches = list(config['niches'].keys())
    elif args.niche:
        niches = [n.strip() for n in args.niche.split(',')]
    else:
        print(f"{Fore.RED}Error: --niche or --all-niches required{Style.RESET_ALL}")
        parser.print_help()
        sys.exit(1)

    # Validate niches
    for niche in niches:
        if niche not in config['niches']:
            print(f"{Fore.RED}Unknown niche: {niche}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
            sys.exit(1)

    # Config summary
    max_results = args.max_results or config['scraping']['max_results_per_niche']
    print(f"📋 {Fore.CYAN}Configuration:{Style.RESET_ALL}")
    print(f"   Niches: {', '.join(niches)}")
    print(f"   Location: {args.location}")
    print(f"   Max Results: {max_results}")
    print(f"   Skip Websites: {args.skip_websites}")
    print()

    # Start timer
    start_time = time.time()

    try:
        # Initialize scrapers
        registry_scraper = RegistryScraper(
            delay=config['scraping']['delay_between_requests'],
            timeout=config['scraping']['timeout'],
            retry_attempts=config['scraping']['retry_attempts'],
            logger=logger
        )

        google_scraper = GoogleMapsScraper(
            timeout=config['scraping']['timeout'],
            logger=logger
        )

        website_scraper = WebsiteScraper(
            timeout=config['scraping']['timeout'],
            delay=config['scraping']['delay_between_requests'],
            logger=logger
        )

        # Initialize processors
        merger = DataMerger(logger=logger)
        deduplicator = Deduplicator(logger=logger)
        prioritizer = LeadPrioritizer(
            scoring_config=config['scoring'],
            logger=logger
        )
        exporter = ExcelExporter(logger=logger)

        all_businesses = []

        # Process each niche
        for niche in niches:
            print(f"\n{Fore.CYAN}━━━ Processing: {niche.upper()} ━━━{Style.RESET_ALL}\n")

            niche_config = config['niches'][niche]
            keywords = niche_config['keywords_cz'] + niche_config['keywords_en']

            # Step 1: Search Google Maps
            print(f"🔍 {Fore.YELLOW}Step 1: Searching Google Maps...{Style.RESET_ALL}")
            businesses = []
            for keyword in keywords[:2]:
                try:
                    results = google_scraper.search_businesses_on_maps(
                        keyword,
                        args.location,
                        max_results=max_results
                    )
                    businesses.extend(results)
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Error searching {keyword}: {e}")
                    continue
            
            businesses = deduplicator.deduplicate(businesses)[:max_results]
            print(f"   ✓ Found {len(businesses)} businesses")

            if not businesses:
                logger.warning(f"No businesses found for {niche}")
                continue

            # Step 2: Scrape websites
            if not args.skip_websites:
                print(f"\n🌐 {Fore.YELLOW}Step 2: Scraping Websites...{Style.RESET_ALL}")
                websites = [b for b in businesses if b.get('website')]
                if websites:
                    businesses = website_scraper.scrape_websites(businesses)
                    emails = sum(1 for b in businesses if b.get('email'))
                    print(f"   ✓ Found {emails} emails")
                else:
                    print(f"   ⚠ No websites to scrape")
            else:
                print(f"\n🌐 {Fore.YELLOW}Step 2: SKIPPED{Style.RESET_ALL}")

            all_businesses.extend(businesses)

        # Step 3: Deduplicate
        print(f"\n🔧 {Fore.YELLOW}Step 3: Deduplicating...{Style.RESET_ALL}")
        all_businesses = deduplicator.deduplicate(all_businesses)
        all_businesses = deduplicator.remove_invalid_entries(all_businesses)
        print(f"   ✓ {len(all_businesses)} unique businesses")

        # Step 4: Prioritize
        print(f"\n📊 {Fore.YELLOW}Step 4: Scoring...{Style.RESET_ALL}")
        all_businesses = prioritizer.score_leads(all_businesses)
        print(f"   ✓ Scored {len(all_businesses)} leads")

        # Step 5: Export
        print(f"\n💾 {Fore.YELLOW}Step 5: Exporting...{Style.RESET_ALL}")
        niche_name = '_'.join(niches) if len(niches) <= 3 else 'multi_niche'
        output_file = exporter.export(
            all_businesses,
            filename=args.output,
            niche=niche_name,
            location=args.location
        )
        print(f"   ✓ Saved: {output_file}")

        # Cleanup
        registry_scraper.close()
        google_scraper.close()
        website_scraper.close()

        # Print summary
        elapsed_time = time.time() - start_time
        print_summary(all_businesses, output_file, elapsed_time)

        return 0

    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Interrupted{Style.RESET_ALL}")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())