"""
Czech Republic Districts and Areas Configuration
For comprehensive business scraping across all regions
"""

# Prague Districts (Praha 1-22)
PRAHA_DISTRICTS = [
    "Praha 1",  # Staré Město, Nové Město, Malá Strana
    "Praha 2",  # Vinohrady, Nusle
    "Praha 3",  # Žižkov, Vinohrady
    "Praha 4",  # Nusle, Michle, Podolí
    "Praha 5",  # Smíchov, Barrandov
    "Praha 6",  # Dejvice, Bubeneč, Střešovice
    "Praha 7",  # Holešovice, Letná
    "Praha 8",  # Karlín, Libeň, Kobylisy
    "Praha 9",  # Prosek, Vysočany, Černý Most
    "Praha 10", # Vršovice, Strašnice
    "Praha 11", # Chodov, Háje
    "Praha 12", # Modřany
    "Praha 13", # Stodůlky
    "Praha 14", # Černý Most, Hloubětín
    "Praha 15", # Horní Měcholupy
]

# Brno Districts
BRNO_DISTRICTS = [
    "Brno-střed",
    "Brno-jih", 
    "Brno-sever",
    "Brno-Kohoutovice",
    "Brno-Židenice",
    "Brno-Komín",
    "Brno-Starý Lískovec",
    "Brno-Vinohrady",
    "Brno-Černá Pole",
    "Brno-Líšeň",
]

# Ostrava Districts
OSTRAVA_DISTRICTS = [
    "Ostrava-Poruba",
    "Ostrava-Moravská Ostrava",
    "Ostrava-Vítkovice",
    "Ostrava-Zábřeh",
    "Ostrava-Mariánské Hory",
    "Ostrava-Slezská Ostrava",
]

# Plzeň Districts
PLZEN_DISTRICTS = [
    "Plzeň 1",
    "Plzeň 2", 
    "Plzeň 3",
    "Plzeň 4",
]

# Smaller cities - no districts needed, just city name
SMALLER_CITIES = [
    "Liberec",
    "Olomouc",
    "České Budějovice",
    "Hradec Králové",
    "Ústí nad Labem",
    "Pardubice",
    "Zlín",
    "Karlovy Vary",
    "Teplice",
    "Jihlava",
]

# Main configuration
CITY_DISTRICTS = {
    "Praha": PRAHA_DISTRICTS,
    "Brno": BRNO_DISTRICTS,
    "Ostrava": OSTRAVA_DISTRICTS,
    "Plzeň": PLZEN_DISTRICTS,
}

def get_search_areas(city: str) -> list:
    """
    Get list of areas to search for a city
    
    Args:
        city: City name
        
    Returns:
        List of search areas (districts or just city name)
    """
    # Check if city has districts
    if city in CITY_DISTRICTS:
        return CITY_DISTRICTS[city]
    
    # For smaller cities, just return the city name
    return [city]


def get_all_czech_cities() -> list:
    """
    Get all Czech cities we can scrape
    
    Returns:
        List of all city names
    """
    cities = list(CITY_DISTRICTS.keys()) + SMALLER_CITIES
    return sorted(cities)


def estimate_search_count(city: str, max_results: int) -> dict:
    """
    Estimate how many searches needed for a city
    
    Args:
        city: City name
        max_results: Desired total results
        
    Returns:
        Dict with estimation details
    """
    areas = get_search_areas(city)
    num_areas = len(areas)
    
    # Estimate ~100 results per area (Google Maps limit)
    results_per_area = min(100, max_results // num_areas) if num_areas > 0 else max_results
    
    # Calculate how many areas needed
    areas_needed = min(num_areas, (max_results // 100) + 1)
    
    return {
        'city': city,
        'total_areas': num_areas,
        'areas_to_search': areas_needed,
        'results_per_area': results_per_area,
        'estimated_results': areas_needed * results_per_area,
        'estimated_time_minutes': areas_needed * 3,  # ~3 min per area
    }


# Example usage
if __name__ == "__main__":
    print("Czech Republic Scraping Areas:")
    print("=" * 60)
    
    for city in get_all_czech_cities():
        areas = get_search_areas(city)
        print(f"\n{city}: {len(areas)} areas")
        if len(areas) <= 5:
            print(f"  → {', '.join(areas)}")
        else:
            print(f"  → {', '.join(areas[:3])}, ... (+{len(areas)-3} more)")
    
    print("\n" + "=" * 60)
    print("\nExample: 1000 restaurants in Praha")
    est = estimate_search_count("Praha", 1000)
    print(f"  Areas to search: {est['areas_to_search']}/{est['total_areas']}")
    print(f"  Estimated results: {est['estimated_results']}")
    print(f"  Estimated time: {est['estimated_time_minutes']} minutes")








