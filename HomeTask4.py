"""
Module 2 & 3 Homeworks - Refactored with Functional Approach
===========================================================
This module contains refactored solutions for:
- Homework 2: Random dictionaries generation and merging
- Homework 3: Text processing with normalization and analysis
"""

import re
import random
import string
from typing import List, Dict, Tuple


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
# MAIN EXECUTION FUNCTION
# =============================================================================

def main():
    """
    Main function to execute all homework assignments.
    Demonstrates functional programming approach with clear decomposition.
    """
    print("EPAM Python Training - Module 2 & 3 Homeworks")
    print("=" * 80)
    print("Functional Programming Approach with Proper Decomposition")
    print("=" * 80)

    # Set random seed for reproducible results in homework 2
    random.seed(42)

    # Execute Homework 2
    homework_2()
    print("\n" * 2)

    # Execute Homework 3
    homework_3()



if __name__ == "__main__":
    main()