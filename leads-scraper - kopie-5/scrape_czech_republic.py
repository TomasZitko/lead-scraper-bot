#!/usr/bin/env python3
"""
CZECH REPUBLIC MASTER SCRAPER
Automated execution of complete Czech coverage
With safety delays and progress tracking
"""
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
import json

sys.path.insert(0, str(Path(__file__).parent))

try:
    from colorama import Fore, Style, init
    from database_manager import DatabaseManager
    init(autoreset=True)
except ImportError:
    print("Error: Missing dependencies")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


# Czech cities organized by priority
MAJOR_CITIES = [
    "Praha",
    "Brno", 
    "Ostrava",
    "Plzeň"
]

LARGE_CITIES = [
    "Liberec",
    "Olomouc",
    "České Budějovice",
    "Hradec Králové",
    "Ústí nad Labem",
    "Pardubice",
    "Zlín",
    "Karlovy Vary"
]

MEDIUM_CITIES = [
    "Havířov",
    "Kladno",
    "Most",
    "Opava",
    "Frýdek-Místek",
    "Jihlava",
    "Teplice",
    "Děčín",
    "Karviná",
    "Chomutov",
    "Jablonec nad Nisou",
    "Mladá Boleslav",
    "Prostějov",
    "Přerov"
]


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║   🇨🇿 CZECH REPUBLIC MASTER SCRAPER                              ║
║   Complete Coverage Strategy                                     ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def load_progress():
    """Load scraping progress from file"""
    progress_file = Path("data/czech_progress.json")
    if progress_file.exists():
        with open(progress_file) as f:
            return json.load(f)
    return {"completed_cities": [], "total_businesses": 0, "started_at": None}


def save_progress(progress):
    """Save scraping progress"""
    progress_file = Path("data/czech_progress.json")
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)


def scrape_city(city, skip_websites=False, skip_registry=False, results_per_area=50):
    """
    Scrape one complete city
    
    Returns:
        Number of businesses found
    """
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"🏙️  SCRAPING: {city.upper()}")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    # Build command
    cmd = [
        sys.executable,
        "scrape_city_SMART.py",
        "--city", city,
        "--complete",
        "--results-per-area", str(results_per_area)
    ]
    
    if skip_websites:
        cmd.append("--skip-websites")
    
    if skip_registry:
        cmd.append("--skip-registry")
    
    # Execute
    try:
        result = subprocess.run(cmd, check=True)
        
        # Get count from database
        db = DatabaseManager()
        businesses = db.get_businesses(city=city)
        count = len(businesses)
        db.close()
        
        print(f"\n{Fore.GREEN}✅ {city} COMPLETE: {count} businesses{Style.RESET_ALL}\n")
        return count
        
    except subprocess.CalledProcessError as e:
        print(f"\n{Fore.RED}❌ Error scraping {city}: {e}{Style.RESET_ALL}\n")
        return 0
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Interrupted during {city}{Style.RESET_ALL}")
        raise


