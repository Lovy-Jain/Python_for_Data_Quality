"""
Homework 10: Enhanced News Feed System with Database Storage
===========================================================
This module extends Homework 5, 6, 7, 8, and 9 with database storage capabilities.
Includes functionality to:
- Save records to SQLite database with different tables for different record types
- Implement duplicate checking to prevent duplicate records
- Create separate tables for News, Private Ads, and Weather Alerts
- Maintain all previous functionality (manual input, JSON/XML processing)
"""

import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import sqlite3
import hashlib
import os
import re
import random
import string
import csv
from collections import Counter
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path


# =============================================================================
# BASE CLASSES FROM PREVIOUS HOMEWORKS (EXTENDED WITH DATABASE SUPPORT)
# =============================================================================

class FeedRecord(ABC):
    """
    Abstract base class for all feed record types.
    Defines the interface that all record types must implement.
    """

    def __init__(self, text: str):
        """
        Initialize base record with text content.

        Args:
            text: The main content text for the record
        """
        self.text = text.strip()
        self.timestamp = datetime.now()

    @abstractmethod
    def get_user_input(self) -> None:
        """
        Get additional input from user specific to this record type.
        Must be implemented by each concrete record class.
        """
        pass

    @abstractmethod
    def format_for_publication(self) -> str:
        """
        Format the record for publication in the news feed file.
        Must return formatted string ready for writing to file.
        """
        pass

    @abstractmethod
    def get_record_type_name(self) -> str:
        """
        Return the display name for this record type.
        """
        pass

    @classmethod
    @abstractmethod
    def from_json_data(cls, data: Dict) -> 'FeedRecord':
        """
        Create record instance from JSON data.
        Must be implemented by each concrete record class.

        Args:
            data: Dictionary containing record data from JSON

        Returns:
            Instance of the record class
        """
        pass

    @classmethod
    @abstractmethod
    def from_xml_element(cls, element: ET.Element) -> 'FeedRecord':
        """
        Create record instance from XML element.
        Must be implemented by each concrete record class.

        Args:
            element: XML Element containing record data

        Returns:
            Instance of the record class
        """
        pass

    @abstractmethod
    def get_database_data(self) -> Dict:
        """
        Get record data formatted for database storage.
        Must be implemented by each concrete record class.

        Returns:
            Dictionary containing record data for database insertion
        """
        pass

    @abstractmethod
    def get_duplicate_check_fields(self) -> List[str]:
        """
        Get list of field names to use for duplicate checking.
        Must be implemented by each concrete record class.

        Returns:
            List of field names for duplicate checking
        """
        pass

    def generate_content_hash(self) -> str:
        """
        Generate hash for duplicate checking based on content.

        Returns:
            SHA-256 hash of record content
        """
        # Get duplicate check fields and their values
        check_fields = self.get_duplicate_check_fields()
        db_data = self.get_database_data()

        # Create string from relevant fields for hashing
        hash_content = ""
        for field in check_fields:
            if field in db_data:
                hash_content += str(db_data[field])

        # Generate SHA-256 hash
        content_hash = hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
        return content_hash


class NewsRecord(FeedRecord):
    """
    News record type with text, city, and auto-calculated date.
    """

    def __init__(self, text: str, city: str = ""):
        """
        Initialize news record with text content and optional city.

        Args:
            text: The news text content
            city: The city where news happened (optional)
        """
        super().__init__(text)
        self.city = city

    def get_user_input(self) -> None:
        """
        Get city input from user for news record.
        """
        if not self.city:
            self.city = input("Enter city where news happened: ").strip()
            while not self.city:
                print("City cannot be empty!")
                self.city = input("Enter city where news happened: ").strip()

    def format_for_publication(self) -> str:
        """
        Format news record for publication with special news format.

        Returns:
            Formatted string ready for publication
        """
        # Format timestamp for display
        formatted_date = self.timestamp.strftime("%Y-%m-%d %H:%M")

        # Create formatted news entry
        formatted_text = f"News -------------------------\n"
        formatted_text += f"{self.text}\n"
        formatted_text += f"{self.city}, {formatted_date}\n\n"

        return formatted_text

    def get_record_type_name(self) -> str:
        """
        Return the display name for news records.
        """
        return "News"

    def get_database_data(self) -> Dict:
        """
        Get news record data formatted for database storage.

        Returns:
            Dictionary containing news record data for database insertion
        """
        return {
            'text': self.text,
            'city': self.city,
            'timestamp': self.timestamp.isoformat(),
            'content_hash': self.generate_content_hash()
        }

    def get_duplicate_check_fields(self) -> List[str]:
        """
        Get list of field names to use for duplicate checking in news records.

        Returns:
            List of field names for duplicate checking
        """
        return ['text', 'city']

    @classmethod
    def from_json_data(cls, data: Dict) -> 'NewsRecord':
        """
        Create NewsRecord instance from JSON data.

        Args:
            data: Dictionary containing record data from JSON

        Returns:
            NewsRecord instance
        """
        # Extract required fields from JSON data
        text = data.get('text', '')
        city = data.get('city', '')

        # Validate required fields
        if not text:
            raise ValueError("News record requires 'text' field")
        if not city:
            raise ValueError("News record requires 'city' field")

        # Create and return new NewsRecord instance
        return cls(text, city)

    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'NewsRecord':
        """
        Create NewsRecord instance from XML element.

        Args:
            element: XML Element containing record data

        Returns:
            NewsRecord instance
        """
        # Extract required fields from XML element
        text_elem = element.find('text')
        city_elem = element.find('city')

        # Validate required elements exist
        if text_elem is None or not text_elem.text:
            raise ValueError("News record requires 'text' element with content")
        if city_elem is None or not city_elem.text:
            raise ValueError("News record requires 'city' element with content")

        # Extract text content from elements
        text = text_elem.text.strip()
        city = city_elem.text.strip()

        # Create and return new NewsRecord instance
        return cls(text, city)


