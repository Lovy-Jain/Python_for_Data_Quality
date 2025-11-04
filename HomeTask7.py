"""
Module 2, 3 & 4 Homeworks - Refactored with Functional Approach
===============================================================
This module contains refactored solutions for:
- Homework 2: Random dictionaries generation and merging
- Homework 3: Text processing with normalization and analysis
- Homework 4: User-generated news feed system
"""

import re
import random
import string
import os
import csv
from collections import Counter
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


# =============================================================================
# HOMEWORK 1: Random Numbers List Processing
# =============================================================================

def generate_random_numbers_list(count: int = 100, min_val: int = 0, max_val: int = 1000) -> List[int]:
    """
    Generate a list of random numbers within specified range.

    Args:
        count: Number of random numbers to generate
        min_val: Minimum value for random numbers
        max_val: Maximum value for random numbers

    Returns:
        List of random integers
    """
    # Create empty list to store random numbers
    numbers_list = []

    # Generate specified count of random numbers
    for i in range(count):
        # Generate random number between min_val and max_val (inclusive)
        random_number = random.randint(min_val, max_val)
        # Add random number to the list
        numbers_list.append(random_number)

    return numbers_list


def bubble_sort_manual(numbers: List[int]) -> List[int]:
    """
    Sort list from min to max using bubble sort algorithm (without using sort()).

    Args:
        numbers: List of integers to sort

    Returns:
        Sorted list of integers (min to max)
    """
    # Create a copy of the list to avoid modifying the original
    sorted_numbers = numbers.copy()
    # Get the length of the list
    n = len(sorted_numbers)

    # Bubble sort algorithm implementation
    for i in range(n):
        # Flag to optimize - if no swaps occur, list is already sorted
        swapped = False

        # Last i elements are already in place, so we don't need to check them
        for j in range(0, n - i - 1):
            # Compare adjacent elements
            if sorted_numbers[j] > sorted_numbers[j + 1]:
                # Swap elements if they are in wrong order (larger before smaller)
                sorted_numbers[j], sorted_numbers[j + 1] = sorted_numbers[j + 1], sorted_numbers[j]
                # Set flag to indicate a swap occurred
                swapped = True

        # If no swapping occurred, the list is already sorted
        if not swapped:
            break

    return sorted_numbers


def separate_even_odd_numbers(numbers: List[int]) -> Tuple[List[int], List[int]]:
    """
    Separate numbers into even and odd lists.

    Args:
        numbers: List of integers to separate

    Returns:
        Tuple containing (even_numbers, odd_numbers)
    """
    # Initialize empty lists for even and odd numbers
    even_numbers = []
    odd_numbers = []

    # Iterate through each number in the list
    for number in numbers:
        # Check if number is even (divisible by 2 with no remainder)
        if number % 2 == 0:
            # Add to even numbers list
            even_numbers.append(number)
        else:
            # Add to odd numbers list
            odd_numbers.append(number)

    return even_numbers, odd_numbers


def calculate_average(numbers: List[int]) -> float:
    """
    Calculate the average of a list of numbers.

    Args:
        numbers: List of integers to calculate average for

    Returns:
        Average as float, or 0.0 if list is empty
    """
    # Check if list is empty to avoid division by zero
    if not numbers:
        return 0.0

    # Calculate sum of all numbers in the list
    total_sum = sum(numbers)
    # Calculate average by dividing sum by count of numbers
    average = total_sum / len(numbers)

    return average


def homework_1():
    """Execute Homework 1: Random numbers list processing with manual sorting."""
    print("=" * 60)
    print("HOMEWORK 1: Random Numbers List Processing")
    print("=" * 60)

    # Step 1: Create list of 100 random numbers from 0 to 1000
    print("Step 1: Generating list of 100 random numbers (0-1000)...")
    random_numbers = generate_random_numbers_list(100, 0, 1000)
    print(f"Generated {len(random_numbers)} random numbers")
    print(f"First 10 numbers: {random_numbers[:10]}")
    print(f"Last 10 numbers: {random_numbers[-10:]}")

    # Step 2: Sort list from min to max without using sort()
    print("\nStep 2: Sorting numbers from min to max (using bubble sort)...")
    sorted_numbers = bubble_sort_manual(random_numbers)
    print(f"Sorting completed!")
    print(f"Smallest 10 numbers: {sorted_numbers[:10]}")
    print(f"Largest 10 numbers: {sorted_numbers[-10:]}")

    # Step 3: Separate even and odd numbers
    print("\nStep 3: Separating even and odd numbers...")
    even_numbers, odd_numbers = separate_even_odd_numbers(sorted_numbers)
    print(f"Found {len(even_numbers)} even numbers")
    print(f"Found {len(odd_numbers)} odd numbers")

    # Step 4: Calculate averages for even and odd numbers
    print("\nStep 4: Calculating averages...")
    even_average = calculate_average(even_numbers)
    odd_average = calculate_average(odd_numbers)

    # Step 5: Print both average results in console
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    print(f"Average of even numbers: {even_average:.2f}")
    print(f"Average of odd numbers: {odd_average:.2f}")
    print(f"Total numbers processed: {len(sorted_numbers)}")
    print(f"Even numbers count: {len(even_numbers)}")
    print(f"Odd numbers count: {len(odd_numbers)}")

    return {
        'original_numbers': random_numbers,
        'sorted_numbers': sorted_numbers,
        'even_numbers': even_numbers,
        'odd_numbers': odd_numbers,
        'even_average': even_average,
        'odd_average': odd_average
    }


