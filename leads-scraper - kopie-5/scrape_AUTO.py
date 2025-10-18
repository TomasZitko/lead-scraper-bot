#!/usr/bin/env python3
"""
AUTOMATIC ROTATION SCRAPER
One command = scrapes multiple niches automatically
Full website & registry extraction
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
    from database_manager import DatabaseManager
    from scrapers.google_maps_scraper import GoogleMapsScraper
    from scrapers.website_scraper import WebsiteScraper
    from scrapers.registry_enhancer import RegistryEnhancer
    from processors.deduplicator import Deduplicator
    from processors.prioritizer import LeadPrioritizer
    from exporters.excel_exporter import ExcelExporter
    from utils.logger import setup_logger
    init(autoreset=True)
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)


MAIN_DISTRICTS = [
    "Praha 1", "Brno-střed", "Ostrava-Poruba", "Plzeň 1", "Liberec",
    "Olomouc", "České Budějovice", "Hradec Králové", "Ústí nad Labem",
    "Pardubice", "Zlín", "Karlovy Vary", "Havířov", "Kladno", "Most",
    "Opava", "Frýdek-Místek", "Jihlava", "Teplice", "Děčín"
]


def scrape_district_full(niche, district, google_scraper, website_scraper, registry_enhancer, db, config, logger, results):
    """Scrape district with FULL info extraction"""
    
    niche_config = config['niches'][niche]
    keyword = niche_config['keywords_cz'][0]
    
    # Check if done
    if db.is_area_scraped(niche, district, district, keyword):
        return []
    
    try:
        # Google Maps
        businesses = google_scraper.search_businesses_on_maps(keyword, district, max_results=results)
        
        if not businesses:
            return []
        
        # Tag
        for b in businesses:
            b['niche'] = niche
            b['city'] = district
        
        # IMMEDIATE website scraping (while data fresh)
        print(f"\n      🌐 Scraping {len(businesses)} websites...")
        businesses = website_scraper.scrape_websites(businesses)
        
        # Registry for missing info
        missing = [b for b in businesses if not b.get('website') or not b.get('email')]
        if missing:
            print(f"      🇨🇿 Registry lookup for {len(missing)} businesses...")
            for b in tqdm(missing, desc="      Registry", leave=False):
                try:
                    registry_enhancer.enhance_business(b)
                except:
                    pass
        
        # Save to DB
        for b in businesses:
            db.add_business(b)
        
        # Mark done
        db.mark_area_scraped(niche, district, district, keyword, len(businesses))
        
        return businesses
        
    except Exception as e:
        logger.error(f"Error in {district}: {e}")
        return []


def scrape_niche_auto(niche, cities, google_scraper, website_scraper, registry_enhancer, db, config, logger, results_per_city):
    """Scrape one niche across cities with full extraction"""
    
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"🎯 NICHE: {niche.upper()}")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    all_businesses = []
    
    with tqdm(total=len(cities), desc=f"   {niche}", unit="city") as pbar:
        for district in cities:
            pbar.set_description(f"   {district}")
            
            businesses = scrape_district_full(
                niche, district, google_scraper, website_scraper, 
                registry_enhancer, db, config, logger, results_per_city
            )
            
            all_businesses.extend(businesses)
            pbar.set_postfix({"Total": len(all_businesses)})
            pbar.update(1)
            
            time.sleep(3)
    
    # Deduplicate
    deduplicator = Deduplicator(logger=logger)
    before = len(all_businesses)
    all_businesses = deduplicator.deduplicate(all_businesses)
    all_businesses = deduplicator.remove_invalid_entries(all_businesses)
    after = len(all_businesses)
    
    print(f"\n   ✓ {Fore.GREEN}{after}{Style.RESET_ALL} unique businesses (removed {before-after} duplicates)")
    
    # Stats
    no_website = sum(1 for b in all_businesses if not b.get('website'))
    with_email = sum(1 for b in all_businesses if b.get('email'))
    with_phone = sum(1 for b in all_businesses if b.get('phone'))
    with_instagram = sum(1 for b in all_businesses if b.get('instagram'))
    
    print(f"   🔥 {Fore.RED}{no_website}{Style.RESET_ALL} without website")
    print(f"   ✉️  {Fore.GREEN}{with_email}{Style.RESET_ALL} with email")
    print(f"   📞 {Fore.GREEN}{with_phone}{Style.RESET_ALL} with phone")
    print(f"   📱 {Fore.MAGENTA}{with_instagram}{Style.RESET_ALL} with Instagram")
    
    return all_businesses


def main():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🤖 AUTOMATIC ROTATION SCRAPER                          ║
║   One Command = Multiple Niches + Full Extraction       ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")
    
    parser = argparse.ArgumentParser(description="Automatic multi-niche scraper")
    parser.add_argument('--niches', type=str, default='restaurants,cafes,bars,hair_salons,fitness_gyms,personal_trainers', 
                        help='Comma-separated niches (default: 6 top niches)')
    parser.add_argument('--cities', type=int, default=20, help='Cities per niche (default: 20)')
    parser.add_argument('--results-per-city', type=int, default=50, help='Target per city (default: 50)')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    # Setup
    logger = setup_logger(verbose=args.verbose)
    with open("config.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    niches = [n.strip() for n in args.niches.split(',')]
    cities = MAIN_DISTRICTS[:args.cities]
    
    # Validate niches
    for niche in niches:
        if niche not in config['niches']:
            print(f"{Fore.RED}Unknown niche: {niche}{Style.RESET_ALL}")
            return 1
    
    print(f"🎯 {Fore.CYAN}Niches:{Style.RESET_ALL} {len(niches)} ({', '.join(niches)})")
    print(f"🏙️  {Fore.CYAN}Cities:{Style.RESET_ALL} {len(cities)} per niche")
    print(f"📊 {Fore.CYAN}Target:{Style.RESET_ALL} {args.results_per_city} per city")
    print(f"🔥 {Fore.CYAN}Features:{Style.RESET_ALL} Full website + registry extraction")
    print(f"⏱️  {Fore.CYAN}Est. Time:{Style.RESET_ALL} {len(niches) * len(cities) * 4} minutes")
    print(f"📈 {Fore.CYAN}Est. Leads:{Style.RESET_ALL} {len(niches) * len(cities) * args.results_per_city} leads\n")
    
    input(f"{Fore.YELLOW}Press ENTER to start automatic scraping...{Style.RESET_ALL}")
    
    start_time = time.time()
    
    # Initialize (reuse same instances)
    db = DatabaseManager()
    google_scraper = GoogleMapsScraper(timeout=30, logger=logger)
    website_scraper = WebsiteScraper(timeout=30, delay=2, logger=logger)
    registry_enhancer = RegistryEnhancer(logger=logger)
    prioritizer = LeadPrioritizer(scoring_config=config['scoring'], logger=logger)
    exporter = ExcelExporter(logger=logger)
    
    all_niches_businesses = []
    
    # AUTO-ROTATE THROUGH NICHES
    for i, niche in enumerate(niches, 1):
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"NICHE {i}/{len(niches)}")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        businesses = scrape_niche_auto(
            niche, cities, google_scraper, website_scraper,
            registry_enhancer, db, config, logger, args.results_per_city
        )
        
        all_niches_businesses.extend(businesses)
        
        print(f"\n   📊 {Fore.CYAN}Session Total:{Style.RESET_ALL} {len(all_niches_businesses)} leads")
        
        # Wait between niches (let Google cool down)
        if i < len(niches):
            print(f"\n   {Fore.YELLOW}⏳ Waiting 60s before next niche...{Style.RESET_ALL}")
            time.sleep(60)
    
    # Final processing
    if all_niches_businesses:
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"FINAL PROCESSING")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        # Final dedup across all niches
        deduplicator = Deduplicator(logger=logger)
        before = len(all_niches_businesses)
        all_niches_businesses = deduplicator.deduplicate(all_niches_businesses)
        after = len(all_niches_businesses)
        
        print(f"\n🔧 Final Deduplication:")
        print(f"   {before} → {Fore.GREEN}{after}{Style.RESET_ALL} (removed {before-after})")
        
        # Prioritize
        print(f"\n📊 Priority Scoring...")
        all_niches_businesses = prioritizer.score_leads(all_niches_businesses)
        
        # Final stats
        no_website = sum(1 for b in all_niches_businesses if not b.get('website'))
        with_email = sum(1 for b in all_niches_businesses if b.get('email'))
        with_phone = sum(1 for b in all_niches_businesses if b.get('phone'))
        with_instagram = sum(1 for b in all_niches_businesses if b.get('instagram'))
        with_facebook = sum(1 for b in all_niches_businesses if b.get('facebook'))
        
        print(f"\n{Fore.CYAN}📈 FINAL STATS:{Style.RESET_ALL}")
        print(f"   📊 Total Leads: {Fore.GREEN}{after}{Style.RESET_ALL}")
        print(f"   🔥 No Website: {Fore.RED}{no_website}{Style.RESET_ALL} (qualified!)")
        print(f"   ✉️  With Email: {Fore.GREEN}{with_email}{Style.RESET_ALL}")
        print(f"   📞 With Phone: {Fore.GREEN}{with_phone}{Style.RESET_ALL}")
        print(f"   📱 With Instagram: {Fore.MAGENTA}{with_instagram}{Style.RESET_ALL}")
        print(f"   👥 With Facebook: {Fore.CYAN}{with_facebook}{Style.RESET_ALL}")
        
        # Export
        print(f"\n💾 Exporting to Excel...")
        output = exporter.export(
            all_niches_businesses,
            niche="MULTI_NICHE",
            location=f"{len(cities)}_cities"
        )
        
        # Summary
        elapsed = int(time.time() - start_time)
        hours = elapsed // 3600
        mins = (elapsed % 3600) // 60
        
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"✨ AUTOMATIC SCRAPING COMPLETE!")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"🎯 Niches: {len(niches)}")
        print(f"🏙️  Cities: {len(cities)} per niche")
        print(f"📊 Total Leads: {Fore.CYAN}{after}{Style.RESET_ALL}")
        print(f"🔥 Qualified (no website): {Fore.GREEN}{no_website}{Style.RESET_ALL}")
        print(f"📁 Excel: {Fore.CYAN}{output}{Style.RESET_ALL}")
        print(f"⏱️  Time: {hours}h {mins}m")
        print(f"⚡ Rate: {after/(elapsed/60):.1f} leads/min")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    
    # Cleanup
    google_scraper.close()
    db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())