class PrivateAdRecord(FeedRecord):
    """
    Private advertisement record with expiration date and days calculation.
    """

    def __init__(self, text: str, expiration_date: str = ""):
        """
        Initialize private ad record with text and optional expiration date.

        Args:
            text: The advertisement text content
            expiration_date: Expiration date in YYYY-MM-DD format (optional)
        """
        super().__init__(text)
        self.expiration_date_str = expiration_date
        self.expiration_date = None
        self.days_left = 0

    def get_user_input(self) -> None:
        """
        Get expiration date input from user for private ad record.
        """
        if not self.expiration_date_str:
            while True:
                self.expiration_date_str = input("Enter expiration date (YYYY-MM-DD): ").strip()
                try:
                    # Validate date format and calculate days left
                    self.expiration_date = datetime.strptime(self.expiration_date_str, "%Y-%m-%d")
                    self.days_left = (self.expiration_date - datetime.now()).days
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD format.")
        else:
            # Parse provided expiration date
            try:
                self.expiration_date = datetime.strptime(self.expiration_date_str, "%Y-%m-%d")
                self.days_left = (self.expiration_date - datetime.now()).days
            except ValueError:
                raise ValueError(f"Invalid expiration date format: {self.expiration_date_str}")

    def format_for_publication(self) -> str:
        """
        Format private ad record for publication with expiration info.

        Returns:
            Formatted string ready for publication
        """
        # Ensure expiration date is calculated
        if self.expiration_date is None:
            self.get_user_input()

        # Create formatted private ad entry
        formatted_text = f"Private Ad -------------------\n"
        formatted_text += f"{self.text}\n"
        formatted_text += f"Actual until: {self.expiration_date_str}, {self.days_left} days left\n\n"

        return formatted_text

    def get_record_type_name(self) -> str:
        """
        Return the display name for private ad records.
        """
        return "Private Ad"

    def get_database_data(self) -> Dict:
        """
        Get private ad record data formatted for database storage.

        Returns:
            Dictionary containing private ad record data for database insertion
        """
        # Ensure expiration date is parsed
        if self.expiration_date is None and self.expiration_date_str:
            try:
                self.expiration_date = datetime.strptime(self.expiration_date_str, "%Y-%m-%d")
                self.days_left = (self.expiration_date - datetime.now()).days
            except ValueError:
                pass

        return {
            'text': self.text,
            'expiration_date': self.expiration_date_str,
            'days_left': self.days_left,
            'timestamp': self.timestamp.isoformat(),
            'content_hash': self.generate_content_hash()
        }

    def get_duplicate_check_fields(self) -> List[str]:
        """
        Get list of field names to use for duplicate checking in private ad records.

        Returns:
            List of field names for duplicate checking
        """
        return ['text', 'expiration_date']

    @classmethod
    def from_json_data(cls, data: Dict) -> 'PrivateAdRecord':
        """
        Create PrivateAdRecord instance from JSON data.

        Args:
            data: Dictionary containing record data from JSON

        Returns:
            PrivateAdRecord instance
        """
        # Extract required fields from JSON data
        text = data.get('text', '')
        expiration_date = data.get('expiration_date', '')

        # Validate required fields
        if not text:
            raise ValueError("Private Ad record requires 'text' field")
        if not expiration_date:
            raise ValueError("Private Ad record requires 'expiration_date' field")

        # Create and return new PrivateAdRecord instance
        return cls(text, expiration_date)

    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'PrivateAdRecord':
        """
        Create PrivateAdRecord instance from XML element.

        Args:
            element: XML Element containing record data

        Returns:
            PrivateAdRecord instance
        """
        # Extract required fields from XML element
        text_elem = element.find('text')
        expiration_elem = element.find('expiration_date')

        # Validate required elements exist
        if text_elem is None or not text_elem.text:
            raise ValueError("Private Ad record requires 'text' element with content")
        if expiration_elem is None or not expiration_elem.text:
            raise ValueError("Private Ad record requires 'expiration_date' element with content")

        # Extract text content from elements
        text = text_elem.text.strip()
        expiration_date = expiration_elem.text.strip()

        # Create and return new PrivateAdRecord instance
        return cls(text, expiration_date)