# =============================================================================
# HOMEWORK 2: Random Dictionaries Generation and Merging
# =============================================================================

def generate_random_dict(min_keys: int = 2, max_keys: int = 8) -> Dict[str, int]:
    """
    Generate a single dictionary with random letter keys and numeric values.

    Args:
        min_keys: Minimum number of keys in the dictionary
        max_keys: Maximum number of keys in the dictionary

    Returns:
        Dictionary with random letter keys and values 0-100
    """
    # Determine random number of keys for this dictionary
    num_keys = random.randint(min_keys, max_keys)

    # Select random letters as keys (ensure uniqueness)
    available_letters = list(string.ascii_lowercase)
    selected_keys = random.sample(available_letters, num_keys)

    # Create dictionary with random values 0-100
    return {key: random.randint(0, 100) for key in selected_keys}


def generate_list_of_dicts(min_dicts: int = 2, max_dicts: int = 10) -> List[Dict[str, int]]:
    """
    Generate a list containing random number of dictionaries.

    Args:
        min_dicts: Minimum number of dictionaries to generate
        max_dicts: Maximum number of dictionaries to generate

    Returns:
        List of dictionaries with random letter keys and numeric values
    """
    # Determine random number of dictionaries to create
    num_dicts = random.randint(min_dicts, max_dicts)

    # Generate list of random dictionaries
    return [generate_random_dict() for _ in range(num_dicts)]


def find_key_max_value_and_dict_index(dicts_list: List[Dict[str, int]], key: str) -> Tuple[int, int]:
    """
    Find the maximum value for a given key across all dictionaries and its dictionary index.

    Args:
        dicts_list: List of dictionaries to search through
        key: The key to search for

    Returns:
        Tuple of (max_value, dict_index) where dict_index is 0-based
    """
    max_value = -1
    max_dict_index = -1

    # Iterate through all dictionaries to find maximum value for the key
    for dict_index, current_dict in enumerate(dicts_list):
        if key in current_dict and current_dict[key] > max_value:
            max_value = current_dict[key]
            max_dict_index = dict_index

    return max_value, max_dict_index


def create_merged_dict(dicts_list: List[Dict[str, int]]) -> Dict[str, int]:
    """
    Merge list of dictionaries according to specific rules:
    - If key appears in multiple dicts: take max value and append dict number
    - If key appears in only one dict: take as is

    Args:
        dicts_list: List of dictionaries to merge

    Returns:
        Single merged dictionary following the specified rules
    """
    # Collect all unique keys from all dictionaries
    all_keys = set()
    for dictionary in dicts_list:
        all_keys.update(dictionary.keys())

    merged_dict = {}

    # Process each unique key
    for key in all_keys:
        # Count how many dictionaries contain this key
        dicts_with_key = [i for i, d in enumerate(dicts_list) if key in d]

        if len(dicts_with_key) == 1:
            # Key exists in only one dictionary - take as is
            dict_index = dicts_with_key[0]
            merged_dict[key] = dicts_list[dict_index][key]
        else:
            # Key exists in multiple dictionaries - find max value and rename key
            max_value, max_dict_index = find_key_max_value_and_dict_index(dicts_list, key)
            # Create new key name with dict number (1-based indexing for display)
            new_key = f"{key}_{max_dict_index + 1}"
            merged_dict[new_key] = max_value

    return merged_dict


def homework_2():
    """Execute Homework 2: Random dictionaries generation and merging."""
    print("=" * 60)
    print("HOMEWORK 2: Random Dictionaries Generation and Merging")
    print("=" * 60)

    # Step 1: Generate list of random dictionaries
    print("Step 1: Generating random list of dictionaries...")
    random_dicts = generate_list_of_dicts()

    print(f"Generated {len(random_dicts)} dictionaries:")
    for i, dictionary in enumerate(random_dicts, 1):
        print(f"  Dict {i}: {dictionary}")

    # Step 2: Merge dictionaries according to rules
    print("\nStep 2: Merging dictionaries with conflict resolution...")
    merged_result = create_merged_dict(random_dicts)

    print(f"Merged dictionary: {merged_result}")
    print(f"Total keys in merged dict: {len(merged_result)}")


