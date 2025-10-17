#!/usr/bin/env python3
"""
Database Administrator - Complete database management tool
Reset areas, view stats, export data, manage history
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import argparse
from colorama import Fore, Style, init
from database_manager import DatabaseManager
from master_exporter import MasterExporter

init(autoreset=True)


def print_banner():
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║   🔧 DATABASE ADMINISTRATOR                              ║
║   Manage your scraping database                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def view_stats(db: DatabaseManager):
    """View detailed database statistics"""
    stats = db.get_progress_stats()
    
    print(f"\n{Fore.YELLOW}📊 DATABASE STATISTICS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"Total Businesses: {Fore.GREEN}{stats['total_businesses']}{Style.RESET_ALL}")
    
    if stats['by_city']:
        print(f"\n{Fore.CYAN}📍 By City:{Style.RESET_ALL}")
        for city_stat in stats['by_city']:
            print(f"  • {city_stat['city']:<20} {city_stat['count']:>5} businesses")
    
    if stats['recent_sessions']:
        print(f"\n{Fore.CYAN}🕒 Recent Scraping Sessions:{Style.RESET_ALL}")
        for session in stats['recent_sessions']:
            time_str = session['started_at'][:19]
            status_color = Fore.GREEN if session['status'] == 'completed' else Fore.YELLOW
            print(f"  • {time_str} | {session['niche']:<15} | {session['location']:<15} | {status_color}{session['businesses_found']:>3}{Style.RESET_ALL} found")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def reset_city(db: DatabaseManager, city: str):
    """Reset all scraping history for a city"""
    print(f"\n{Fore.YELLOW}🔄 RESETTING CITY: {city}{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  WARNING: This will mark all areas in {city} as not scraped{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  Businesses in database will NOT be deleted{Style.RESET_ALL}")
    print(f"{Fore.CYAN}This allows you to re-scrape areas that may have been incomplete{Style.RESET_ALL}")
    
    confirm = input(f"\n{Fore.YELLOW}Type the city name again to confirm: {Style.RESET_ALL}")
    
    if confirm.lower() == city.lower():
        # Reset all niches in this city
        db.cursor.execute("""
            DELETE FROM area_progress
            WHERE city = ?
        """, (city,))
        db.conn.commit()
        
        deleted = db.cursor.rowcount
        print(f"\n{Fore.GREEN}✅ Reset complete!{Style.RESET_ALL}")
        print(f"   Cleared {deleted} area records")
        print(f"   Next scrape will start fresh in {city}\n")
    else:
        print(f"{Fore.RED}❌ Cancelled{Style.RESET_ALL}\n")


def reset_niche(db: DatabaseManager, niche: str, city: str = None):
    """Reset scraping history for a specific niche"""
    if city:
        target = f"{niche} in {city}"
        print(f"\n{Fore.YELLOW}🔄 RESETTING: {target}{Style.RESET_ALL}")
    else:
        target = f"{niche} (ALL CITIES)"
        print(f"\n{Fore.YELLOW}🔄 RESETTING: {target}{Style.RESET_ALL}")
    
    print(f"{Fore.RED}⚠️  WARNING: This will mark areas as not scraped{Style.RESET_ALL}")
    print(f"{Fore.RED}⚠️  Businesses in database will NOT be deleted{Style.RESET_ALL}")
    
    confirm = input(f"\n{Fore.YELLOW}Confirm reset? (yes/no): {Style.RESET_ALL}")
    
    if confirm.lower() == 'yes':
        if city:
            db.cursor.execute("""
                DELETE FROM area_progress
                WHERE niche = ? AND city = ?
            """, (niche, city))
        else:
            db.cursor.execute("""
                DELETE FROM area_progress
                WHERE niche = ?
            """, (niche,))
        
        db.conn.commit()
        deleted = db.cursor.rowcount
        
        print(f"\n{Fore.GREEN}✅ Reset complete!{Style.RESET_ALL}")
        print(f"   Cleared {deleted} area records")
        print(f"   Next scrape will start fresh\n")
    else:
        print(f"{Fore.RED}❌ Cancelled{Style.RESET_ALL}\n")


def reset_all(db: DatabaseManager):
    """Reset EVERYTHING - complete fresh start"""
    print(f"\n{Fore.RED}{'='*70}")
    print(f"⚠️  DANGER: COMPLETE DATABASE RESET")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This will:{Style.RESET_ALL}")
    print(f"  • Delete ALL scraping history")
    print(f"  • Delete ALL businesses")
    print(f"  • Delete ALL sessions")
    print(f"  • Start completely fresh")
    print(f"\n{Fore.RED}THIS CANNOT BE UNDONE!{Style.RESET_ALL}")
    
    confirm1 = input(f"\n{Fore.YELLOW}Type 'DELETE EVERYTHING' to confirm: {Style.RESET_ALL}")
    
    if confirm1 == 'DELETE EVERYTHING':
        confirm2 = input(f"{Fore.RED}Are you ABSOLUTELY sure? (yes/no): {Style.RESET_ALL}")
        
        if confirm2.lower() == 'yes':
            # Delete all data
            db.cursor.execute("DELETE FROM businesses")
            db.cursor.execute("DELETE FROM scraping_sessions")
            db.cursor.execute("DELETE FROM area_progress")
            db.conn.commit()
            
            print(f"\n{Fore.GREEN}✅ Database completely reset{Style.RESET_ALL}")
            print(f"   You can now start fresh!\n")
        else:
            print(f"{Fore.YELLOW}❌ Cancelled{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.YELLOW}❌ Cancelled{Style.RESET_ALL}\n")


def list_cities(db: DatabaseManager):
    """List all cities in database"""
    db.cursor.execute("""
        SELECT city, COUNT(*) as count
        FROM businesses
        WHERE city IS NOT NULL AND city != ''
        GROUP BY city
        ORDER BY count DESC
    """)
    
    cities = db.cursor.fetchall()
    
    print(f"\n{Fore.CYAN}🏙️  CITIES IN DATABASE:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    if cities:
        for i, row in enumerate(cities, 1):
            print(f"  {i:2d}. {row['city']:<30} {row['count']:>5} businesses")
    else:
        print(f"  {Fore.YELLOW}No cities found{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def list_niches(db: DatabaseManager):
    """List all niches in database"""
    db.cursor.execute("""
        SELECT niche, COUNT(*) as count
        FROM businesses
        WHERE niche IS NOT NULL AND niche != ''
        GROUP BY niche
        ORDER BY count DESC
    """)
    
    niches = db.cursor.fetchall()
    
    print(f"\n{Fore.CYAN}🎯 NICHES IN DATABASE:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    if niches:
        for i, row in enumerate(niches, 1):
            print(f"  {i:2d}. {row['niche']:<30} {row['count']:>5} businesses")
    else:
        print(f"  {Fore.YELLOW}No niches found{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")


def export_master(db: DatabaseManager, niche: str = None, city: str = None):
    """Export master database to Excel"""
    exporter = MasterExporter(db)
    exporter.export_master_file(niche=niche, city=city)


def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Database Administrator - Manage your scraping database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View database statistics
  python db_admin.py stats
  
  # List all cities
  python db_admin.py cities
  
  # List all niches
  python db_admin.py niches
  
  # Export master Excel file
  python db_admin.py export
  
  # Export specific city
  python db_admin.py export --city Praha
  
  # Export specific niche
  python db_admin.py export --niche restaurants
  
  # Reset specific city (allows re-scraping)
  python db_admin.py reset-city --city Praha
  
  # Reset specific niche in city
  python db_admin.py reset-niche --niche restaurants --city Praha
  
  # Reset EVERYTHING (dangerous!)
  python db_admin.py reset-all
        """
    )
    
    parser.add_argument(
        'command',
        choices=['stats', 'cities', 'niches', 'export', 'reset-city', 'reset-niche', 'reset-all'],
        help='Command to execute'
    )
    parser.add_argument('--city', type=str, help='City name')
    parser.add_argument('--niche', type=str, help='Niche name')
    
    args = parser.parse_args()
    
    # Initialize database
    db = DatabaseManager()
    
    try:
        if args.command == 'stats':
            view_stats(db)
        
        elif args.command == 'cities':
            list_cities(db)
        
        elif args.command == 'niches':
            list_niches(db)
        
        elif args.command == 'export':
            export_master(db, niche=args.niche, city=args.city)
        
        elif args.command == 'reset-city':
            if not args.city:
                print(f"{Fore.RED}❌ Error: --city required{Style.RESET_ALL}")
                return 1
            reset_city(db, args.city)
        
        elif args.command == 'reset-niche':
            if not args.niche:
                print(f"{Fore.RED}❌ Error: --niche required{Style.RESET_ALL}")
                return 1
            reset_niche(db, args.niche, args.city)
        
        elif args.command == 'reset-all':
            reset_all(db)
        
        return 0
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())