"""
Homework 8: Enhanced News Feed System with JSON File Processing
==============================================================
This module extends Homework 5, 6, and 7 with additional JSON file processing capabilities.
Includes functionality to:
- Process records from JSON files
- Support single and multiple record formats
- Handle default and custom file paths
- Remove processed files automatically
"""

import json
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
# BASE CLASSES FROM PREVIOUS HOMEWORKS (REUSED)
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


# =============================================================================
# NEW JSON FILE PROCESSOR CLASS
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

    def define_input_format(self) -> Dict:
        """
        Define and return the expected JSON input format documentation.

        Returns:
            Dictionary describing the expected JSON format
        """
        # Define format specification for JSON input files
        format_spec = {
            "description": "JSON file format specification for news feed records",
            "supported_formats": {
                "single_record": {
                    "structure": {
                        "type": "string (news, private_ad, weather_alert)",
                        "data": "object containing record-specific fields"
                    },
                    "example": {
                        "type": "news",
                        "data": {
                            "text": "Breaking news content",
                            "city": "New York"
                        }
                    }
                },
                "multiple_records": {
                    "structure": {
                        "records": "array of record objects"
                    },
                    "example": {
                        "records": [
                            {
                                "type": "news",
                                "data": {
                                    "text": "News content 1",
                                    "city": "London"
                                }
                            },
                            {
                                "type": "private_ad",
                                "data": {
                                    "text": "Advertisement content",
                                    "expiration_date": "2025-12-31"
                                }
                            }
                        ]
                    }
                }
            },
            "record_types": {
                "news": {
                    "required_fields": ["text", "city"],
                    "description": "News record with text and city information"
                },
                "private_ad": {
                    "required_fields": ["text", "expiration_date"],
                    "description": "Private advertisement with expiration date (YYYY-MM-DD format)"
                },
                "weather_alert": {
                    "required_fields": ["text", "severity", "location"],
                    "description": "Weather alert with severity level and location"
                }
            }
        }

        return format_spec

    def get_file_path(self, user_provided_path: Optional[str] = None) -> Path:
        """
        Get file path - either user provided or from default folder.

        Args:
            user_provided_path: Optional user-provided file path

        Returns:
            Path object for the JSON file to process
        """
        if user_provided_path:
            # Use user-provided file path
            file_path = Path(user_provided_path)
            if not file_path.exists():
                raise FileNotFoundError(f"User-provided file not found: {file_path}")
        else:
            # Look for JSON files in default folder
            json_files = list(self.default_folder.glob("*.json"))
            if not json_files:
                raise FileNotFoundError(f"No JSON files found in default folder: {self.default_folder}")

            # If multiple files, let user choose or take the first one
            if len(json_files) == 1:
                file_path = json_files[0]
                print(f"Processing file from default folder: {file_path.name}")
            else:
                print(f"Found {len(json_files)} JSON files in default folder:")
                for i, file in enumerate(json_files, 1):
                    print(f"{i}. {file.name}")

                while True:
                    try:
                        choice = int(input("Choose file number to process: ")) - 1
                        if 0 <= choice < len(json_files):
                            file_path = json_files[choice]
                            break
                        else:
                            print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")

        return file_path

    def load_json_file(self, file_path: Path) -> Dict:
        """
        Load and parse JSON file content.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data as dictionary
        """
        try:
            # Read and parse JSON file
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            print(f"Successfully loaded JSON file: {file_path.name}")
            return json_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in file {file_path.name}: {e}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path.name}: {e}")

    def validate_record_data(self, record_type: str, data: Dict) -> None:
        """
        Validate record data against required fields for the record type.

        Args:
            record_type: Type of record (news, private_ad, weather_alert)
            data: Record data dictionary
        """
        # Check if record type is supported
        if record_type not in self.record_type_mapping:
            raise ValueError(f"Unsupported record type: {record_type}")

        # Define required fields for each record type
        required_fields = {
            'news': ['text', 'city'],
            'private_ad': ['text', 'expiration_date'],
            'weather_alert': ['text', 'severity', 'location']
        }

        # Validate required fields are present
        missing_fields = []
        for field in required_fields[record_type]:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields for {record_type}: {missing_fields}")

    def parse_json_records(self, json_data: Dict) -> List[FeedRecord]:
        """
        Parse JSON data and create record objects.

        Args:
            json_data: Parsed JSON data

        Returns:
            List of created FeedRecord objects
        """
        records = []

        # Check if JSON contains single record or multiple records
        if 'records' in json_data:
            # Multiple records format
            print(f"Processing multiple records format with {len(json_data['records'])} records")

            for i, record_info in enumerate(json_data['records'], 1):
                try:
                    # Extract record type and data
                    record_type = record_info.get('type', '').lower()
                    record_data = record_info.get('data', {})

                    # Validate record data
                    self.validate_record_data(record_type, record_data)

                    # Create record object
                    record_class = self.record_type_mapping[record_type]
                    record = record_class.from_json_data(record_data)
                    records.append(record)

                    print(f"  ✓ Record {i}: {record_type} processed successfully")

                except Exception as e:
                    print(f"  ✗ Error processing record {i}: {e}")
                    continue

        elif 'type' in json_data and 'data' in json_data:
            # Single record format
            print("Processing single record format")

            try:
                # Extract record type and data
                record_type = json_data.get('type', '').lower()
                record_data = json_data.get('data', {})

                # Validate record data
                self.validate_record_data(record_type, record_data)

                # Create record object
                record_class = self.record_type_mapping[record_type]
                record = record_class.from_json_data(record_data)
                records.append(record)

                print(f"  ✓ {record_type} record processed successfully")

            except Exception as e:
                print(f"  ✗ Error processing record: {e}")

        else:
            raise ValueError("Invalid JSON format. Expected 'records' array or single record with 'type' and 'data'")

        return records

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
            file_path = self.get_file_path(user_provided_path)

            # Load JSON file content
            json_data = self.load_json_file(file_path)

            # Parse records from JSON data
            records = self.parse_json_records(json_data)

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

    def remove_processed_file(self, file_path: Path) -> bool:
        """
        Remove a successfully processed file.

        Args:
            file_path: Path to the file to remove

        Returns:
            True if file was removed successfully, False otherwise
        """
        try:
            # Remove the file
            file_path.unlink()
            print(f"Successfully removed processed file: {file_path.name}")
            return True

        except Exception as e:
            print(f"Error removing file {file_path.name}: {e}")
            return False

    def cleanup_processed_files(self) -> None:
        """
        Remove all successfully processed files.
        """
        if not self.processed_files:
            print("No files to clean up.")
            return

        print(f"\nCleaning up {len(self.processed_files)} processed files...")

        # Remove each processed file
        removed_count = 0
        for file_path in self.processed_files:
            if self.remove_processed_file(file_path):
                removed_count += 1

        print(f"Cleanup completed: {removed_count}/{len(self.processed_files)} files removed")

        # Clear the processed files list
        self.processed_files.clear()

    def create_sample_json_files(self) -> None:
        """
        Create sample JSON files in the default folder for testing.
        """
        # Sample single record file
        single_record_sample = {
            "type": "news",
            "data": {
                "text": "Sample news content from JSON file",
                "city": "Sample City"
            }
        }

        # Sample multiple records file
        multiple_records_sample = {
            "records": [
                {
                    "type": "news",
                    "data": {
                        "text": "First news from JSON batch processing",
                        "city": "New York"
                    }
                },
                {
                    "type": "private_ad",
                    "data": {
                        "text": "JSON-based advertisement content",
                        "expiration_date": "2025-12-31"
                    }
                },
                {
                    "type": "weather_alert",
                    "data": {
                        "text": "Severe weather warning from JSON processing",
                        "severity": "High",
                        "location": "Downtown Area"
                    }
                }
            ]
        }

        # Write sample files
        single_file_path = self.default_folder / "sample_single_record.json"
        multiple_file_path = self.default_folder / "sample_multiple_records.json"

        try:
            # Write single record sample
            with open(single_file_path, 'w', encoding='utf-8') as file:
                json.dump(single_record_sample, file, indent=2)

            # Write multiple records sample
            with open(multiple_file_path, 'w', encoding='utf-8') as file:
                json.dump(multiple_records_sample, file, indent=2)

            print(f"Sample JSON files created in {self.default_folder}:")
            print(f"  - {single_file_path.name} (single record)")
            print(f"  - {multiple_file_path.name} (multiple records)")

        except Exception as e:
            print(f"Error creating sample files: {e}")