# =============================================================================
# HOMEWORK 3: Text Processing with Normalization and Analysis
# =============================================================================

def get_homework_text() -> str:
    """
    Return the homework text as a string variable.

    Returns:
        The original homework text with mixed cases and intentional errors
    """
    return """tHis iz your homeWork, copy these Text to variable.



  You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.



  it iZ misspeLLing here. fix"iZ" with correct "is", but ONLY when it Iz a mistAKE.



  last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""


def normalize_text_case(text: str) -> str:
    """
    Normalize text to proper sentence case (first letter capitalized, rest lowercase).

    Args:
        text: Input text with mixed cases

    Returns:
        Text with normalized case (proper sentence case)
    """
    # Split text into sentences using punctuation as delimiters
    sentences = re.split(r'([.!?]+)', text)
    normalized_parts = []

    # Process each part (alternating between sentence content and punctuation)
    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            if sentence:
                # Apply proper sentence case: first letter upper, rest lower
                normalized_sentence = sentence[0].upper() + sentence[1:].lower()
                normalized_parts.append(normalized_sentence)

                # Add back the punctuation if it exists
                if i + 1 < len(sentences):
                    normalized_parts.append(sentences[i + 1])

    return ''.join(normalized_parts)


def fix_iz_spelling_errors(text: str) -> str:
    """
    Fix "iz" spelling mistakes by replacing with "is" only when it's standalone.

    Args:
        text: Input text containing potential "iz" spelling errors

    Returns:
        Text with "iz" replaced by "is" only when it's a standalone word
    """
    # Use word boundaries to replace only standalone "iz" words, case-insensitive
    return re.sub(r'\biz\b', 'is', text, flags=re.IGNORECASE)


def extract_last_words_from_sentences(text: str) -> List[str]:
    """
    Extract the last word from each sentence in the text.

    Args:
        text: Input text containing multiple sentences

    Returns:
        List of last words from each sentence
    """
    # Split text into sentences using common sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    last_words = []

    # Extract last word from each non-empty sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            words = sentence.split()
            if words:
                last_words.append(words[-1])

    return last_words


def append_last_words_sentence(text: str) -> str:
    """
    Create a new sentence from last words of existing sentences and append to text.

    Args:
        text: Input text to process

    Returns:
        Text with new sentence appended containing last words
    """
    # Get last words from all sentences
    last_words = extract_last_words_from_sentences(text)

    if last_words:
        # Create new sentence from last words and append to original text
        new_sentence = " ".join(last_words) + "."
        return text + " " + new_sentence

    return text


def count_all_whitespace_characters(text: str) -> int:
    """
    Count all whitespace characters in text (spaces, newlines, tabs, etc.).

    Args:
        text: Input text to analyze

    Returns:
        Total count of whitespace characters
    """
    # Count all characters that are considered whitespace
    return sum(1 for char in text if char.isspace())


def analyze_whitespace_breakdown(text: str) -> Dict[str, int]:
    """
    Provide detailed breakdown of different types of whitespace characters.

    Args:
        text: Input text to analyze

    Returns:
        Dictionary with counts of different whitespace types
    """
    # Count different types of whitespace characters
    breakdown = {
        'spaces': text.count(' '),
        'newlines': text.count('\n'),
        'tabs': text.count('\t'),
        'carriage_returns': text.count('\r')
    }

    # Calculate other whitespace types
    total_whitespace = count_all_whitespace_characters(text)
    breakdown['other'] = total_whitespace - sum(breakdown.values())
    breakdown['total'] = total_whitespace

    return breakdown


def process_homework_text(text: str) -> str:
    """
    Apply all text processing steps in sequence.

    Args:
        text: Original homework text

    Returns:
        Fully processed text after all transformations
    """
    # Apply all processing steps in the required order
    step1_normalized = normalize_text_case(text)
    step2_fixed_spelling = fix_iz_spelling_errors(step1_normalized)
    step3_final = append_last_words_sentence(step2_fixed_spelling)

    return step3_final


def homework_3():
    """Execute Homework 3: Text processing with normalization and analysis."""
    print("=" * 60)
    print("HOMEWORK 3: Text Processing with Normalization and Analysis")
    print("=" * 60)

    # Step 1: Get the original homework text
    print("Step 1: Loading homework text into variable...")
    original_text = get_homework_text()
    print(f"Original text loaded. Length: {len(original_text)} characters")
    print(f"Original whitespace count: {count_all_whitespace_characters(original_text)}")

    # Step 2: Apply all text processing transformations
    print("\nStep 2: Processing text through all transformation steps...")

    # Show intermediate steps
    normalized_text = normalize_text_case(original_text)
    print("✓ Case normalization completed")

    spelling_fixed_text = fix_iz_spelling_errors(normalized_text)
    print("✓ Spelling corrections applied")

    final_text = append_last_words_sentence(spelling_fixed_text)
    print("✓ Last words sentence appended")

    # Step 3: Analyze final results
    print("\nStep 3: Final text analysis...")
    whitespace_analysis = analyze_whitespace_breakdown(final_text)

    print(f"Final text length: {len(final_text)} characters")
    print("Whitespace breakdown:")
    for ws_type, count in whitespace_analysis.items():
        print(f"  {ws_type.capitalize()}: {count}")

    print("\n" + "=" * 60)
    print("FINAL PROCESSED TEXT:")
    print("=" * 60)
    print(final_text)

    return final_text


# =============================================================================
# HOMEWORK 4: User-Generated News Feed System
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


class NewsRecord(FeedRecord):
    """
    News record type with text, city, and auto-calculated date.
    """

    def __init__(self, text: str):
        """
        Initialize news record with text content.

        Args:
            text: The news text content
        """
        super().__init__(text)
        self.city = ""

    def get_user_input(self) -> None:
        """
        Get city input from user for news record.
        """
        self.city = input("Enter city where news happened: ").strip()
        while not self.city:
            print("City cannot be empty!")
            self.city = input("Enter city where news happened: ").strip()

    def format_for_publication(self) -> str:
        """
        Format news record for publication with special news format.

        Returns:
            Formatted string with news header, content, city and date
        """
        # Calculate publication date (current date)
        pub_date = self.timestamp.strftime("%d/%m/%Y")

        # Create formatted news entry
        separator = "-" * 50
        header = "NEWS"
        content_lines = [
            separator,
            header,
            separator,
            self.text,
            f"City: {self.city}",
            f"Date: {pub_date}",
            separator,
            ""  # Empty line for separation
        ]

        return "\n".join(content_lines)

    def get_record_type_name(self) -> str:
        """Return display name for news records."""
        return "News"


class PrivateAdRecord(FeedRecord):
    """
    Private advertisement record with text, expiration date, and calculated days left.
    """

    def __init__(self, text: str):
        """
        Initialize private ad record with text content.

        Args:
            text: The advertisement text content
        """
        super().__init__(text)
        self.expiration_date = None

    def get_user_input(self) -> None:
        """
        Get expiration date input from user for private ad.
        """
        while True:
            try:
                date_input = input("Enter expiration date (DD/MM/YYYY): ").strip()
                self.expiration_date = datetime.strptime(date_input, "%d/%m/%Y")

                # Validate that expiration date is in the future
                if self.expiration_date.date() <= datetime.now().date():
                    print("Expiration date must be in the future!")
                    continue
                break

            except ValueError:
                print("Invalid date format! Please use DD/MM/YYYY format.")

    def calculate_days_left(self) -> int:
        """
        Calculate number of days left until expiration.

        Returns:
            Number of days remaining until expiration
        """
        today = datetime.now().date()
        expiry = self.expiration_date.date()
        return (expiry - today).days

    def format_for_publication(self) -> str:
        """
        Format private ad record for publication with days left calculation.

        Returns:
            Formatted string with ad header, content, expiration and days left
        """
        days_left = self.calculate_days_left()
        exp_date = self.expiration_date.strftime("%d/%m/%Y")

        # Create formatted private ad entry
        separator = "-" * 50
        header = "PRIVATE AD"
        content_lines = [
            separator,
            header,
            separator,
            self.text,
            f"Expires: {exp_date}",
            f"Days left: {days_left}",
            separator,
            ""  # Empty line for separation
        ]

        return "\n".join(content_lines)

    def get_record_type_name(self) -> str:
        """Return display name for private ad records."""
        return "Private Advertisement"


class WeatherAlertRecord(FeedRecord):
    """
    Custom weather alert record with severity level and auto-calculated urgency status.
    This is the unique record type with special publishing rules.
    """

    SEVERITY_LEVELS = {
        1: "Low",
        2: "Moderate",
        3: "High",
        4: "Severe",
        5: "Extreme"
    }

    def __init__(self, text: str):
        """
        Initialize weather alert record with text content.

        Args:
            text: The weather alert text content
        """
        super().__init__(text)
        self.severity_level = 1
        self.affected_areas = []

    def get_user_input(self) -> None:
        """
        Get severity level and affected areas from user for weather alert.
        """
        # Get severity level
        while True:
            try:
                print("\nSeverity levels:")
                for level, name in self.SEVERITY_LEVELS.items():
                    print(f"  {level} - {name}")

                severity_input = input("Enter severity level (1-5): ").strip()
                self.severity_level = int(severity_input)

                if self.severity_level not in self.SEVERITY_LEVELS:
                    print("Please enter a number between 1 and 5!")
                    continue
                break

            except ValueError:
                print("Please enter a valid number!")

        # Get affected areas
        areas_input = input("Enter affected areas (comma-separated): ").strip()
        self.affected_areas = [area.strip() for area in areas_input.split(",") if area.strip()]

        if not self.affected_areas:
            self.affected_areas = ["General area"]

    def calculate_urgency_status(self) -> str:
        """
        Calculate urgency status based on severity level and time since creation.
        This is the unique publishing rule for weather alerts.

        Returns:
            Urgency status string
        """
        # Time-sensitive urgency calculation
        time_elapsed = datetime.now() - self.timestamp
        hours_elapsed = time_elapsed.total_seconds() / 3600

        # Urgency decreases over time, but severity affects the rate
        if self.severity_level >= 4:  # Severe/Extreme
            if hours_elapsed < 2:
                return "IMMEDIATE ACTION REQUIRED"
            elif hours_elapsed < 6:
                return "URGENT"
            else:
                return "MONITOR CLOSELY"
        elif self.severity_level == 3:  # High
            if hours_elapsed < 4:
                return "URGENT"
            elif hours_elapsed < 12:
                return "IMPORTANT"
            else:
                return "ADVISORY"
        else:  # Low/Moderate
            if hours_elapsed < 8:
                return "ADVISORY"
            else:
                return "INFORMATIONAL"

    def format_for_publication(self) -> str:
        """
        Format weather alert record with unique publishing rules.
        Includes severity, urgency status, and affected areas.

        Returns:
            Formatted string with weather alert header and special formatting
        """
        severity_name = self.SEVERITY_LEVELS[self.severity_level]
        urgency = self.calculate_urgency_status()
        issue_time = self.timestamp.strftime("%d/%m/%Y %H:%M")
        areas = ", ".join(self.affected_areas)

        # Special formatting based on severity level
        if self.severity_level >= 4:
            separator = "=" * 50
            header = f"🚨 WEATHER ALERT - {severity_name.upper()} 🚨"
        elif self.severity_level == 3:
            separator = "*" * 50
            header = f"⚠️ WEATHER ALERT - {severity_name.upper()} ⚠️"
        else:
            separator = "-" * 50
            header = f"🌤️ Weather Alert - {severity_name}"

        content_lines = [
            separator,
            header,
            separator,
            f"URGENCY: {urgency}",
            f"SEVERITY: {severity_name.upper()} (Level {self.severity_level}/5)",
            "",
            self.text,
            "",
            f"Affected Areas: {areas}",
            f"Issued: {issue_time}",
            separator,
            ""  # Empty line for separation
        ]

        return "\n".join(content_lines)

    def get_record_type_name(self) -> str:
        """Return display name for weather alert records."""
        return "Weather Alert"


class NewsFeedManager:
    """
    Main manager class for the news feed system.
    Handles user interaction, record creation, and file operations.
    """

    def __init__(self, feed_file: str = "news_feed.txt"):
        """
        Initialize news feed manager with specified output file.

        Args:
            feed_file: Path to the news feed output file
        """
        self.feed_file = feed_file
        self.record_types = {
            1: NewsRecord,
            2: PrivateAdRecord,
            3: WeatherAlertRecord
        }

    def display_menu(self) -> None:
        """
        Display the main menu with available record types.
        """
        print("\n" + "=" * 60)
        print("📰 USER-GENERATED NEWS FEED SYSTEM 📰")
        print("=" * 60)
        print("Select the type of record you want to add:")
        print("1. News (requires: text, city)")
        print("2. Private Advertisement (requires: text, expiration date)")
        print("3. Weather Alert (requires: text, severity, affected areas)")
        print("4. View current feed")
        print("5. Exit")
        print("-" * 60)

    def get_user_choice(self) -> int:
        """
        Get and validate user's menu choice.

        Returns:
            User's menu choice as integer (1-5)
        """
        while True:
            try:
                choice = input("Enter your choice (1-5): ").strip()
                choice_num = int(choice)

                if choice_num in range(1, 6):
                    return choice_num
                else:
                    print("Please enter a number between 1 and 5!")

            except ValueError:
                print("Please enter a valid number!")

    def get_record_text(self) -> str:
        """
        Get the main text content for any record type.

        Returns:
            Text content entered by user
        """
        print("\nEnter the main text content:")
        text = input("> ").strip()

        while not text:
            print("Text content cannot be empty!")
            text = input("> ").strip()

        return text

    def create_record(self, record_type: int) -> Optional[FeedRecord]:
        """
        Create a new record of the specified type with user input.

        Args:
            record_type: Integer representing the record type (1-3)

        Returns:
            Created record instance or None if creation failed
        """
        if record_type not in self.record_types:
            print("Invalid record type!")
            return None

        try:
            # Get main text content
            text = self.get_record_text()

            # Create record instance
            record_class = self.record_types[record_type]
            record = record_class(text)

            # Get additional user input specific to this record type
            print(f"\nEntering details for {record.get_record_type_name()}...")
            record.get_user_input()

            return record

        except Exception as e:
            print(f"Error creating record: {e}")
            return None

    def publish_record(self, record: FeedRecord) -> bool:
        """
        Publish a record to the news feed file.

        Args:
            record: The record to publish

        Returns:
            True if published successfully, False otherwise
        """
        try:
            # Format record for publication
            formatted_content = record.format_for_publication()

            # Append to feed file
            with open(self.feed_file, 'a', encoding='utf-8') as file:
                file.write(formatted_content)

            print(f"\n✅ {record.get_record_type_name()} published successfully!")
            return True

        except Exception as e:
            print(f"❌ Error publishing record: {e}")
            return False

    def view_feed(self) -> None:
        """
        Display the current contents of the news feed file.
        """
        try:
            if not os.path.exists(self.feed_file):
                print("\n📰 News feed is empty. No records published yet.")
                return

            with open(self.feed_file, 'r', encoding='utf-8') as file:
                content = file.read()

            if not content.strip():
                print("\n📰 News feed is empty. No records published yet.")
            else:
                print("\n" + "=" * 60)
                print("📰 CURRENT NEWS FEED 📰")
                print("=" * 60)
                print(content)

        except Exception as e:
            print(f"❌ Error reading feed file: {e}")

    def run(self) -> None:
        """
        Main loop for the news feed system.
        Handles user interaction and coordinates all operations.
        """
        print("Welcome to the User-Generated News Feed System!")

        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice in [1, 2, 3]:
                # Create and publish a new record
                record = self.create_record(choice)
                if record:
                    self.publish_record(record)

            elif choice == 4:
                # View current feed
                self.view_feed()

            elif choice == 5:
                # Exit
                print("\n👋 Thank you for using the News Feed System!")
                break

            # Wait for user to continue
            input("\nPress Enter to continue...")


def homework_4():
    """Execute Homework 4: User-generated news feed system."""
    print("=" * 60)
    print("HOMEWORK 4: User-Generated News Feed System")
    print("=" * 60)

    # Create and run the news feed manager
    feed_manager = NewsFeedManager("homework_4_news_feed.txt")
    feed_manager.run()


# =============================================================================
# HOMEWORK 5/6: News Feed Analysis and CSV Reports
# =============================================================================

def read_news_feed_file(file_path: str) -> str:
    """
    Read the entire content of the news feed file.

    Args:
        file_path: Path to the news feed file

    Returns:
        File content as string, empty string if file doesn't exist
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"News feed file '{file_path}' not found.")
            return ""

        # Read file content with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        return content

    except Exception as e:
        print(f"Error reading news feed file: {e}")
        return ""


