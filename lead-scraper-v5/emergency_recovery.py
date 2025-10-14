#!/usr/bin/env python3
"""
Emergency Data Recovery Tool
Use this when Excel export crashes but data is in database
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime
import csv
from colorama import Fore, Style, init

sys.path.insert(0, str(Path(__file__).parent))

from database_manager import DatabaseManager

init(autoreset=True)


def print_banner():
    """Print banner"""
    print(f"""
{Fore.RED}╔══════════════════════════════════════════════════════════╗
║   🚨 EMERGENCY DATA RECOVERY                             ║
║   Extract your leads from the database                   ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")


def recover_data(db: DatabaseManager, niche: str = None, city: str = None, output_format: str = "csv"):
    """Recover data from database"""
    
    print(f"\n{Fore.YELLOW}🔍 Searching database...{Style.RESET_ALL}\n")
    
    # Get all businesses
    businesses = db.get_businesses(niche, city)
    
    if not businesses:
        print(f"{Fore.RED}❌ No businesses found in database{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Filters used:{Style.RESET_ALL}")
        print(f"  Niche: {niche or 'ALL'}")
        print(f"  City: {city or 'ALL'}")
        print(f"\n{Fore.YELLOW}Try without filters:{Style.RESET_ALL}")
        print(f"  py -3.13 emergency_recovery.py recover")
        return None
    
    print(f"{Fore.GREEN}✅ Found {len(businesses)} businesses!{Style.RESET_ALL}\n")
    
    # Categorize
    no_website = [b for b in businesses if not b.get('website')]
    has_website = [b for b in businesses if b.get('website')]
    
    print(f"{Fore.CYAN}📊 Breakdown:{Style.RESET_ALL}")
    print(f"  🔥 NO WEBSITE: {len(no_website)} (qualified leads!)")
    print(f"  🌐 HAS WEBSITE: {len(has_website)}")
    print(f"  📊 TOTAL: {len(businesses)}")
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    niche_str = niche or "all"
    city_str = city or "all"
    
    if output_format == "csv":
        # Export to CSV
        output_file = f"RECOVERED_{niche_str}_{city_str}_{timestamp}.csv"
        
        print(f"\n{Fore.YELLOW}💾 Exporting to CSV...{Style.RESET_ALL}")
        
        columns = ['business_name', 'phone', 'email', 'website', 'instagram', 
                   'facebook', 'address', 'city', 'google_rating', 'notes']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for business in businesses:
                writer.writerow({col: business.get(col, '') for col in columns})
        
        print(f"{Fore.GREEN}✅ Saved to: {output_file}{Style.RESET_ALL}\n")
        
        # Also save no-website leads separately
        if no_website:
            no_web_file = f"RECOVERED_NO_WEBSITE_{niche_str}_{city_str}_{timestamp}.csv"
            
            with open(no_web_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=columns)
                writer.writeheader()
                
                for business in no_website:
                    writer.writerow({col: business.get(col, '') for col in columns})
            
            print(f"{Fore.RED}🔥 BONUS: No-website leads saved to: {no_web_file}{Style.RESET_ALL}\n")
        
        return output_file
    
    elif output_format == "txt":
        # Export websites to TXT (one per line)
        websites = [b.get('website') for b in has_website if b.get('website')]
        
        if not websites:
            print(f"{Fore.YELLOW}⚠️  No websites found to export{Style.RESET_ALL}")
            return None
        
        output_file = f"RECOVERED_WEBSITES_{niche_str}_{city_str}_{timestamp}.txt"
        
        print(f"\n{Fore.YELLOW}💾 Exporting websites to TXT...{Style.RESET_ALL}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for website in websites:
                f.write(f"{website}\n")
        
        print(f"{Fore.GREEN}✅ Saved {len(websites)} websites to: {output_file}{Style.RESET_ALL}\n")
        
        return output_file


def check_last_session(db: DatabaseManager):
    """Check what happened in the last scraping session"""
    
    print(f"\n{Fore.YELLOW}🔍 Checking last session...{Style.RESET_ALL}\n")
    
    stats = db.get_progress_stats()
    
    if not stats['recent_sessions']:
        print(f"{Fore.RED}❌ No sessions found in database{Style.RESET_ALL}")
        return
    
    last_session = stats['recent_sessions'][0]
    
    print(f"{Fore.CYAN}Last Scraping Session:{Style.RESET_ALL}")
    print(f"  Time: {last_session['started_at'][:19]}")
    print(f"  Niche: {last_session['niche']}")
    print(f"  Location: {last_session['location']}")
    print(f"  Area: {last_session.get('area', 'N/A')}")
    print(f"  Status: {last_session['status']}")
    print(f"  Businesses Found: {Fore.GREEN}{last_session['businesses_found']}{Style.RESET_ALL}")
    
    # Check if data is in database
    niche = last_session['niche']
    city = last_session['location']
    
    businesses_in_db = db.get_businesses(niche, city)
    
    print(f"\n{Fore.CYAN}Data in Database:{Style.RESET_ALL}")
    print(f"  Total for {niche} in {city}: {Fore.GREEN}{len(businesses_in_db)}{Style.RESET_ALL}")
    
    if len(businesses_in_db) > last_session['businesses_found']:
        print(f"\n{Fore.GREEN}✅ Good news! Database has MORE data than the session reported{Style.RESET_ALL}")
        print(f"   Session reported: {last_session['businesses_found']}")
        print(f"   Database actually has: {len(businesses_in_db)}")
        print(f"\n{Fore.YELLOW}→ Your data is safe! Use 'recover' command to export it{Style.RESET_ALL}")
    elif len(businesses_in_db) == last_session['businesses_found']:
        print(f"\n{Fore.GREEN}✅ Data looks consistent{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Database has LESS than reported{Style.RESET_ALL}")
        print(f"   This might indicate an issue")


def main():
    """Main function"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="Emergency Data Recovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check what happened
  py -3.13 emergency_recovery.py check
  
  # Recover all data
  py -3.13 emergency_recovery.py recover
  
  # Recover specific niche/city
  py -3.13 emergency_recovery.py recover --niche restaurants --city Praha
  
  # Export as TXT (websites only)
  py -3.13 emergency_recovery.py recover --format txt
        """
    )
    
    parser.add_argument('command', choices=['check', 'recover'], help='Command to run')
    parser.add_argument('--niche', type=str, help='Filter by niche')
    parser.add_argument('--city', type=str, help='Filter by city')
    parser.add_argument('--format', type=str, choices=['csv', 'txt'], default='csv', help='Output format')
    
    args = parser.parse_args()
    
    # Initialize database
    db = DatabaseManager()
    
    try:
        if args.command == 'check':
            check_last_session(db)
        
        elif args.command == 'recover':
            output_file = recover_data(db, args.niche, args.city, args.format)
            
            if output_file:
                print(f"\n{Fore.GREEN}{'='*60}")
                print(f"✅ RECOVERY COMPLETE!")
                print(f"{'='*60}{Style.RESET_ALL}")
                print(f"\n{Fore.YELLOW}📁 Your data is saved in:{Style.RESET_ALL}")
                print(f"   {output_file}")
                print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
                print(f"   1. Open the file")
                print(f"   2. Verify your data is there")
                print(f"   3. Use it! 💰")
                print(f"\n{Fore.GREEN}Happy selling! 🚀{Style.RESET_ALL}\n")
    
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())