class WeatherAlertRecord(FeedRecord):
    """
    Weather alert record with severity level and auto-generated alert ID.
    """

    def __init__(self, text: str, severity: str = "", location: str = ""):
        """
        Initialize weather alert record.

        Args:
            text: The weather alert text content
            severity: Alert severity level (optional)
            location: Location for the alert (optional)
        """
        super().__init__(text)
        self.severity = severity
        self.location = location
        self.alert_id = self._generate_alert_id()

    def _generate_alert_id(self) -> str:
        """
        Generate unique alert ID for weather alert.

        Returns:
            Unique alert ID string
        """
        # Generate random 4-character alphanumeric ID
        alert_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"WA-{alert_id}"

    def get_user_input(self) -> None:
        """
        Get severity and location input from user for weather alert.
        """
        if not self.severity:
            severity_options = ["Low", "Medium", "High", "Critical"]
            print(f"Available severity levels: {', '.join(severity_options)}")
            while True:
                self.severity = input("Enter alert severity level: ").strip().title()
                if self.severity in severity_options:
                    break
                print(f"Invalid severity. Please choose from: {', '.join(severity_options)}")

        if not self.location:
            self.location = input("Enter location for weather alert: ").strip()
            while not self.location:
                print("Location cannot be empty!")
                self.location = input("Enter location for weather alert: ").strip()

    def format_for_publication(self) -> str:
        """
        Format weather alert record for publication.

        Returns:
            Formatted string ready for publication
        """
        # Ensure all required fields are available
        if not self.severity or not self.location:
            self.get_user_input()

        # Format timestamp for display
        formatted_date = self.timestamp.strftime("%Y-%m-%d %H:%M")

        # Create formatted weather alert entry
        formatted_text = f"Weather Alert ----------------\n"
        formatted_text += f"Alert ID: {self.alert_id}\n"
        formatted_text += f"Severity: {self.severity}\n"
        formatted_text += f"{self.text}\n"
        formatted_text += f"Location: {self.location}, {formatted_date}\n\n"

        return formatted_text

    def get_record_type_name(self) -> str:
        """
        Return the display name for weather alert records.
        """
        return "Weather Alert"

    def get_database_data(self) -> Dict:
        """
        Get weather alert record data formatted for database storage.

        Returns:
            Dictionary containing weather alert record data for database insertion
        """
        return {
            'text': self.text,
            'severity': self.severity,
            'location': self.location,
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'content_hash': self.generate_content_hash()
        }

    def get_duplicate_check_fields(self) -> List[str]:
        """
        Get list of field names to use for duplicate checking in weather alert records.

        Returns:
            List of field names for duplicate checking
        """
        return ['text', 'severity', 'location']

    @classmethod
    def from_json_data(cls, data: Dict) -> 'WeatherAlertRecord':
        """
        Create WeatherAlertRecord instance from JSON data.

        Args:
            data: Dictionary containing record data from JSON

        Returns:
            WeatherAlertRecord instance
        """
        # Extract required fields from JSON data
        text = data.get('text', '')
        severity = data.get('severity', '')
        location = data.get('location', '')

        # Validate required fields
        if not text:
            raise ValueError("Weather Alert record requires 'text' field")
        if not severity:
            raise ValueError("Weather Alert record requires 'severity' field")
        if not location:
            raise ValueError("Weather Alert record requires 'location' field")

        # Create and return new WeatherAlertRecord instance
        return cls(text, severity, location)

    @classmethod
    def from_xml_element(cls, element: ET.Element) -> 'WeatherAlertRecord':
        """
        Create WeatherAlertRecord instance from XML element.

        Args:
            element: XML Element containing record data

        Returns:
            WeatherAlertRecord instance
        """
        # Extract required fields from XML element
        text_elem = element.find('text')
        severity_elem = element.find('severity')
        location_elem = element.find('location')

        # Validate required elements exist
        if text_elem is None or not text_elem.text:
            raise ValueError("Weather Alert record requires 'text' element with content")
        if severity_elem is None or not severity_elem.text:
            raise ValueError("Weather Alert record requires 'severity' element with content")
        if location_elem is None or not location_elem.text:
            raise ValueError("Weather Alert record requires 'location' element with content")

        # Extract text content from elements
        text = text_elem.text.strip()
        severity = severity_elem.text.strip()
        location = location_elem.text.strip()

        # Create and return new WeatherAlertRecord instance
        return cls(text, severity, location)


# =============================================================================
# NEW DATABASE MANAGER CLASS
# =============================================================================