def extract_text_content_from_feed(feed_content: str) -> str:
    """
    Extract only the text content from news feed, removing separators and headers.

    Args:
        feed_content: Raw content from news feed file

    Returns:
        Clean text content without formatting elements
    """
    if not feed_content.strip():
        return ""

    # Split content into lines
    lines = feed_content.split('\n')
    text_lines = []

    # Process each line to extract meaningful text
    for line in lines:
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Skip separator lines (dashes, equals, asterisks)
        if all(char in '-=*' for char in line):
            continue

        # Skip header lines
        if line in ['NEWS', 'PRIVATE AD'] or 'WEATHER ALERT' in line:
            continue

        # Skip metadata lines (City:, Date:, Expires:, etc.)
        if any(line.startswith(prefix) for prefix in
               ['City:', 'Date:', 'Expires:', 'Days left:', 'URGENCY:', 'SEVERITY:', 'Affected Areas:', 'Issued:']):
            continue

        # Skip emoji-only lines or lines with special formatting
        if line.startswith('🚨') or line.startswith('⚠️') or line.startswith('🌤️'):
            continue

        # Add remaining text content
        text_lines.append(line)

    # Join all text lines with spaces
    return ' '.join(text_lines)


def preprocess_text_for_word_analysis(text: str) -> List[str]:
    """
    Preprocess text for word analysis: convert to lowercase, remove punctuation, split into words.

    Args:
        text: Input text to process

    Returns:
        List of preprocessed words (lowercase, no punctuation)
    """
    if not text.strip():
        return []

    # Convert to lowercase
    text = text.lower()

    # Remove punctuation and special characters, keep only letters and spaces
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Split into words and filter out empty strings
    words = [word.strip() for word in text.split() if word.strip()]

    return words


