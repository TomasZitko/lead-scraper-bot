"""
Database Manager for Lead Scraper
Tracks scraped businesses, prevents duplicates, monitors progress
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging


class DatabaseManager:
    """Manages SQLite database for scraping history and deduplication"""
    
    # CRITICAL: Minimum results threshold to consider area "complete"
    MIN_RESULTS_FOR_COMPLETION = 50
    
    def __init__(self, db_path: str = "data/scraping_history.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        self._create_tables()
        
    def _create_tables(self):
        """Create database tables"""
        
        # Businesses table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                address TEXT,
                city TEXT,
                postal_code TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                instagram TEXT,
                facebook TEXT,
                google_rating REAL,
                google_place_id TEXT UNIQUE,
                niche TEXT,
                source TEXT,
                first_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scrape_count INTEGER DEFAULT 1,
                notes TEXT
            )
        """)
        
        # Index for fast lookups
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_normalized_name 
            ON businesses(normalized_name)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_place_id 
            ON businesses(google_place_id)
        """)
        
        # Scraping sessions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                location TEXT NOT NULL,
                area TEXT,
                keyword TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                businesses_found INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                notes TEXT
            )
        """)
        
        # Progress tracking - UPDATED with quality threshold
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS area_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                city TEXT NOT NULL,
                area TEXT NOT NULL,
                keyword TEXT NOT NULL,
                last_scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                businesses_found INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                quality_score INTEGER DEFAULT 0,
                UNIQUE(niche, city, area, keyword)
            )
        """)
        
        self.conn.commit()
    
    def normalize_name(self, name: str) -> str:
        """Normalize business name for comparison"""
        if not name:
            return ""
        
        # Remove common words, punctuation, lowercase
        name = name.lower()
        name = name.replace('restaurace', '').replace('restaurant', '')
        name = name.replace('kavárna', '').replace('café', '').replace('cafe', '')
        name = name.replace('&', '').replace('-', ' ')
        name = ' '.join(name.split())  # Remove extra spaces
        
        return name.strip()
    
    def business_exists(self, business_name: str, address: str = None, google_place_id: str = None) -> Optional[int]:
        """
        Check if business already exists in database
        
        Returns:
            business_id if exists, None otherwise
        """
        # Check by Google Place ID first (most reliable)
        if google_place_id:
            self.cursor.execute(
                "SELECT id FROM businesses WHERE google_place_id = ?",
                (google_place_id,)
            )
            result = self.cursor.fetchone()
            if result:
                return result['id']
        
        # Check by normalized name
        normalized = self.normalize_name(business_name)
        if not normalized:
            return None
        
        if address:
            # With address
            self.cursor.execute("""
                SELECT id FROM businesses 
                WHERE normalized_name = ? 
                AND (address LIKE ? OR address IS NULL)
                LIMIT 1
            """, (normalized, f"%{address[:20]}%"))
        else:
            # Name only
            self.cursor.execute("""
                SELECT id FROM businesses 
                WHERE normalized_name = ?
                LIMIT 1
            """, (normalized,))
        
        result = self.cursor.fetchone()
        return result['id'] if result else None
    
    def add_business(self, business: Dict) -> int:
        """
        Add or update business in database
        
        Returns:
            business_id
        """
        normalized = self.normalize_name(business.get('business_name', ''))
        
        # Check if exists
        existing_id = self.business_exists(
            business.get('business_name', ''),
            business.get('address'),
            business.get('google_place_id')
        )
        
        if existing_id:
            # Update existing
            self.cursor.execute("""
                UPDATE businesses SET
                    address = COALESCE(?, address),
                    city = COALESCE(?, city),
                    postal_code = COALESCE(?, postal_code),
                    phone = COALESCE(?, phone),
                    email = COALESCE(?, email),
                    website = COALESCE(?, website),
                    instagram = COALESCE(?, instagram),
                    facebook = COALESCE(?, facebook),
                    google_rating = COALESCE(?, google_rating),
                    last_updated_at = CURRENT_TIMESTAMP,
                    scrape_count = scrape_count + 1,
                    notes = COALESCE(?, notes)
                WHERE id = ?
            """, (
                business.get('address'),
                business.get('city'),
                business.get('postal_code'),
                business.get('phone'),
                business.get('email'),
                business.get('website'),
                business.get('instagram'),
                business.get('facebook'),
                business.get('google_rating'),
                business.get('notes'),
                existing_id
            ))
            
            self.conn.commit()
            return existing_id
        
        else:
            # Insert new
            self.cursor.execute("""
                INSERT INTO businesses (
                    business_name, normalized_name, address, city, postal_code,
                    phone, email, website, instagram, facebook, google_rating,
                    google_place_id, niche, source, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                business.get('business_name'),
                normalized,
                business.get('address'),
                business.get('city'),
                business.get('postal_code'),
                business.get('phone'),
                business.get('email'),
                business.get('website'),
                business.get('instagram'),
                business.get('facebook'),
                business.get('google_rating'),
                business.get('google_place_id'),
                business.get('niche'),
                business.get('source'),
                business.get('notes')
            ))
            
            self.conn.commit()
            return self.cursor.lastrowid
    
    def start_session(self, niche: str, location: str, area: str = None, keyword: str = None) -> int:
        """Start a new scraping session"""
        self.cursor.execute("""
            INSERT INTO scraping_sessions (niche, location, area, keyword, status)
            VALUES (?, ?, ?, ?, 'running')
        """, (niche, location, area, keyword))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def end_session(self, session_id: int, businesses_found: int, status: str = 'completed', notes: str = None):
        """End a scraping session"""
        self.cursor.execute("""
            UPDATE scraping_sessions SET
                completed_at = CURRENT_TIMESTAMP,
                businesses_found = ?,
                status = ?,
                notes = ?
            WHERE id = ?
        """, (businesses_found, status, notes, session_id))
        
        self.conn.commit()
    
    def mark_area_scraped(self, niche: str, city: str, area: str, keyword: str, businesses_found: int):
        """
        Mark an area as scraped
        
        CRITICAL FIX: Only mark as "completed" if we got substantial results
        """
        # Calculate quality score
        quality_score = self._calculate_scrape_quality(businesses_found)
        
        # Only mark as complete if we found enough businesses
        is_complete = businesses_found >= self.MIN_RESULTS_FOR_COMPLETION
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO area_progress 
            (niche, city, area, keyword, businesses_found, completed, quality_score, last_scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (niche, city, area, keyword, businesses_found, 1 if is_complete else 0, quality_score))
        
        self.conn.commit()
    
    def _calculate_scrape_quality(self, businesses_found: int) -> int:
        """
        Calculate quality score for a scrape (0-100)
        
        Args:
            businesses_found: Number of businesses found
            
        Returns:
            Quality score (0-100)
        """
        if businesses_found >= 100:
            return 100
        elif businesses_found >= 50:
            return 80
        elif businesses_found >= 20:
            return 50
        elif businesses_found >= 10:
            return 30
        else:
            return 10
    
    def is_area_scraped(self, niche: str, city: str, area: str, keyword: str) -> bool:
        """
        Check if area has been scraped recently AND successfully
        
        CRITICAL FIX: Don't skip if previous scrape was poor quality
        """
        self.cursor.execute("""
            SELECT completed, businesses_found, quality_score, last_scraped_at 
            FROM area_progress
            WHERE niche = ? AND city = ? AND area = ? AND keyword = ?
        """, (niche, city, area, keyword))
        
        result = self.cursor.fetchone()
        if not result:
            return False
        
        # Only skip if:
        # 1. Marked as completed AND
        # 2. Found substantial results (50+) AND
        # 3. Scraped in last 7 days
        if not result['completed']:
            return False
        
        if result['businesses_found'] < self.MIN_RESULTS_FOR_COMPLETION:
            # Previous scrape was poor quality - rescrape!
            return False
        
        # Check if scraped recently
        from datetime import timedelta
        last_scraped = datetime.fromisoformat(result['last_scraped_at'])
        if (datetime.now() - last_scraped) >= timedelta(days=7):
            return False
        
        return True
    
    def get_progress_stats(self, niche: str = None, city: str = None) -> Dict:
        """Get scraping progress statistics"""
        query = "SELECT COUNT(*) as total FROM businesses WHERE 1=1"
        params = []
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        if city:
            query += " AND city = ?"
            params.append(city)
        
        self.cursor.execute(query, params)
        total = self.cursor.fetchone()['total']
        
        # By city
        query = "SELECT city, COUNT(*) as count FROM businesses WHERE 1=1"
        if niche:
            query += " AND niche = ?"
        query += " GROUP BY city ORDER BY count DESC LIMIT 10"
        
        self.cursor.execute(query, [niche] if niche else [])
        by_city = [dict(row) for row in self.cursor.fetchall()]
        
        # Recent sessions
        self.cursor.execute("""
            SELECT niche, location, area, businesses_found, started_at, status
            FROM scraping_sessions
            ORDER BY started_at DESC
            LIMIT 10
        """)
        recent_sessions = [dict(row) for row in self.cursor.fetchall()]
        
        return {
            'total_businesses': total,
            'by_city': by_city,
            'recent_sessions': recent_sessions
        }
    
    def get_businesses(self, niche: str = None, city: str = None, has_website: bool = None, limit: int = None) -> List[Dict]:
        """Get businesses from database"""
        query = "SELECT * FROM businesses WHERE 1=1"
        params = []
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        if city:
            query += " AND city = ?"
            params.append(city)
        
        if has_website is not None:
            if has_website:
                query += " AND website IS NOT NULL AND website != ''"
            else:
                query += " AND (website IS NULL OR website = '')"
        
        query += " ORDER BY last_updated_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def reset_area(self, niche: str, city: str, area: str = None):
        """
        Reset scraping status for an area (force rescrape)
        
        Args:
            niche: Business niche
            city: City name
            area: Specific area (optional - if None, reset entire city)
        """
        if area:
            self.cursor.execute("""
                DELETE FROM area_progress
                WHERE niche = ? AND city = ? AND area = ?
            """, (niche, city, area))
        else:
            self.cursor.execute("""
                DELETE FROM area_progress
                WHERE niche = ? AND city = ?
            """, (niche, city))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == "__main__":
    # Test the database
    db = DatabaseManager()
    
    # Test business
    test_business = {
        'business_name': 'Test Restaurant Praha',
        'address': 'Praha 1',
        'city': 'Praha',
        'niche': 'restaurants',
        'source': 'google_maps',
        'website': 'https://test.cz'
    }
    
    bid = db.add_business(test_business)
    print(f"✅ Added business with ID: {bid}")
    
    # Check if exists
    exists = db.business_exists('Test Restaurant Praha')
    print(f"✅ Business exists: {exists}")
    
    # Get stats
    stats = db.get_progress_stats()
    print(f"✅ Total businesses: {stats['total_businesses']}")
    
    db.close()
    print("✅ Database test complete!")