class DatabaseManager:
    """
    Database manager class to handle SQLite database operations.
    Creates separate tables for different record types and implements duplicate checking.
    """

    def __init__(self, database_path: str = "news_feed.db"):
        """
        Initialize database manager with SQLite database.

        Args:
            database_path: Path to SQLite database file
        """
        # Set database path
        self.database_path = database_path

        # Define table schemas for different record types
        self.table_schemas = {
            'news': {
                'table_name': 'news_records',
                'schema': '''
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    city TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                '''
            },
            'private_ad': {
                'table_name': 'private_ad_records',
                'schema': '''
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    expiration_date TEXT NOT NULL,
                    days_left INTEGER,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                '''
            },
            'weather_alert': {
                'table_name': 'weather_alert_records',
                'schema': '''
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    location TEXT NOT NULL,
                    alert_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                '''
            }
        }

        # Initialize database and create tables
        self.initialize_database()

    def initialize_database(self) -> None:
        """
        Initialize database and create tables if they don't exist.
        """
        try:
            # Connect to database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Create tables for each record type
                for record_type, table_info in self.table_schemas.items():
                    table_name = table_info['table_name']
                    schema = table_info['schema']

                    # Create table
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")

                # Commit changes
                conn.commit()

            print(f"Database initialized successfully: {self.database_path}")

        except Exception as e:
            print(f"Error initializing database: {e}")
            raise

    def get_table_name_for_record(self, record: FeedRecord) -> str:
        """
        Get the appropriate table name for a given record type.

        Args:
            record: FeedRecord instance

        Returns:
            Table name for the record type
        """
        # Map record classes to table names
        record_type_mapping = {
            NewsRecord: 'news',
            PrivateAdRecord: 'private_ad',
            WeatherAlertRecord: 'weather_alert'
        }

        # Get record type
        record_type = type(record)
        if record_type not in record_type_mapping:
            raise ValueError(f"Unsupported record type: {record_type}")

        # Get table name
        table_key = record_type_mapping[record_type]
        return self.table_schemas[table_key]['table_name']

    def check_duplicate(self, record: FeedRecord) -> bool:
        """
        Check if a record already exists in the database (duplicate check).

        Args:
            record: FeedRecord instance to check

        Returns:
            True if record is a duplicate, False otherwise
        """
        try:
            # Get table name and content hash
            table_name = self.get_table_name_for_record(record)
            content_hash = record.generate_content_hash()

            # Connect to database and check for duplicate
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Query for existing record with same content hash
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE content_hash = ?",
                    (content_hash,)
                )

                # Get count
                count = cursor.fetchone()[0]

                return count > 0

        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return False

    def save_record(self, record: FeedRecord) -> bool:
        """
        Save a record to the appropriate database table.

        Args:
            record: FeedRecord instance to save

        Returns:
            True if record was saved successfully, False otherwise
        """
        try:
            # Check for duplicates first
            if self.check_duplicate(record):
                print(f"Duplicate record detected - skipping save for {record.get_record_type_name()}")
                return False

            # Get table name and record data
            table_name = self.get_table_name_for_record(record)
            record_data = record.get_database_data()

            # Prepare SQL insert statement
            columns = list(record_data.keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)

            sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            values = list(record_data.values())

            # Connect to database and insert record
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()

                # Get inserted record ID
                record_id = cursor.lastrowid

            print(f"✓ {record.get_record_type_name()} record saved to database (ID: {record_id})")
            return True

        except sqlite3.IntegrityError as e:
            print(f"✗ Duplicate record detected (integrity constraint): {e}")
            return False
        except Exception as e:
            print(f"✗ Error saving record to database: {e}")
            return False

    def get_record_count(self, record_type: Optional[str] = None) -> Dict[str, int]:
        """
        Get count of records in database, optionally filtered by record type.

        Args:
            record_type: Optional record type to filter by ('news', 'private_ad', 'weather_alert')

        Returns:
            Dictionary with record counts by type
        """
        try:
            counts = {}

            # Connect to database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Get counts for specified type or all types
                if record_type and record_type in self.table_schemas:
                    table_name = self.table_schemas[record_type]['table_name']
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    counts[record_type] = cursor.fetchone()[0]
                else:
                    # Get counts for all record types
                    for rec_type, table_info in self.table_schemas.items():
                        table_name = table_info['table_name']
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        counts[rec_type] = cursor.fetchone()[0]

            return counts

        except Exception as e:
            print(f"Error getting record counts: {e}")
            return {}

    def get_recent_records(self, record_type: str, limit: int = 10) -> List[Dict]:
        """
        Get recent records from database for a specific record type.

        Args:
            record_type: Record type ('news', 'private_ad', 'weather_alert')
            limit: Maximum number of records to return

        Returns:
            List of record dictionaries
        """
        try:
            # Validate record type
            if record_type not in self.table_schemas:
                raise ValueError(f"Invalid record type: {record_type}")

            # Get table name
            table_name = self.table_schemas[record_type]['table_name']

            # Connect to database and fetch records
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                cursor = conn.cursor()

                cursor.execute(
                    f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )

                # Convert rows to dictionaries
                records = [dict(row) for row in cursor.fetchall()]

            return records

        except Exception as e:
            print(f"Error fetching recent records: {e}")
            return []

    def clear_all_records(self) -> bool:
        """
        Clear all records from all tables (for testing purposes).

        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Clear all tables
                for table_info in self.table_schemas.values():
                    table_name = table_info['table_name']
                    cursor.execute(f"DELETE FROM {table_name}")

                # Commit changes
                conn.commit()

            print("All database records cleared successfully")
            return True

        except Exception as e:
            print(f"Error clearing database records: {e}")
            return False

    def get_database_info(self) -> Dict:
        """
        Get comprehensive information about the database.

        Returns:
            Dictionary with database information
        """
        try:
            info = {
                'database_path': self.database_path,
                'database_exists': os.path.exists(self.database_path),
                'tables': {},
                'total_records': 0
            }

            if info['database_exists']:
                # Get record counts
                counts = self.get_record_count()
                info['record_counts'] = counts
                info['total_records'] = sum(counts.values())

                # Get table information
                with sqlite3.connect(self.database_path) as conn:
                    cursor = conn.cursor()

                    for record_type, table_info in self.table_schemas.items():
                        table_name = table_info['table_name']

                        # Get table info
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()

                        info['tables'][record_type] = {
                            'table_name': table_name,
                            'columns': [col[1] for col in columns],
                            'record_count': counts.get(record_type, 0)
                        }

            return info

        except Exception as e:
            print(f"Error getting database info: {e}")
            return {'error': str(e)}


# =============================================================================
# JSON FILE PROCESSOR CLASS (FROM HOMEWORK 9)
# =============================================================================

class JSONFileProcessor:
    """
    Class to handle JSON file processing for news feed records.
    Supports single and multiple record formats with configurable file paths.
    """

    def __init__(self, default_folder: str = "json_input"):
        """
        Initialize JSON file processor with default folder configuration.

        Args:
            default_folder: Default folder path for JSON input files
        """
        # Set default folder for JSON input files
        self.default_folder = Path(default_folder)

        # Create default folder if it doesn't exist
        self.default_folder.mkdir(exist_ok=True)

        # Define supported record types and their corresponding classes
        self.record_type_mapping = {
            'news': NewsRecord,
            'private_ad': PrivateAdRecord,
            'weather_alert': WeatherAlertRecord
        }

        # Track processed files for cleanup
        self.processed_files = []

    def process_json_file(self, user_provided_path: Optional[str] = None) -> List[FeedRecord]:
        """
        Main method to process JSON file and return record objects.

        Args:
            user_provided_path: Optional user-provided file path

        Returns:
            List of processed FeedRecord objects
        """
        try:
            # Get file path (user provided or from default folder)
            file_path = self._get_file_path(user_provided_path, "*.json")

            # Load JSON file content
            json_data = self._load_json_file(file_path)

            # Parse records from JSON data
            records = self._parse_json_records(json_data)

            if records:
                # Add file to processed files list for cleanup
                self.processed_files.append(file_path)
                print(f"\nSuccessfully processed {len(records)} records from {file_path.name}")
            else:
                print(f"No valid records found in {file_path.name}")

            return records

        except Exception as e:
            print(f"Error processing JSON file: {e}")
            return []

    def _get_file_path(self, user_provided_path: Optional[str], pattern: str) -> Path:
        """Get file path - either user provided or from default folder."""
        if user_provided_path:
            file_path = Path(user_provided_path)
            if not file_path.exists():
                raise FileNotFoundError(f"User-provided file not found: {file_path}")
        else:
            files = list(self.default_folder.glob(pattern))
            if not files:
                raise FileNotFoundError(f"No {pattern} files found in default folder: {self.default_folder}")

            if len(files) == 1:
                file_path = files[0]
                print(f"Processing file from default folder: {file_path.name}")
            else:
                print(f"Found {len(files)} {pattern} files in default folder:")
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file.name}")

                while True:
                    try:
                        choice = int(input("Choose file number to process: ")) - 1
                        if 0 <= choice < len(files):
                            file_path = files[choice]
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")

        return file_path

    def _load_json_file(self, file_path: Path) -> Dict:
        """Load and parse JSON file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            print(f"Successfully loaded JSON file: {file_path.name}")
            return json_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in file {file_path.name}: {e}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path.name}: {e}")

    def _parse_json_records(self, json_data: Dict) -> List[FeedRecord]:
        """Parse JSON data and create record objects."""
        records = []

        if 'records' in json_data:
            print(f"Processing multiple records format with {len(json_data['records'])} records")

            for i, record_info in enumerate(json_data['records'], 1):
                try:
                    record_type = record_info.get('type', '').lower()
                    record_data = record_info.get('data', {})

                    record_class = self.record_type_mapping[record_type]
                    record = record_class.from_json_data(record_data)
                    records.append(record)

                    print(f"  ✓ Record {i}: {record_type} processed successfully")

                except Exception as e:
                    print(f"  ✗ Error processing record {i}: {e}")
                    continue

        elif 'type' in json_data and 'data' in json_data:
            print("Processing single record format")

            try:
                record_type = json_data.get('type', '').lower()
                record_data = json_data.get('data', {})

                record_class = self.record_type_mapping[record_type]
                record = record_class.from_json_data(record_data)
                records.append(record)

                print(f"  ✓ {record_type} record processed successfully")

            except Exception as e:
                print(f"  ✗ Error processing record: {e}")

        else:
            raise ValueError("Invalid JSON format. Expected 'records' array or single record with 'type' and 'data'")

        return records

    def cleanup_processed_files(self) -> None:
        """Remove all successfully processed files."""
        if not self.processed_files:
            print("No files to clean up.")
            return

        print(f"\nCleaning up {len(self.processed_files)} processed files...")

        removed_count = 0
        for file_path in self.processed_files:
            try:
                file_path.unlink()
                print(f"Successfully removed processed file: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing file {file_path.name}: {e}")

        print(f"Cleanup completed: {removed_count}/{len(self.processed_files)} files removed")
        self.processed_files.clear()