def count_words(text: str) -> Dict[str, int]:
    """
    Count frequency of each word in the text.

    Args:
        text: Input text to analyze

    Returns:
        Dictionary with word frequencies
    """
    # Preprocess text to get clean words
    words = preprocess_text_for_word_analysis(text)

    # Count word frequencies using Counter
    word_counts = Counter(words)

    return dict(word_counts)


def count_letters(text: str) -> Dict[str, Dict[str, int]]:
    """
    Count letters with detailed statistics (total, uppercase, percentage).

    Args:
        text: Input text to analyze

    Returns:
        Dictionary with letter statistics
    """
    if not text.strip():
        return {}

    # Initialize letter statistics
    letter_stats = {}

    # Process each character in the text
    for char in text:
        # Only process alphabetic characters (skip spaces and punctuation)
        if char.isalpha():
            char_lower = char.lower()

            # Initialize letter entry if not exists
            if char_lower not in letter_stats:
                letter_stats[char_lower] = {
                    'count_all': 0,
                    'count_uppercase': 0
                }

            # Count total occurrences
            letter_stats[char_lower]['count_all'] += 1

            # Count uppercase occurrences
            if char.isupper():
                letter_stats[char_lower]['count_uppercase'] += 1

    # Calculate percentages
    for letter in letter_stats:
        total = letter_stats[letter]['count_all']
        uppercase = letter_stats[letter]['count_uppercase']

        # Calculate percentage of uppercase letters
        if total > 0:
            percentage = (uppercase / total) * 100
        else:
            percentage = 0.0

        letter_stats[letter]['percentage'] = round(percentage, 2)

    return letter_stats


