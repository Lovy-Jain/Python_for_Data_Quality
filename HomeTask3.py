import re

# Step 1: Copy the text to a variable
original_text = """
  tHis iz your homeWork, copy these Text to variable.



  You NEED TO normalize it fROM letter CASEs point oF View. also, create one MORE senTENCE witH LAST WoRDS of each existING SENtence and add it to the END OF this Paragraph.



  it iZ misspeLLing here. fix"iZ" with correct "is", but ONLY when it Iz a mistAKE.



  last iz TO calculate nuMber OF Whitespace characteRS in this Tex. caREFULL, not only Spaces, but ALL whitespaces. I got 87."""

print("Original text:")
print(repr(original_text))
print("\n" + "=" * 50 + "\n")


# Step 2: Normalize letter cases (proper sentence case)
def normalize_case(text):
    # Split into sentences and normalize each
    sentences = re.split(r'([.!?]+)', text)
    normalized_sentences = []

    for i in range(0, len(sentences), 2):
        if i < len(sentences):
            sentence = sentences[i].strip()
            if sentence:
                # Capitalize first letter and make rest lowercase
                normalized_sentence = sentence[0].upper() + sentence[1:].lower()
                normalized_sentences.append(normalized_sentence)

                # Add punctuation if exists
                if i + 1 < len(sentences):
                    normalized_sentences.append(sentences[i + 1])

    return ''.join(normalized_sentences)


# Step 3: Fix "iZ" with "is" (only when it's a mistake)
def fix_iz_mistakes(text):
    # Replace "iz" with "is" when it's clearly a mistake (not part of other words)
    # Using word boundaries to ensure we only replace standalone "iz"
    fixed_text = re.sub(r'\biz\b', 'is', text, flags=re.IGNORECASE)
    return fixed_text


# Step 4: Create sentence with last words and add to end
def add_last_words_sentence(text):
    # Find all sentences (split by ., !, ?)
    sentences = re.split(r'[.!?]+', text)
    last_words = []

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            words = sentence.split()
            if words:
                last_words.append(words[-1])

    if last_words:
        new_sentence = " ".join(last_words) + "."
        text += " " + new_sentence

    return text


# Step 5: Count whitespace characters
def count_whitespaces(text):
    whitespace_count = 0
    for char in text:
        if char.isspace():  # This includes spaces, tabs, newlines, etc.
            whitespace_count += 1
    return whitespace_count


# Process the text step by step
print("Step 1: Original text copied to variable ✓")
print(f"Original whitespace count: {count_whitespaces(original_text)}")
print()

# Apply transformations
step2_text = normalize_case(original_text)
print("Step 2: Normalized case")
print(step2_text)
print()

step3_text = fix_iz_mistakes(step2_text)
print("Step 3: Fixed 'iZ' mistakes")
print(step3_text)
print()

step4_text = add_last_words_sentence(step3_text)
print("Step 4: Added sentence with last words")
print(step4_text)
print()

# Final whitespace count
final_whitespace_count = count_whitespaces(step4_text)
print("Step 5: Whitespace analysis")
print(f"Final whitespace count: {final_whitespace_count}")
print()

# Let's also show the breakdown of whitespace characters
print("Whitespace character breakdown:")
space_count = step4_text.count(' ')
newline_count = step4_text.count('\n')
tab_count = step4_text.count('\t')
other_whitespace = final_whitespace_count - space_count - newline_count - tab_count

print(f"Spaces: {space_count}")
print(f"Newlines: {newline_count}")
print(f"Tabs: {tab_count}")
print(f"Other whitespace: {other_whitespace}")
print(f"Total whitespace: {final_whitespace_count}")

print("\n" + "*" * 50)
print("FINAL PROCESSED TEXT:")
print("*" * 50)
print(step4_text)