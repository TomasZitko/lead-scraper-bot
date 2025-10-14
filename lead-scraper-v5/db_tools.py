#!/usr/bin/env python3
"""
Database Management Tools
Reset areas, view stats, export data
"""
import sys
import argparse
from pathlib import Path
from colorama import Fore, Style, init

sys.path.insert(0, str(Path(__file__).parent))

from database_manager import DatabaseManager

init(autoreset=True)


def print_banner():
    """Print banner"""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🔧 DATABASE MANAGEMENT TOOLS                           ║
║   Reset • View Stats • Export                            ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def view_stats(db: DatabaseManager, niche: str = None, city: str = None):
    """View database statistics"""
    stats = db.get_progress_stats(niche, city)
    
    print(f"\n{Fore.YELLOW}📊 DATABASE STATISTICS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Total Businesses: {Fore.GREEN}{stats['total_businesses']}{Style.RESET_ALL}")
    
    if stats['by_city']:
        print(f"\n{Fore.CYAN}By City:{Style.RESET_ALL}")
        for city_stat in stats['by_city'][:10]:
            print(f"  • {city_stat['city']:<20} {city_stat['count']:>5} businesses")
    
    if stats['recent_sessions']:
        print(f"\n{Fore.CYAN}Recent Sessions:{Style.RESET_ALL}")
        for session in stats['recent_sessions'][:5]:
            time_str = session['started_at'][:19]
            status_color = Fore.GREEN if session['status'] == 'completed' else Fore.YELLOW
            print(f"  • {time_str} | {session['niche']:<15} | {session['location']:<15} | {status_color}{session['businesses_found']:>3}{Style.RESET_ALL} found")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def reset_area(db: DatabaseManager, niche: str, city: str, area: str = None):
    """Reset scraping status for an area"""
    if area:
        print(f"\n{Fore.YELLOW}🔄 Resetting:{Style.RESET_ALL} {niche} in {city} - {area}")
    else:
        print(f"\n{Fore.YELLOW}🔄 Resetting ALL areas:{Style.RESET_ALL} {niche} in {city}")
    
    confirm = input(f"{Fore.RED}Are you sure? (yes/no): {Style.RESET_ALL}")
    
    if confirm.lower() == 'yes':
        db.reset_area(niche, city, area)
        print(f"{Fore.GREEN}✅ Reset complete!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Next scrape will re-scrape this area{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}❌ Cancelled{Style.RESET_ALL}\n")


def export_businesses(db: DatabaseManager, niche: str = None, city: str = None, output: str = "export.csv"):
    """Export businesses to CSV"""
    businesses = db.get_businesses(niche, city)
    
    if not businesses:
        print(f"{Fore.YELLOW}⚠️  No businesses found{Style.RESET_ALL}")
        return
    
    import csv
    
    # Define columns
    columns = ['business_name', 'phone', 'email', 'website', 'address', 'city', 'google_rating']
    
    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for business in businesses:
            writer.writerow({col: business.get(col, '') for col in columns})
    
    print(f"{Fore.GREEN}✅ Exported {len(businesses)} businesses to {output}{Style.RESET_ALL}\n")


def main():
    """Main function"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Database Management Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', choices=['stats', 'reset', 'export'], help='Command to run')
    parser.add_argument('--niche', type=str, help='Business niche')
    parser.add_argument('--city', type=str, help='City name')
    parser.add_argument('--area', type=str, help='Specific area (for reset)')
    parser.add_argument('--output', type=str, default='export.csv', help='Output file (for export)')
    
    args = parser.parse_args()
    
    # Initialize database
    db = DatabaseManager()
    
    try:
        if args.command == 'stats':
            view_stats(db, args.niche, args.city)
        
        elif args.command == 'reset':
            if not args.niche or not args.city:
                print(f"{Fore.RED}❌ Error: --niche and --city required for reset{Style.RESET_ALL}")
                return 1
            reset_area(db, args.niche, args.city, args.area)
        
        elif args.command == 'export':
            export_businesses(db, args.niche, args.city, args.output)
    
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