def create_word_count_csv(word_counts: Dict[str, int], output_file: str = "word-count.csv") -> bool:
    """
    Create CSV file with word count statistics.

    Args:
        word_counts: Dictionary with word frequencies
        output_file: Output CSV file path

    Returns:
        True if CSV created successfully, False otherwise
    """
    try:
        # Sort words alphabetically for consistent output
        sorted_words = sorted(word_counts.items())

        # Create CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['word', 'count'])

            # Write word count data
            for word, count in sorted_words:
                writer.writerow([word, count])

        print(f"✅ Word count CSV created: {output_file}")
        print(f"   Total unique words: {len(word_counts)}")
        return True

    except Exception as e:
        print(f"❌ Error creating word count CSV: {e}")
        return False


def create_letter_count_csv(letter_stats: Dict[str, Dict[str, int]], output_file: str = "letter-count.csv") -> bool:
    """
    Create CSV file with letter statistics.

    Args:
        letter_stats: Dictionary with letter statistics
        output_file: Output CSV file path

    Returns:
        True if CSV created successfully, False otherwise
    """
    try:
        # Sort letters alphabetically for consistent output
        sorted_letters = sorted(letter_stats.items())

        # Create CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['letter', 'count_all', 'count_uppercase', 'percentage'])

            # Write letter statistics data
            for letter, stats in sorted_letters:
                writer.writerow([
                    letter,
                    stats['count_all'],
                    stats['count_uppercase'],
                    stats['percentage']
                ])

        print(f"✅ Letter count CSV created: {output_file}")
        print(f"   Total unique letters: {len(letter_stats)}")
        return True

    except Exception as e:
        print(f"❌ Error creating letter count CSV: {e}")
        return False


