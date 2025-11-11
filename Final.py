"""
City Distance Calculator Tool
============================
This tool calculates straight-line distances between cities using the Haversine formula.
Features:
- Interactive console interface for city input
- SQLite database storage for city coordinates
- Automatic coordinate lookup or user input for unknown cities
- Accurate distance calculation considering Earth's spherical shape
- Persistent storage of city data for future use
"""

import sqlite3
import math
import os
from typing import Tuple, Optional, Dict
from pathlib import Path


class CityDistanceCalculator:
    """
    City distance calculator using Haversine formula for spherical Earth calculations.
    Stores city coordinates in SQLite database for persistent storage.
    """

    def __init__(self, database_path: str = "cities.db"):
        """
        Initialize the city distance calculator.

        Args:
            database_path: Path to SQLite database file for storing city coordinates
        """
        # Set database path
        self.database_path = database_path

        # Earth's radius in kilometers (mean radius)
        self.EARTH_RADIUS_KM = 6371.0

        # Initialize database
        self.initialize_database()

        # Pre-populate with some major cities for convenience
        self.populate_initial_cities()

    def initialize_database(self) -> None:
        """
        Initialize SQLite database and create cities table if it doesn't exist.
        """
        try:
            # Connect to database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Create cities table with unique constraint on city name
                cursor.execute('''
                               CREATE TABLE IF NOT EXISTS cities
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   name
                                   TEXT
                                   UNIQUE
                                   NOT
                                   NULL,
                                   latitude
                                   REAL
                                   NOT
                                   NULL,
                                   longitude
                                   REAL
                                   NOT
                                   NULL,
                                   country
                                   TEXT,
                                   created_at
                                   DATETIME
                                   DEFAULT
                                   CURRENT_TIMESTAMP
                               )
                               ''')

                # Create index for faster city name lookups
                cursor.execute('''
                               CREATE INDEX IF NOT EXISTS idx_city_name
                                   ON cities(name)
                               ''')

                # Commit changes
                conn.commit()

            print(f"Database initialized successfully: {self.database_path}")

        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

    def populate_initial_cities(self) -> None:
        """
        Pre-populate database with coordinates of major world cities for convenience.
        """
        # Major world cities with their coordinates (latitude, longitude)
        initial_cities = [
            ("New York", 40.7128, -74.0060, "USA"),
            ("London", 51.5074, -0.1278, "UK"),
            ("Paris", 48.8566, 2.3522, "France"),
            ("Tokyo", 35.6762, 139.6503, "Japan"),
            ("Sydney", -33.8688, 151.2093, "Australia"),
            ("Los Angeles", 34.0522, -118.2437, "USA"),
            ("Berlin", 52.5200, 13.4050, "Germany"),
            ("Moscow", 55.7558, 37.6176, "Russia"),
            ("Mumbai", 19.0760, 72.8777, "India"),
            ("Beijing", 39.9042, 116.4074, "China"),
            ("Cairo", 30.0444, 31.2357, "Egypt"),
            ("São Paulo", -23.5505, -46.6333, "Brazil"),
            ("Mexico City", 19.4326, -99.1332, "Mexico"),
            ("Buenos Aires", -34.6118, -58.3960, "Argentina"),
            ("Lagos", 6.5244, 3.3792, "Nigeria"),
            ("Bangkok", 13.7563, 100.5018, "Thailand"),
            ("Istanbul", 41.0082, 28.9784, "Turkey"),
            ("Seoul", 37.5665, 126.9780, "South Korea"),
            ("Dubai", 25.2048, 55.2708, "UAE"),
            ("Singapore", 1.3521, 103.8198, "Singapore")
        ]

        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Check if any cities already exist
                cursor.execute("SELECT COUNT(*) FROM cities")
                city_count = cursor.fetchone()[0]

                # Only populate if database is empty
                if city_count == 0:
                    print("Populating database with initial city coordinates...")

                    # Insert initial cities
                    for name, lat, lon, country in initial_cities:
                        try:
                            cursor.execute('''
                                           INSERT INTO cities (name, latitude, longitude, country)
                                           VALUES (?, ?, ?, ?)
                                           ''', (name, lat, lon, country))
                        except sqlite3.IntegrityError:
                            # City already exists, skip
                            pass

                    # Commit changes
                    conn.commit()
                    print(f"Successfully added {len(initial_cities)} initial cities to database.")

        except Exception as e:
            print(f"Error populating initial cities: {e}")

    def get_city_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Get city coordinates from database.

        Args:
            city_name: Name of the city to look up

        Returns:
            Tuple of (latitude, longitude) if found, None otherwise
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Search for city (case-insensitive)
                cursor.execute('''
                               SELECT latitude, longitude
                               FROM cities
                               WHERE LOWER(name) = LOWER(?)
                               ''', (city_name,))

                result = cursor.fetchone()

                if result:
                    return (result[0], result[1])
                else:
                    return None

        except Exception as e:
            print(f"Error retrieving city coordinates: {e}")
            return None

    def save_city_coordinates(self, city_name: str, latitude: float, longitude: float, country: str = "") -> bool:
        """
        Save city coordinates to database.

        Args:
            city_name: Name of the city
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            country: Optional country name

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Validate coordinates
            if not (-90 <= latitude <= 90):
                print(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
                return False

            if not (-180 <= longitude <= 180):
                print(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
                return False

            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Insert or update city coordinates
                cursor.execute('''
                    INSERT OR REPLACE INTO cities (name, latitude, longitude, country)
                    VALUES (?, ?, ?, ?)
                ''', (city_name, latitude, longitude, country))

                # Commit changes
                conn.commit()

            print(f"✓ Coordinates saved for {city_name}: ({latitude}, {longitude})")
            return True

        except Exception as e:
            print(f"✗ Error saving city coordinates: {e}")
            return False

    def get_city_coordinates_from_user(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Get city coordinates from user input with validation.

        Args:
            city_name: Name of the city

        Returns:
            Tuple of (latitude, longitude) if valid input provided, None otherwise
        """
        print(f"\nCity '{city_name}' not found in database.")
        print("Please provide coordinates for this city.")
        print("You can find coordinates using Google Maps, GPS coordinates websites, etc.")
        print("Format: Latitude ranges from -90 to 90, Longitude ranges from -180 to 180")

        try:
            # Get latitude
            while True:
                lat_input = input(f"Enter latitude for {city_name} (-90 to 90): ").strip()
                if not lat_input:
                    print("Latitude cannot be empty. Please try again.")
                    continue

                try:
                    latitude = float(lat_input)
                    if -90 <= latitude <= 90:
                        break
                    else:
                        print("Latitude must be between -90 and 90. Please try again.")
                except ValueError:
                    print("Invalid latitude format. Please enter a valid number.")

            # Get longitude
            while True:
                lon_input = input(f"Enter longitude for {city_name} (-180 to 180): ").strip()
                if not lon_input:
                    print("Longitude cannot be empty. Please try again.")
                    continue

                try:
                    longitude = float(lon_input)
                    if -180 <= longitude <= 180:
                        break
                    else:
                        print("Longitude must be between -180 and 180. Please try again.")
                except ValueError:
                    print("Invalid longitude format. Please enter a valid number.")

            # Get optional country
            country = input(f"Enter country for {city_name} (optional): ").strip()

            # Save to database
            if self.save_city_coordinates(city_name, latitude, longitude, country):
                return (latitude, longitude)
            else:
                return None

        except KeyboardInterrupt:
            print("\nInput cancelled by user.")
            return None
        except Exception as e:
            print(f"Error getting coordinates from user: {e}")
            return None

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the straight-line distance between two points on Earth using the Haversine formula.

        The Haversine formula accounts for the spherical shape of Earth and calculates
        the great-circle distance between two points given their latitude and longitude.

        Args:
            lat1: Latitude of first point in decimal degrees
            lon1: Longitude of first point in decimal degrees
            lat2: Latitude of second point in decimal degrees
            lon2: Longitude of second point in decimal degrees

        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude from degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Calculate differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        # a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
        # c = 2 ⋅ atan2( √a, √(1−a) )
        # d = R ⋅ c

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(dlon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Distance in kilometers
        distance = self.EARTH_RADIUS_KM * c

        return distance

    def calculate_distance_between_cities(self, city1: str, city2: str) -> Optional[float]:
        """
        Calculate distance between two cities.

        Args:
            city1: Name of first city
            city2: Name of second city

        Returns:
            Distance in kilometers if successful, None if failed
        """
        # Get coordinates for first city
        coords1 = self.get_city_coordinates(city1)
        if coords1 is None:
            coords1 = self.get_city_coordinates_from_user(city1)
            if coords1 is None:
                print(f"Failed to get coordinates for {city1}")
                return None

        # Get coordinates for second city
        coords2 = self.get_city_coordinates(city2)
        if coords2 is None:
            coords2 = self.get_city_coordinates_from_user(city2)
            if coords2 is None:
                print(f"Failed to get coordinates for {city2}")
                return None

        # Calculate distance using Haversine formula
        distance = self.haversine_distance(coords1[0], coords1[1], coords2[0], coords2[1])

        return distance

    def list_stored_cities(self) -> None:
        """
        Display all cities stored in the database.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                               SELECT name, latitude, longitude, country
                               FROM cities
                               ORDER BY name
                               ''')

                cities = cursor.fetchall()

                if cities:
                    print(f"\n{'=' * 60}")
                    print("STORED CITIES IN DATABASE")
                    print(f"{'=' * 60}")
                    print(f"{'City':<20} {'Latitude':<12} {'Longitude':<12} {'Country':<15}")
                    print("-" * 60)

                    for name, lat, lon, country in cities:
                        country_display = country if country else "N/A"
                        print(f"{name:<20} {lat:<12.4f} {lon:<12.4f} {country_display:<15}")

                    print(f"\nTotal cities stored: {len(cities)}")
                else:
                    print("No cities stored in database.")

        except Exception as e:
            print(f"Error listing stored cities: {e}")

    def get_database_info(self) -> Dict:
        """
        Get information about the database.

        Returns:
            Dictionary with database information
        """
        try:
            info = {
                'database_path': self.database_path,
                'database_exists': os.path.exists(self.database_path),
                'total_cities': 0,
                'countries_count': 0
            }

            if info['database_exists']:
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()

                    # Get total cities count
                    cursor.execute("SELECT COUNT(*) FROM cities")
                    info['total_cities'] = cursor.fetchone()[0]

                    # Get unique countries count
                    cursor.execute("SELECT COUNT(DISTINCT country) FROM cities WHERE country != ''")
                    info['countries_count'] = cursor.fetchone()[0]

            return info

        except Exception as e:
            print(f"Error getting database info: {e}")
            return {'error': str(e)}

    def run_interactive_mode(self) -> None:
        """
        Run the interactive console interface for city distance calculation.
        """
        print("=" * 70)
        print("CITY DISTANCE CALCULATOR")
        print("=" * 70)
        print("Calculate straight-line distances between cities using coordinates.")
        print("The tool uses the Haversine formula to account for Earth's spherical shape.")
        print("City coordinates are stored in SQLite database for future use.")

        while True:
            print(f"\n{'=' * 50}")
            print("MAIN MENU")
            print(f"{'=' * 50}")
            print("1. Calculate distance between two cities")
            print("2. View stored cities")
            print("3. View database information")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                self.handle_distance_calculation()
            elif choice == '2':
                self.list_stored_cities()
            elif choice == '3':
                self.show_database_info()
            elif choice == '4':
                print("Thank you for using the City Distance Calculator!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

    def handle_distance_calculation(self) -> None:
        """
        Handle the distance calculation workflow.
        """
        print(f"\n{'-' * 50}")
        print("DISTANCE CALCULATION")
        print(f"{'-' * 50}")

        try:
            # Get first city
            city1 = input("Enter the name of the first city: ").strip()
            if not city1:
                print("City name cannot be empty.")
                return

            # Get second city
            city2 = input("Enter the name of the second city: ").strip()
            if not city2:
                print("City name cannot be empty.")
                return

            # Check if cities are the same
            if city1.lower() == city2.lower():
                print("Both cities are the same. Distance is 0 km.")
                return

            print(f"\nCalculating distance between {city1} and {city2}...")

            # Calculate distance
            distance = self.calculate_distance_between_cities(city1, city2)

            if distance is not None:
                print(f"\n{'=' * 50}")
                print("CALCULATION RESULT")
                print(f"{'=' * 50}")
                print(f"Distance between {city1} and {city2}:")
                print(f"  {distance:.2f} kilometers")
                print(f"  {distance * 0.621371:.2f} miles")
                print(f"  {distance * 0.539957:.2f} nautical miles")

                # Additional information
                if distance < 100:
                    print(f"\nNote: These cities are relatively close ({distance:.1f} km apart)")
                elif distance > 10000:
                    print(f"\nNote: These cities are on opposite sides of the world ({distance:.1f} km apart)")

            else:
                print("✗ Failed to calculate distance between cities.")

        except KeyboardInterrupt:
            print("\nDistance calculation cancelled by user.")
        except Exception as e:
            print(f"Error during distance calculation: {e}")

    def show_database_info(self) -> None:
        """
        Display comprehensive database information.
        """
        print(f"\n{'-' * 50}")
        print("DATABASE INFORMATION")
        print(f"{'-' * 50}")

        info = self.get_database_info()

        if 'error' in info:
            print(f"Error: {info['error']}")
            return

        print(f"Database File: {info['database_path']}")
        print(f"Database Exists: {info['database_exists']}")
        print(f"Total Cities Stored: {info['total_cities']}")
        print(f"Countries Represented: {info['countries_count']}")

        if info['database_exists']:
            file_size = os.path.getsize(info['database_path'])
            print(f"Database Size: {file_size:,} bytes ({file_size / 1024:.2f} KB)")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function to run the city distance calculator.
    """
    try:
        # Create calculator instance2

        calculator = CityDistanceCalculator()

        # Run interactive mode
        calculator.run_interactive_mode()

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run the main application
    main()