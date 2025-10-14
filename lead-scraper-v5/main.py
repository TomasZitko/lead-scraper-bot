#!/usr/bin/env python3
"""
Czech Business Lead Scraper
Main CLI Controller
"""
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import yaml
from dotenv import load_dotenv
import os
from colorama import Fore, Style
from tqdm import tqdm

# Import our modules
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
        print(f"{Fore.RED}Error: Configuration file '{config_path}' not found{Style.RESET_ALL}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"{Fore.RED}Error parsing configuration file: {e}{Style.RESET_ALL}")
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
    print(f"💾 Exported to: {Fore.CYAN}{output_file}{Style.RESET_ALL}")
    print(f"⏱️  Total Time: {Fore.CYAN}{format_time(elapsed_time)}{Style.RESET_ALL}")
    print("━" * 50)

    # Show priority breakdown
    high_priority = sum(1 for b in businesses if b.get('priority_score', 0) >= 75)
    medium_priority = sum(1 for b in businesses if 50 <= b.get('priority_score', 0) < 75)
    low_priority = sum(1 for b in businesses if b.get('priority_score', 0) < 50)

    print(f"\n📈 Priority Breakdown:")
    print(f"  🔴 High Priority (75+):    {high_priority}")
    print(f"  🟡 Medium Priority (50-74): {medium_priority}")
    print(f"  🟢 Low Priority (<50):      {low_priority}")


def format_time(seconds: float) -> str:
    """Format elapsed time"""
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m {secs}s"


def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Czech Business Lead Scraper - Generate prioritized leads for web design agency",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--niche',
        type=str,
        help='Single niche or comma-separated niches (e.g., "restaurants,cafes")'
    )
    parser.add_argument(
        '--location',
        type=str,
        default='Praha',
        help='City name (default: Praha)'
    )
    parser.add_argument(
        '--all-niches',
        action='store_true',
        help='Scrape all configured niches'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        help='Maximum results per niche (overrides config)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Custom output filename'
    )
    parser.add_argument(
        '--skip-websites',
        action='store_true',
        help='Skip website scraping step'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Load configuration
    config = load_config(args.config)

    # Setup logger
    logger = setup_logger(verbose=args.verbose)

    # Determine which niches to scrape
    if args.all_niches:
        niches = list(config['niches'].keys())
    elif args.niche:
        niches = [n.strip() for n in args.niche.split(',')]
    else:
        print(f"{Fore.RED}Error: Please specify --niche or --all-niches{Style.RESET_ALL}")
        parser.print_help()
        sys.exit(1)

    # Validate niches
    for niche in niches:
        if niche not in config['niches']:
            print(f"{Fore.RED}Error: Unknown niche '{niche}'. Available: {', '.join(config['niches'].keys())}{Style.RESET_ALL}")
            sys.exit(1)

    # Configuration summary
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

        google_api_key = os.getenv('GOOGLE_MAPS_API_KEY', config['google_maps']['api_key'])
        use_google_api = config['scraping']['use_google_api'] and bool(google_api_key)

        google_scraper = GoogleMapsScraper(
            api_key=google_api_key,
            use_api=use_google_api,
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

            # Step 1: Scrape business registry
            print(f"🔍 {Fore.YELLOW}Step 1: Scraping Business Registry...{Style.RESET_ALL}")
            businesses = registry_scraper.search_registry(keywords, args.location, max_results)
            print(f"   ✓ Found {len(businesses)} businesses")

            if not businesses:
                logger.warning(f"No businesses found for {niche}")
                continue

            # Step 2: Enrich with Google Maps
            print(f"\n📞 {Fore.YELLOW}Step 2: Enriching with Google Maps...{Style.RESET_ALL}")
            businesses = google_scraper.enrich_businesses(businesses)
            with_contact = sum(1 for b in businesses if b.get('phone') or b.get('website'))
            print(f"   ✓ Enriched {with_contact}/{len(businesses)} businesses")

            # Step 3: Scrape websites (optional)
            if not args.skip_websites:
                print(f"\n🌐 {Fore.YELLOW}Step 3: Scraping Websites...{Style.RESET_ALL}")
                websites_to_scrape = [b for b in businesses if b.get('website')]
                if websites_to_scrape:
                    businesses = website_scraper.scrape_websites(businesses)
                    with_email = sum(1 for b in businesses if b.get('email'))
                    print(f"   ✓ Found {with_email} emails")
                else:
                    print(f"   ⚠ No websites to scrape")
            else:
                print(f"\n🌐 {Fore.YELLOW}Step 3: Scraping Websites... SKIPPED{Style.RESET_ALL}")

            all_businesses.extend(businesses)

        # Step 4: Deduplicate
        print(f"\n🔧 {Fore.YELLOW}Step 4: Processing & Deduplicating...{Style.RESET_ALL}")
        all_businesses = deduplicator.deduplicate(all_businesses)
        all_businesses = deduplicator.remove_invalid_entries(all_businesses)
        print(f"   ✓ {len(all_businesses)} unique businesses")

        # Step 5: Calculate priority scores
        print(f"\n📊 {Fore.YELLOW}Step 5: Calculating Priority Scores...{Style.RESET_ALL}")
        all_businesses = prioritizer.score_leads(all_businesses)
        print(f"   ✓ Scored {len(all_businesses)} leads")

        # Step 6: Export to Excel
        print(f"\n💾 {Fore.YELLOW}Step 6: Exporting to Excel...{Style.RESET_ALL}")
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
        print(f"\n\n{Fore.YELLOW}⚠ Scraping interrupted by user{Style.RESET_ALL}")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