def analyze_news_feed_and_create_csvs(feed_file: str = "homework_4_news_feed.txt") -> bool:
    """
    Analyze news feed file and create both CSV reports.

    Args:
        feed_file: Path to the news feed file to analyze

    Returns:
        True if analysis and CSV creation successful, False otherwise
    """
    print("\n" + "=" * 60)
    print("📊 NEWS FEED ANALYSIS & CSV GENERATION")
    print("=" * 60)

    # Step 1: Read news feed file
    print("Step 1: Reading news feed file...")
    feed_content = read_news_feed_file(feed_file)

    if not feed_content.strip():
        print("⚠️ No content found in news feed file. No analysis performed.")
        return False

    # Step 2: Extract clean text content
    print("Step 2: Extracting text content from feed...")
    clean_text = extract_text_content_from_feed(feed_content)

    if not clean_text.strip():
        print("⚠️ No text content extracted from feed. No analysis performed.")
        return False

    print(f"   Extracted text length: {len(clean_text)} characters")

    # Step 3: Analyze words
    print("Step 3: Analyzing word frequencies...")
    word_counts = count_words(clean_text)
    print(f"   Found {len(word_counts)} unique words")

    # Step 4: Analyze letters
    print("Step 4: Analyzing letter statistics...")
    letter_stats = count_letters(clean_text)
    print(f"   Found {len(letter_stats)} unique letters")

    # Step 5: Create CSV files
    print("Step 5: Creating CSV reports...")
    word_csv_success = create_word_count_csv(word_counts)
    letter_csv_success = create_letter_count_csv(letter_stats)

    # Summary
    if word_csv_success and letter_csv_success:
        print("\n✅ Analysis completed successfully!")
        print("📄 Generated files:")
        print("   - word-count.csv")
        print("   - letter-count.csv")
        return True
    else:
        print("\n❌ Some errors occurred during analysis.")
        return False