# =============================================================================
# XML FILE PROCESSOR CLASS (FROM HOMEWORK 9)
# =============================================================================

class XMLFileProcessor:
    """
    Class to handle XML file processing for news feed records.
    Supports single and multiple record formats with configurable file paths.
    """

    def __init__(self, default_folder: str = "xml_input"):
        """
        Initialize XML file processor with default folder configuration.

        Args:
            default_folder: Default folder path for XML input files
        """
        # Set default folder for XML input files
        self.default_folder = Path(default_folder)

        # Create default folder if it doesn't exist
        self.default_folder.mkdir(exist_ok=True)

        # Define supported record types and their corresponding classes
        self.record_type_mapping = {
            'news': NewsRecord,
            'private_ad': PrivateAdRecord,
            'weather_alert': WeatherAlertRecord
        }

        # Track processed files for cleanup
        self.processed_files = []

    def process_xml_file(self, user_provided_path: Optional[str] = None) -> List[FeedRecord]:
        """
        Main method to process XML file and return record objects.

        Args:
            user_provided_path: Optional user-provided file path

        Returns:
            List of processed FeedRecord objects
        """
        try:
            # Get file path (user provided or from default folder)
            file_path = self._get_file_path(user_provided_path)

            # Load XML file content
            root = self._load_xml_file(file_path)

            # Parse records from XML data
            records = self._parse_xml_records(root)

            if records:
                # Add file to processed files list for cleanup
                self.processed_files.append(file_path)
                print(f"\nSuccessfully processed {len(records)} records from {file_path.name}")
            else:
                print(f"No valid records found in {file_path.name}")

            return records

        except Exception as e:
            print(f"Error processing XML file: {e}")
            return []

    def _get_file_path(self, user_provided_path: Optional[str]) -> Path:
        """Get file path - either user provided or from default folder."""
        if user_provided_path:
            file_path = Path(user_provided_path)
            if not file_path.exists():
                raise FileNotFoundError(f"User-provided file not found: {file_path}")
        else:
            xml_files = list(self.default_folder.glob("*.xml"))
            if not xml_files:
                raise FileNotFoundError(f"No XML files found in default folder: {self.default_folder}")

            if len(xml_files) == 1:
                file_path = xml_files[0]
                print(f"Processing file from default folder: {file_path.name}")
            else:
                print(f"Found {len(xml_files)} XML files in default folder:")
                for i, file in enumerate(xml_files, 1):
                    print(f"{i}. {file.name}")

                while True:
                    try:
                        choice = int(input("Choose file number to process: ")) - 1
                        if 0 <= choice < len(xml_files):
                            file_path = xml_files[choice]
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")

        return file_path

    def _load_xml_file(self, file_path: Path) -> ET.Element:
        """Load and parse XML file content."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            print(f"Successfully loaded XML file: {file_path.name}")
            return root
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format in file {file_path.name}: {e}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path.name}: {e}")

    def _parse_xml_records(self, root: ET.Element) -> List[FeedRecord]:
        """Parse XML data and create record objects."""
        records = []

        if root.tag == 'records':
            record_elements = root.findall('record')
            print(f"Processing multiple records format with {len(record_elements)} records")

            for i, record_element in enumerate(record_elements, 1):
                try:
                    record_type = record_element.get('type', '').lower()

                    record_class = self.record_type_mapping[record_type]
                    record = record_class.from_xml_element(record_element)
                    records.append(record)

                    print(f"  ✓ Record {i}: {record_type} processed successfully")

                except Exception as e:
                    print(f"  ✗ Error processing record {i}: {e}")
                    continue

        elif root.tag == 'record':
            print("Processing single record format")

            try:
                record_type = root.get('type', '').lower()

                record_class = self.record_type_mapping[record_type]
                record = record_class.from_xml_element(root)
                records.append(record)

                print(f"  ✓ {record_type} record processed successfully")

            except Exception as e:
                print(f"  ✗ Error processing record: {e}")

        else:
            raise ValueError("Invalid XML format. Expected root element 'records' or 'record'")

        return records

    def cleanup_processed_files(self) -> None:
        """Remove all successfully processed files."""
        if not self.processed_files:
            print("No files to clean up.")
            return

        print(f"\nCleaning up {len(self.processed_files)} processed files...")

        removed_count = 0
        for file_path in self.processed_files:
            try:
                file_path.unlink()
                print(f"Successfully removed processed file: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing file {file_path.name}: {e}")

        print(f"Cleanup completed: {removed_count}/{len(self.processed_files)} files removed")
        self.processed_files.clear()


# =============================================================================
# ENHANCED NEWS FEED MANAGER WITH DATABASE SUPPORT
# =============================================================================

class EnhancedNewsFeedManager:
    """
    Enhanced news feed manager with JSON, XML, and database capabilities.
    Extends the original functionality with database storage and duplicate checking.
    """

    def __init__(self, output_file: str = "news_feed.txt", json_folder: str = "json_input",
                 xml_folder: str = "xml_input", database_path: str = "news_feed.db"):
        """
        Initialize enhanced news feed manager.

        Args:
            output_file: Output file for news feed
            json_folder: Default folder for JSON input files
            xml_folder: Default folder for XML input files
            database_path: Path to SQLite database file
        """
        # Initialize output file for news feed
        self.output_file = output_file

        # Initialize processors
        self.json_processor = JSONFileProcessor(json_folder)
        self.xml_processor = XMLFileProcessor(xml_folder)
        self.database_manager = DatabaseManager(database_path)

        # Define available record types for manual entry
        self.record_types = {
            '1': NewsRecord,
            '2': PrivateAdRecord,
            '3': WeatherAlertRecord
        }

    def append_to_file(self, content: str) -> None:
        """Append formatted content to the news feed file."""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as file:
                file.write(content)
            print("Record published to file successfully!")
        except Exception as e:
            print(f"Error writing to file: {e}")

    def publish_record(self, record: FeedRecord, save_to_database: bool = True) -> bool:
        """
        Publish a single record to both file and database.

        Args:
            record: FeedRecord object to publish
            save_to_database: Whether to save to database

        Returns:
            True if record was successfully processed, False otherwise
        """
        success = True

        try:
            # Save to database first (with duplicate checking)
            if save_to_database:
                db_success = self.database_manager.save_record(record)
                if not db_success:
                    print("Record not saved to database (duplicate or error)")
                    return False  # Don't save to file if database save failed due to duplicate

            # Save to file
            formatted_content = record.format_for_publication()
            self.append_to_file(formatted_content)

        except Exception as e:
            print(f"Error publishing record: {e}")
            success = False

        return success

    def publish_manual_record(self) -> None:
        """Handle manual record creation and publication through user input."""
        print("\n" + "=" * 50)
        print("MANUAL RECORD CREATION")
        print("=" * 50)

        print("Select record type to create:")
        print("1. News")
        print("2. Private Ad")
        print("3. Weather Alert")
        print("4. Back to main menu")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '4':
            return

        if choice not in self.record_types:
            print("Invalid choice. Please try again.")
            return

        try:
            text = input("Enter record text content: ").strip()
            while not text:
                print("Text content cannot be empty!")
                text = input("Enter record text content: ").strip()

            record_class = self.record_types[choice]
            record = record_class(text)
            record.get_user_input()

            # Ask user about database saving
            save_to_db = input("Save to database? (y/n, default: y): ").strip().lower()
            save_to_database = save_to_db != 'n'

            # Publish the record
            if self.publish_record(record, save_to_database):
                print("✓ Record created and published successfully!")
            else:
                print("✗ Record creation failed or was skipped due to duplicate")

        except Exception as e:
            print(f"Error creating manual record: {e}")

    def publish_from_json(self) -> None:
        """Handle JSON file processing and publication of records."""
        print("\n" + "=" * 50)
        print("JSON FILE PROCESSING")
        print("=" * 50)

        print("Choose JSON file source:")
        print("1. Use default folder (json_input)")
        print("2. Specify custom file path")
        print("3. Back to main menu")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '3':
            return
        elif choice == '1':
            file_path = None
        elif choice == '2':
            file_path = input("Enter full path to JSON file: ").strip()
            if not file_path:
                print("File path cannot be empty!")
                return
        else:
            print("Invalid choice. Please try again.")
            return

        records = self.json_processor.process_json_file(file_path)
        self._process_file_records(records, self.json_processor)

    def publish_from_xml(self) -> None:
        """Handle XML file processing and publication of records."""
        print("\n" + "=" * 50)
        print("XML FILE PROCESSING")
        print("=" * 50)

        print("Choose XML file source:")
        print("1. Use default folder (xml_input)")
        print("2. Specify custom file path")
        print("3. Back to main menu")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '3':
            return
        elif choice == '1':
            file_path = None
        elif choice == '2':
            file_path = input("Enter full path to XML file: ").strip()
            if not file_path:
                print("File path cannot be empty!")
                return
        else:
            print("Invalid choice. Please try again.")
            return

        records = self.xml_processor.process_xml_file(file_path)
        self._process_file_records(records, self.xml_processor)

    def _process_file_records(self, records: List[FeedRecord], processor) -> None:
        """Common method to process and publish records from any file type."""
        try:
            if records:
                # Ask user about database saving
                save_to_db = input("Save records to database? (y/n, default: y): ").strip().lower()
                save_to_database = save_to_db != 'n'

                print(f"\nPublishing {len(records)} records...")
                published_count = 0
                skipped_count = 0

                for i, record in enumerate(records, 1):
                    try:
                        if self.publish_record(record, save_to_database):
                            published_count += 1
                            print(f"  ✓ Record {i} published successfully")
                        else:
                            skipped_count += 1
                            print(f"  - Record {i} skipped (duplicate)")
                    except Exception as e:
                        print(f"  ✗ Error publishing record {i}: {e}")

                print(f"\nPublication completed:")
                print(f"  - Published: {published_count}/{len(records)} records")
                print(f"  - Skipped (duplicates): {skipped_count}/{len(records)} records")

                # Ask user about file cleanup
                cleanup_choice = input("\nRemove processed file? (y/n): ").strip().lower()
                if cleanup_choice == 'y':
                    processor.cleanup_processed_files()
            else:
                print("No records to publish.")

        except Exception as e:
            print(f"Error processing file records: {e}")

    def view_database_info(self) -> None:
        """Display comprehensive database information."""
        print("\n" + "=" * 50)
        print("DATABASE INFORMATION")
        print("=" * 50)

        try:
            info = self.database_manager.get_database_info()

            print(f"Database Path: {info.get('database_path', 'Unknown')}")
            print(f"Database Exists: {info.get('database_exists', False)}")
            print(f"Total Records: {info.get('total_records', 0)}")

            if 'record_counts' in info:
                print("\nRecord Counts by Type:")
                for record_type, count in info['record_counts'].items():
                    print(f"  - {record_type.replace('_', ' ').title()}: {count}")

            if 'tables' in info:
                print("\nTable Information:")
                for record_type, table_info in info['tables'].items():
                    print(f"  {record_type.replace('_', ' ').title()}:")
                    print(f"    Table: {table_info['table_name']}")
                    print(f"    Columns: {', '.join(table_info['columns'])}")
                    print(f"    Records: {table_info['record_count']}")

        except Exception as e:
            print(f"Error getting database information: {e}")

    def view_recent_records(self) -> None:
        """Display recent records from database."""
        print("\n" + "=" * 50)
        print("RECENT DATABASE RECORDS")
        print("=" * 50)

        print("Select record type to view:")
        print("1. News Records")
        print("2. Private Ad Records")
        print("3. Weather Alert Records")
        print("4. Back to main menu")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '4':
            return

        record_type_map = {
            '1': 'news',
            '2': 'private_ad',
            '3': 'weather_alert'
        }

        if choice not in record_type_map:
            print("Invalid choice.")
            return

        record_type = record_type_map[choice]

        try:
            limit = int(input("Number of recent records to show (default: 10): ") or "10")
            records = self.database_manager.get_recent_records(record_type, limit)

            if records:
                print(f"\nShowing {len(records)} most recent {record_type.replace('_', ' ')} records:")
                print("-" * 80)

                for i, record in enumerate(records, 1):
                    print(f"{i}. ID: {record['id']}")
                    print(f"   Text: {record['text'][:100]}{'...' if len(record['text']) > 100 else ''}")
                    if record_type == 'news':
                        print(f"   City: {record['city']}")
                    elif record_type == 'private_ad':
                        print(f"   Expiration: {record['expiration_date']} ({record['days_left']} days left)")
                    elif record_type == 'weather_alert':
                        print(f"   Severity: {record['severity']}, Location: {record['location']}")
                        print(f"   Alert ID: {record['alert_id']}")
                    print(f"   Created: {record['created_at']}")
                    print("-" * 80)
            else:
                print(f"No {record_type.replace('_', ' ')} records found in database.")

        except ValueError:
            print("Invalid number entered.")
        except Exception as e:
            print(f"Error viewing recent records: {e}")

    def clear_database(self) -> None:
        """Clear all records from database."""
        print("\n" + "=" * 50)
        print("CLEAR DATABASE")
        print("=" * 50)

        confirm = input("Are you sure you want to clear ALL database records? (yes/no): ").strip().lower()
        if confirm == 'yes':
            if self.database_manager.clear_all_records():
                print("✓ All database records cleared successfully!")
            else:
                print("✗ Failed to clear database records.")
        else:
            print("Clear operation cancelled.")

    def view_news_feed(self) -> None:
        """Display the current contents of the news feed file."""
        try:
            if not os.path.exists(self.output_file):
                print("News feed file doesn't exist yet. No records published.")
                return

            with open(self.output_file, 'r', encoding='utf-8') as file:
                content = file.read()

            if content.strip():
                print("\n" + "=" * 50)
                print("CURRENT NEWS FEED CONTENT")
                print("=" * 50)
                print(content)
            else:
                print("News feed file is empty. No records published yet.")

        except Exception as e:
            print(f"Error reading news feed file: {e}")

    def clear_news_feed(self) -> None:
        """Clear the contents of the news feed file."""
        try:
            confirm = input("Are you sure you want to clear the news feed file? (y/n): ").strip().lower()
            if confirm == 'y':
                with open(self.output_file, 'w', encoding='utf-8') as file:
                    file.write("")
                print("News feed file cleared successfully!")
            else:
                print("Clear operation cancelled.")
        except Exception as e:
            print(f"Error clearing news feed file: {e}")

    def run(self) -> None:
        """Main application loop with enhanced menu including database functionality."""
        print("=" * 70)
        print("ENHANCED NEWS FEED SYSTEM WITH DATABASE STORAGE")
        print("=" * 70)
        print("Welcome to the enhanced news feed management system!")
        print("This system supports manual input, JSON/XML processing, and database storage.")

        while True:
            print("\n" + "=" * 50)
            print("MAIN MENU")
            print("=" * 50)
            print("1. Create record manually")
            print("2. Import records from JSON file")
            print("3. Import records from XML file")
            print("4. View database information")
            print("5. View recent database records")
            print("6. View current news feed file")
            print("7. Clear news feed file")
            print("8. Clear database")
            print("9. Exit")

            choice = input("Enter your choice (1-9): ").strip()

            if choice == '1':
                self.publish_manual_record()
            elif choice == '2':
                self.publish_from_json()
            elif choice == '3':
                self.publish_from_xml()
            elif choice == '4':
                self.view_database_info()
            elif choice == '5':
                self.view_recent_records()
            elif choice == '6':
                self.view_news_feed()
            elif choice == '7':
                self.clear_news_feed()
            elif choice == '8':
                self.clear_database()
            elif choice == '9':
                print("Thank you for using the Enhanced News Feed System with Database!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 9.")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function to run the enhanced news feed system with database support.
    """
    try:
        # Create and run the enhanced news feed manager
        manager = EnhancedNewsFeedManager()
        manager.run()

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Run the main application
    main()