# =============================================================================
# ENHANCED NEWS FEED MANAGER WITH JSON PROCESSING
# =============================================================================

class EnhancedNewsFeedManager:
    """
    Enhanced news feed manager with JSON file processing capabilities.
    Extends the original functionality with JSON import features.
    """

    def __init__(self, output_file: str = "news_feed.txt", json_folder: str = "json_input"):
        """
        Initialize enhanced news feed manager.

        Args:
            output_file: Output file for news feed
            json_folder: Default folder for JSON input files
        """
        # Initialize output file for news feed
        self.output_file = output_file

        # Initialize JSON file processor
        self.json_processor = JSONFileProcessor(json_folder)

        # Define available record types for manual entry
        self.record_types = {
            '1': NewsRecord,
            '2': PrivateAdRecord,
            '3': WeatherAlertRecord
        }

    def append_to_file(self, content: str) -> None:
        """
        Append formatted content to the news feed file.

        Args:
            content: Formatted content to append
        """
        try:
            # Write content to file
            with open(self.output_file, 'a', encoding='utf-8') as file:
                file.write(content)
            print("Record published successfully!")

        except Exception as e:
            print(f"Error writing to file: {e}")

    def publish_record(self, record: FeedRecord) -> None:
        """
        Publish a single record to the news feed.

        Args:
            record: FeedRecord object to publish
        """
        try:
            # Get formatted content and append to file
            formatted_content = record.format_for_publication()
            self.append_to_file(formatted_content)

        except Exception as e:
            print(f"Error publishing record: {e}")

    def publish_manual_record(self) -> None:
        """
        Handle manual record creation and publication through user input.
        """
        print("\n" + "=" * 50)
        print("MANUAL RECORD CREATION")
        print("=" * 50)

        # Display available record types
        print("Select record type to create:")
        print("1. News")
        print("2. Private Ad")
        print("3. Weather Alert")
        print("4. Back to main menu")

        # Get user choice
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '4':
            return

        if choice not in self.record_types:
            print("Invalid choice. Please try again.")
            return

        try:
            # Get record text content
            text = input("Enter record text content: ").strip()
            while not text:
                print("Text content cannot be empty!")
                text = input("Enter record text content: ").strip()

            # Create record object and get additional input
            record_class = self.record_types[choice]
            record = record_class(text)
            record.get_user_input()

            # Publish the record
            self.publish_record(record)

        except Exception as e:
            print(f"Error creating manual record: {e}")

    def publish_from_json(self) -> None:
        """
        Handle JSON file processing and publication of records.
        """
        print("\n" + "=" * 50)
        print("JSON FILE PROCESSING")
        print("=" * 50)

        print("Choose JSON file source:")
        print("1. Use default folder (json_input)")
        print("2. Specify custom file path")
        print("3. Create sample JSON files")
        print("4. Show JSON format specification")
        print("5. Back to main menu")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '5':
            return
        elif choice == '3':
            # Create sample JSON files
            self.json_processor.create_sample_json_files()
            return
        elif choice == '4':
            # Show format specification
            format_spec = self.json_processor.define_input_format()
            print("\nJSON Format Specification:")
            print(json.dumps(format_spec, indent=2))
            return
        elif choice == '1':
            # Process from default folder
            file_path = None
        elif choice == '2':
            # Get custom file path from user
            file_path = input("Enter full path to JSON file: ").strip()
            if not file_path:
                print("File path cannot be empty!")
                return
        else:
            print("Invalid choice. Please try again.")
            return

        try:
            # Process JSON file and get records
            records = self.json_processor.process_json_file(file_path)

            if records:
                # Publish all processed records
                print(f"\nPublishing {len(records)} records to news feed...")
                published_count = 0

                for i, record in enumerate(records, 1):
                    try:
                        self.publish_record(record)
                        published_count += 1
                        print(f"  ✓ Record {i} published successfully")
                    except Exception as e:
                        print(f"  ✗ Error publishing record {i}: {e}")

                print(f"\nPublication completed: {published_count}/{len(records)} records published")

                # Ask user about file cleanup
                cleanup_choice = input("\nRemove processed JSON file? (y/n): ").strip().lower()
                if cleanup_choice == 'y':
                    self.json_processor.cleanup_processed_files()
            else:
                print("No records to publish.")

        except Exception as e:
            print(f"Error processing JSON file: {e}")

    def view_news_feed(self) -> None:
        """
        Display the current contents of the news feed file.
        """
        try:
            # Check if file exists
            if not os.path.exists(self.output_file):
                print("News feed file doesn't exist yet. No records published.")
                return

            # Read and display file contents
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
        """
        Clear the contents of the news feed file.
        """
        try:
            # Confirm with user
            confirm = input("Are you sure you want to clear the news feed? (y/n): ").strip().lower()
            if confirm == 'y':
                # Clear file contents
                with open(self.output_file, 'w', encoding='utf-8') as file:
                    file.write("")
                print("News feed cleared successfully!")
            else:
                print("Clear operation cancelled.")

        except Exception as e:
            print(f"Error clearing news feed file: {e}")

    def run(self) -> None:
        """
        Main application loop with enhanced menu including JSON processing.
        """
        print("=" * 60)
        print("ENHANCED NEWS FEED SYSTEM WITH JSON PROCESSING")
        print("=" * 60)
        print("Welcome to the enhanced news feed management system!")
        print("This system now supports JSON file processing for batch record imports.")

        while True:
            print("\n" + "=" * 50)
            print("MAIN MENU")
            print("=" * 50)
            print("1. Create record manually")
            print("2. Import records from JSON file")
            print("3. View current news feed")
            print("4. Clear news feed")
            print("5. Show JSON format help")
            print("6. Exit")

            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                self.publish_manual_record()
            elif choice == '2':
                self.publish_from_json()
            elif choice == '3':
                self.view_news_feed()
            elif choice == '4':
                self.clear_news_feed()
            elif choice == '5':
                # Show format specification
                format_spec = self.json_processor.define_input_format()
                print("\nJSON Format Specification:")
                print(json.dumps(format_spec, indent=2))
            elif choice == '6':
                print("Thank you for using the Enhanced News Feed System!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function to run the enhanced news feed system.
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