def homework_5_6():
    """Execute Homework 5/6: News feed analysis and CSV generation."""
    print("=" * 60)
    print("HOMEWORK 5/6: News Feed Analysis and CSV Reports")
    print("=" * 60)

    # Analyze the news feed and create CSV reports
    success = analyze_news_feed_and_create_csvs("homework_4_news_feed.txt")

    if success:
        print("\n" + "=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)

        # Display sample data from CSV files
        try:
            print("\n📄 Sample from word-count.csv (first 10 rows):")
            with open("word-count.csv", 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i < 11:  # Header + 10 data rows
                        print(f"   {', '.join(row)}")
                    else:
                        break
        except Exception as e:
            print(f"   Error reading word-count.csv: {e}")

        try:
            print("\n📄 Sample from letter-count.csv (first 10 rows):")
            with open("letter-count.csv", 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i < 11:  # Header + 10 data rows
                        print(f"   {', '.join(row)}")
                    else:
                        break
        except Exception as e:
            print(f"   Error reading letter-count.csv: {e}")


# =============================================================================
# ENHANCED NEWS FEED MANAGER WITH AUTO CSV GENERATION
# =============================================================================

class EnhancedNewsFeedManager(NewsFeedManager):
    """
    Enhanced news feed manager that automatically generates CSV reports after each record.
    """

    def publish_record(self, record: FeedRecord) -> bool:
        """
        Publish a record and automatically generate CSV reports.

        Args:
            record: The record to publish

        Returns:
            True if published successfully, False otherwise
        """
        # Call parent method to publish record
        success = super().publish_record(record)

        if success:
            # Automatically generate CSV reports after publishing
            print("\n📊 Generating updated CSV reports...")
            analyze_news_feed_and_create_csvs(self.feed_file)

        return success


def homework_4_enhanced():
    """Execute enhanced Homework 4 with automatic CSV generation."""
    print("=" * 60)
    print("HOMEWORK 4 ENHANCED: News Feed with Auto CSV Reports")
    print("=" * 60)

    # Create and run the enhanced news feed manager
    feed_manager = EnhancedNewsFeedManager("homework_4_news_feed.txt")
    feed_manager.run()


# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

def main():
    """
    Main function to execute all homework assignments.
    Demonstrates functional programming approach with clear decomposition.
    """
    print("EPAM Python Training - All Homeworks")
    print("=" * 80)
    print("Functional Programming Approach with Proper Decomposition")
    print("=" * 80)

    while True:
        print("\nSelect which homework to run:")
        print("1. Homework 1: Random Numbers List Processing")
        print("2. Homework 2: Random Dictionaries Generation and Merging")
        print("3. Homework 3: Text Processing and Analysis")
        print("4. Homework 4: User-Generated News Feed System")
        print("5. Homework 5/6: News Feed Analysis & CSV Reports")
        print("6. Homework 4 Enhanced: News Feed with Auto CSV Generation")
        print("7. Run All Homeworks (1, 2 & 3)")
        print("8. Exit")

        try:
            choice = int(input("\nEnter your choice (1-8): "))

            if choice == 1:
                # Set random seed for reproducible results
                random.seed(42)
                homework_1()

            elif choice == 2:
                # Set random seed for reproducible results in homework 2
                random.seed(42)
                homework_2()

            elif choice == 3:
                homework_3()

            elif choice == 4:
                homework_4()

            elif choice == 5:
                homework_5_6()

            elif choice == 6:
                homework_4_enhanced()

            elif choice == 7:
                # Set random seed for reproducible results
                random.seed(42)
                homework_1()
                print("\n" * 2)
                homework_2()
                print("\n" * 2)
                homework_3()

            elif choice == 8:
                print("\n👋 Goodbye!")
                break

            else:
                print("Please enter a number between 1 and 8!")

        except ValueError:
            print("Please enter a valid number!")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break

        if choice != 8:
            input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    main()