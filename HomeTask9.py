"""
Homework 9: Enhanced News Feed System with XML File Processing
==============================================================
This module extends Homework 5, 6, 7, and 8 with additional XML file processing capabilities.
Includes functionality to:
- Process records from XML files
- Support single and multiple record formats
- Handle default and custom file paths
- Remove processed files automatically
- Maintain compatibility with JSON processing from Homework 8
"""

import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
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
# BASE CLASSES FROM PREVIOUS HOMEWORKS (EXTENDED WITH XML SUPPORT)
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
# JSON FILE PROCESSOR CLASS (FROM HOMEWORK 8)
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
        """
        Get file path - either user provided or from default folder.

        Args:
            user_provided_path: Optional user-provided file path
            pattern: File pattern to search for

        Returns:
            Path object for the file to process
        """
        if user_provided_path:
            # Use user-provided file path
            file_path = Path(user_provided_path)
            if not file_path.exists():
                raise FileNotFoundError(f"User-provided file not found: {file_path}")
        else:
            # Look for files in default folder
            files = list(self.default_folder.glob(pattern))
            if not files:
                raise FileNotFoundError(f"No {pattern} files found in default folder: {self.default_folder}")

            # If multiple files, let user choose or take the first one
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

    def _parse_json_records(self, json_data: Dict) -> List[FeedRecord]:
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
            if self._remove_file(file_path):
                removed_count += 1

        print(f"Cleanup completed: {removed_count}/{len(self.processed_files)} files removed")

        # Clear the processed files list
        self.processed_files.clear()

    def _remove_file(self, file_path: Path) -> bool:
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