def show_progress(progress, db):
    """Display current progress"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"📊 PROGRESS REPORT")
    print(f"{'='*70}{Style.RESET_ALL}")
    
    stats = db.get_progress_stats()
    total = stats['total_businesses']
    
    completed = len(progress['completed_cities'])
    remaining_major = len([c for c in MAJOR_CITIES if c not in progress['completed_cities']])
    remaining_large = len([c for c in LARGE_CITIES if c not in progress['completed_cities']])
    remaining_medium = len([c for c in MEDIUM_CITIES if c not in progress['completed_cities']])
    
    print(f"\n{Fore.YELLOW}Total Businesses Scraped:{Style.RESET_ALL} {Fore.GREEN}{total:,}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Cities Completed:{Style.RESET_ALL} {Fore.GREEN}{completed}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Remaining:{Style.RESET_ALL}")
    print(f"  Major Cities: {remaining_major}")
    print(f"  Large Cities: {remaining_large}")
    print(f"  Medium Cities: {remaining_medium}")
    
    if progress['started_at']:
        started = datetime.fromisoformat(progress['started_at'])
        elapsed = datetime.now() - started
        days = elapsed.days
        print(f"\n{Fore.CYAN}Days Running:{Style.RESET_ALL} {days}")
        
        if completed > 0:
            rate = total / max(days, 1)
            print(f"{Fore.CYAN}Average Rate:{Style.RESET_ALL} {rate:.0f} businesses/day")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    if total >= 160000:
        print(f"{Fore.GREEN}🎉 YOU'VE ACHIEVED 70% COVERAGE! 🎉{Style.RESET_ALL}\n")


def scrape_phase(cities, phase_name, progress, skip_websites=False, skip_registry=False):
    """Scrape a phase (group of cities)"""
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"📍 PHASE: {phase_name.upper()}")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"Cities in this phase: {len(cities)}")
    print(f"Estimated time: {len(cities) * 2}-{len(cities) * 4} hours\n")
    
    for i, city in enumerate(cities, 1):
        # Skip if already completed
        if city in progress['completed_cities']:
            print(f"{Fore.YELLOW}⊘ Skipping {city} (already completed){Style.RESET_ALL}\n")
            continue
        
        print(f"\n{Fore.CYAN}[{i}/{len(cities)}] Starting: {city}{Style.RESET_ALL}")
        
        # Scrape city
        count = scrape_city(city, skip_websites, skip_registry)
        
        # Update progress
        if count > 0:
            progress['completed_cities'].append(city)
            progress['total_businesses'] += count
            save_progress(progress)
        
        # Delay between cities (safety)
        if i < len(cities):
            delay = 300  # 5 minutes between cities
            print(f"\n{Fore.YELLOW}⏳ Waiting {delay}s before next city...{Style.RESET_ALL}")
            time.sleep(delay)
    
    print(f"\n{Fore.GREEN}✅ {phase_name} PHASE COMPLETE!{Style.RESET_ALL}\n")


def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Czech Republic Master Scraper - Complete coverage automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start from beginning
  python scrape_czech_republic.py --start
  
  # Resume from where you left off
  python scrape_czech_republic.py --resume
  
  # Just major cities
  python scrape_czech_republic.py --phase major
  
  # Quick mode (skip website/registry)
  python scrape_czech_republic.py --start --quick
  
  # View progress
  python scrape_czech_republic.py --status
  
  # Reset progress (start fresh)
  python scrape_czech_republic.py --reset
        """
    )
    
    parser.add_argument('--start', action='store_true', help='Start from beginning')
    parser.add_argument('--resume', action='store_true', help='Resume from last position')
    parser.add_argument('--phase', choices=['major', 'large', 'medium', 'all'], help='Scrape specific phase')
    parser.add_argument('--status', action='store_true', help='Show progress status')
    parser.add_argument('--reset', action='store_true', help='Reset progress')
    parser.add_argument('--quick', action='store_true', help='Quick mode (skip websites/registry)')
    parser.add_argument('--city', type=str, help='Scrape single city')
    
    args = parser.parse_args()
    
    # Load progress
    progress = load_progress()
    
    # Initialize database
    db = DatabaseManager()
    
    # Show status
    if args.status:
        show_progress(progress, db)
        db.close()
        return 0
    
    # Reset progress
    if args.reset:
        confirm = input(f"{Fore.RED}Reset ALL progress? This will NOT delete data. (yes/no): {Style.RESET_ALL}")
        if confirm.lower() == 'yes':
            progress = {"completed_cities": [], "total_businesses": 0, "started_at": None}
            save_progress(progress)
            print(f"{Fore.GREEN}✅ Progress reset!{Style.RESET_ALL}")
        db.close()
        return 0
    
    # Single city mode
    if args.city:
        count = scrape_city(args.city, args.quick, args.quick)
        db.close()
        return 0
    
    # Start or resume
    if args.start or args.resume:
        # Initialize start time
        if not progress['started_at']:
            progress['started_at'] = datetime.now().isoformat()
            save_progress(progress)
        
        print(f"\n{Fore.CYAN}🇨🇿 CZECH REPUBLIC COVERAGE STRATEGY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        print(f"Target: 70% of Czech businesses (~170,000)")
        print(f"Mode: {'QUICK (no websites/registry)' if args.quick else 'COMPLETE (full data)'}")
        print(f"\nThis will take 3-6 months of regular scraping.")
        print(f"You can stop anytime and resume later!\n")
        
        if args.start:
            confirm = input(f"{Fore.YELLOW}Start Czech Republic scraping? (yes/no): {Style.RESET_ALL}")
            if confirm.lower() != 'yes':
                print("Cancelled")
                db.close()
                return 0
        
        try:
            # Phase 1: Major cities
            if args.phase in ['major', 'all', None]:
                scrape_phase(MAJOR_CITIES, "MAJOR CITIES", progress, args.quick, args.quick)
                show_progress(progress, db)
            
            # Phase 2: Large cities
            if args.phase in ['large', 'all', None]:
                scrape_phase(LARGE_CITIES, "LARGE CITIES", progress, args.quick, args.quick)
                show_progress(progress, db)
            
            # Phase 3: Medium cities
            if args.phase in ['medium', 'all', None]:
                scrape_phase(MEDIUM_CITIES, "MEDIUM CITIES", progress, args.quick, args.quick)
                show_progress(progress, db)
            
            # Final report
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"🎉 CZECH REPUBLIC SCRAPING COMPLETE!")
            print(f"{'='*70}{Style.RESET_ALL}\n")
            
            show_progress(progress, db)
            
            print(f"{Fore.CYAN}Next steps:{Style.RESET_ALL}")
            print(f"  1. Export master file: python master_exporter.py")
            print(f"  2. Backup database: cp data/scraping_history.db backups/")
            print(f"  3. Start selling! 💰\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}⚠️  Interrupted!{Style.RESET_ALL}")
            print(f"Progress saved. Resume anytime with:")
            print(f"  python scrape_czech_republic.py --resume\n")
        
        db.close()
        return 0
    
    # No action specified
    parser.print_help()
    db.close()
    return 1


if __name__ == "__main__":
    sys.exit(main())