# =============================================================================
# NEW XML FILE PROCESSOR CLASS
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

    def define_input_format(self) -> Dict:
        """
        Define and return the expected XML input format documentation.

        Returns:
            Dictionary describing the expected XML format
        """
        # Define format specification for XML input files
        format_spec = {
            "description": "XML file format specification for news feed records",
            "supported_formats": {
                "single_record": {
                    "structure": "Root element with 'type' attribute and child elements",
                    "example": """<?xml version="1.0" encoding="UTF-8"?>
<record type="news">
    <text>Breaking news content</text>
    <city>New York</city>
</record>"""
                },
                "multiple_records": {
                    "structure": "<records> root with multiple <record> children",
                    "example": """<?xml version="1.0" encoding="UTF-8"?>
<records>
    <record type="news">
        <text>News content 1</text>
        <city>London</city>
    </record>
    <record type="private_ad">
        <text>Advertisement content</text>
        <expiration_date>2025-12-31</expiration_date>
    </record>
</records>"""
                }
            },
            "record_types": {
                "news": {
                    "required_elements": ["text", "city"],
                    "description": "News record with text and city information"
                },
                "private_ad": {
                    "required_elements": ["text", "expiration_date"],
                    "description": "Private advertisement with expiration date (YYYY-MM-DD format)"
                },
                "weather_alert": {
                    "required_elements": ["text", "severity", "location"],
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
            Path object for the XML file to process
        """
        if user_provided_path:
            # Use user-provided file path
            file_path = Path(user_provided_path)
            if not file_path.exists():
                raise FileNotFoundError(f"User-provided file not found: {file_path}")
        else:
            # Look for XML files in default folder
            xml_files = list(self.default_folder.glob("*.xml"))
            if not xml_files:
                raise FileNotFoundError(f"No XML files found in default folder: {self.default_folder}")

            # If multiple files, let user choose or take the first one
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

    def load_xml_file(self, file_path: Path) -> ET.Element:
        """
        Load and parse XML file content.

        Args:
            file_path: Path to the XML file

        Returns:
            Parsed XML root element
        """
        try:
            # Parse XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            print(f"Successfully loaded XML file: {file_path.name}")
            return root

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format in file {file_path.name}: {e}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path.name}: {e}")

    def validate_record_element(self, record_element: ET.Element) -> None:
        """
        Validate XML record element against required structure.

        Args:
            record_element: XML element representing a record
        """
        # Check if record has type attribute
        record_type = record_element.get('type', '').lower()
        if not record_type:
            raise ValueError("Record element must have 'type' attribute")

        # Check if record type is supported
        if record_type not in self.record_type_mapping:
            raise ValueError(f"Unsupported record type: {record_type}")

        # Define required elements for each record type
        required_elements = {
            'news': ['text', 'city'],
            'private_ad': ['text', 'expiration_date'],
            'weather_alert': ['text', 'severity', 'location']
        }

        # Validate required elements are present
        missing_elements = []
        for elem_name in required_elements[record_type]:
            elem = record_element.find(elem_name)
            if elem is None or not elem.text or not elem.text.strip():
                missing_elements.append(elem_name)

        if missing_elements:
            raise ValueError(f"Missing required elements for {record_type}: {missing_elements}")

    def parse_xml_records(self, root: ET.Element) -> List[FeedRecord]:
        """
        Parse XML data and create record objects.

        Args:
            root: Root XML element

        Returns:
            List of created FeedRecord objects
        """
        records = []

        # Check if XML contains single record or multiple records
        if root.tag == 'records':
            # Multiple records format
            record_elements = root.findall('record')
            print(f"Processing multiple records format with {len(record_elements)} records")

            for i, record_element in enumerate(record_elements, 1):
                try:
                    # Validate record element
                    self.validate_record_element(record_element)

                    # Extract record type
                    record_type = record_element.get('type', '').lower()

                    # Create record object
                    record_class = self.record_type_mapping[record_type]
                    record = record_class.from_xml_element(record_element)
                    records.append(record)

                    print(f"  ✓ Record {i}: {record_type} processed successfully")

                except Exception as e:
                    print(f"  ✗ Error processing record {i}: {e}")
                    continue

        elif root.tag == 'record':
            # Single record format
            print("Processing single record format")

            try:
                # Validate record element
                self.validate_record_element(root)

                # Extract record type
                record_type = root.get('type', '').lower()

                # Create record object
                record_class = self.record_type_mapping[record_type]
                record = record_class.from_xml_element(root)
                records.append(record)

                print(f"  ✓ {record_type} record processed successfully")

            except Exception as e:
                print(f"  ✗ Error processing record: {e}")

        else:
            raise ValueError("Invalid XML format. Expected root element 'records' or 'record'")

        return records

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
            file_path = self.get_file_path(user_provided_path)

            # Load XML file content
            root = self.load_xml_file(file_path)

            # Parse records from XML data
            records = self.parse_xml_records(root)

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

    def create_sample_xml_files(self) -> None:
        """
        Create sample XML files in the default folder for testing.
        """
        # Sample single record XML
        single_record_xml = """<?xml version="1.0" encoding="UTF-8"?>
<record type="news">
    <text>Sample news content from XML file</text>
    <city>Sample City</city>
</record>"""

        # Sample multiple records XML
        multiple_records_xml = """<?xml version="1.0" encoding="UTF-8"?>
<records>
    <record type="news">
        <text>First news from XML batch processing</text>
        <city>New York</city>
    </record>
    <record type="private_ad">
        <text>XML-based advertisement content</text>
        <expiration_date>2025-12-31</expiration_date>
    </record>
    <record type="weather_alert">
        <text>Severe weather warning from XML processing</text>
        <severity>High</severity>
        <location>Downtown Area</location>
    </record>
</records>"""

        # Write sample files
        single_file_path = self.default_folder / "sample_single_record.xml"
        multiple_file_path = self.default_folder / "sample_multiple_records.xml"

        try:
            # Write single record sample
            with open(single_file_path, 'w', encoding='utf-8') as file:
                file.write(single_record_xml)

            # Write multiple records sample
            with open(multiple_file_path, 'w', encoding='utf-8') as file:
                file.write(multiple_records_xml)

            print(f"Sample XML files created in {self.default_folder}:")
            print(f"  - {single_file_path.name} (single record)")
            print(f"  - {multiple_file_path.name} (multiple records)")

        except Exception as e:
            print(f"Error creating sample files: {e}")


# =============================================================================
# ENHANCED NEWS FEED MANAGER WITH JSON AND XML PROCESSING
# =============================================================================

class EnhancedNewsFeedManager:
    """
    Enhanced news feed manager with JSON and XML file processing capabilities.
    Extends the original functionality with both JSON and XML import features.
    """

    def __init__(self, output_file: str = "news_feed.txt", json_folder: str = "json_input",
                 xml_folder: str = "xml_input"):
        """
        Initialize enhanced news feed manager.

        Args:
            output_file: Output file for news feed
            json_folder: Default folder for JSON input files
            xml_folder: Default folder for XML input files
        """
        # Initialize output file for news feed
        self.output_file = output_file

        # Initialize JSON and XML file processors
        self.json_processor = JSONFileProcessor(json_folder)
        self.xml_processor = XMLFileProcessor(xml_folder)

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
        print("4. Back to main menu")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '4':
            return
        elif choice == '3':
            # Create sample JSON files
            self.json_processor.create_sample_json_files()
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

        self._process_file_records(self.json_processor.process_json_file(file_path), self.json_processor)

    def publish_from_xml(self) -> None:
        """
        Handle XML file processing and publication of records.
        """
        print("\n" + "=" * 50)
        print("XML FILE PROCESSING")
        print("=" * 50)

        print("Choose XML file source:")
        print("1. Use default folder (xml_input)")
        print("2. Specify custom file path")
        print("3. Create sample XML files")
        print("4. Show XML format specification")
        print("5. Back to main menu")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '5':
            return
        elif choice == '3':
            # Create sample XML files
            self.xml_processor.create_sample_xml_files()
            return
        elif choice == '4':
            # Show format specification
            format_spec = self.xml_processor.define_input_format()
            print("\nXML Format Specification:")
            print(json.dumps(format_spec, indent=2))
            return
        elif choice == '1':
            # Process from default folder
            file_path = None
        elif choice == '2':
            # Get custom file path from user
            file_path = input("Enter full path to XML file: ").strip()
            if not file_path:
                print("File path cannot be empty!")
                return
        else:
            print("Invalid choice. Please try again.")
            return

        self._process_file_records(self.xml_processor.process_xml_file(file_path), self.xml_processor)

    def _process_file_records(self, records: List[FeedRecord], processor) -> None:
        """
        Common method to process and publish records from any file type.

        Args:
            records: List of FeedRecord objects
            processor: File processor instance (JSON or XML)
        """
        try:
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
                cleanup_choice = input("\nRemove processed file? (y/n): ").strip().lower()
                if cleanup_choice == 'y':
                    processor.cleanup_processed_files()
            else:
                print("No records to publish.")

        except Exception as e:
            print(f"Error processing file records: {e}")

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

    def show_format_help(self) -> None:
        """
        Display format help for both JSON and XML files.
        """
        print("\n" + "=" * 60)
        print("FILE FORMAT SPECIFICATIONS")
        print("=" * 60)

        print("\n--- JSON FORMAT ---")
        json_format = self.json_processor.define_input_format()
        print(json.dumps(json_format, indent=2))

        print("\n--- XML FORMAT ---")
        xml_format = self.xml_processor.define_input_format()
        print(json.dumps(xml_format, indent=2))

    def run(self) -> None:
        """
        Main application loop with enhanced menu including JSON and XML processing.
        """
        print("=" * 60)
        print("ENHANCED NEWS FEED SYSTEM WITH JSON & XML PROCESSING")
        print("=" * 60)
        print("Welcome to the enhanced news feed management system!")
        print("This system supports JSON and XML file processing for batch record imports.")

        while True:
            print("\n" + "=" * 50)
            print("MAIN MENU")
            print("=" * 50)
            print("1. Create record manually")
            print("2. Import records from JSON file")
            print("3. Import records from XML file")
            print("4. View current news feed")
            print("5. Clear news feed")
            print("6. Show file format help")
            print("7. Exit")

            choice = input("Enter your choice (1-7): ").strip()

            if choice == '1':
                self.publish_manual_record()
            elif choice == '2':
                self.publish_from_json()
            elif choice == '3':
                self.publish_from_xml()
            elif choice == '4':
                self.view_news_feed()
            elif choice == '5':
                self.clear_news_feed()
            elif choice == '6':
                self.show_format_help()
            elif choice == '7':
                print("Thank you for using the Enhanced News Feed System!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 7.")


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