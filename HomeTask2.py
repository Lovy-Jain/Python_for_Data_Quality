import random
import string

# Step 1: Create a list of random number of dictionaries (from 2 to 10)
print("Step 1: Generating random dictionaries...")

# Generate a random number between 2 and 10 to determine how many dictionaries to create
num_dicts = random.randint(2, 10)
print(f"Creating {num_dicts} dictionaries...")

# Initialize an empty list to store our dictionaries
list_of_dicts = []

# Loop to create the specified number of dictionaries
for dict_index in range(num_dicts):
    print(f"\nCreating dictionary #{dict_index + 1}:")

    # Create an empty dictionary for current iteration
    current_dict = {}

    # Generate a random number of keys for this dictionary (between 1 and 5)
    num_keys = random.randint(1, 5)
    print(f"  - Will have {num_keys} keys")

    # Loop to create random key-value pairs
    for key_index in range(num_keys):
        # Generate a random lowercase letter as the key
        random_key = random.choice(string.ascii_lowercase)

        # Generate a random value between 0 and 100
        random_value = random.randint(0, 100)

        # Add the key-value pair to current dictionary
        # Note: if same letter is chosen, it will overwrite (which is fine for this exercise)
        current_dict[random_key] = random_value
        print(f"    Key: '{random_key}' -> Value: {random_value}")

    # Add the completed dictionary to our list
    list_of_dicts.append(current_dict)
    print(f"  - Final dictionary: {current_dict}")

# Display the complete list of generated dictionaries
print(f"\nGenerated list of dictionaries:")
for i, dict_item in enumerate(list_of_dicts):
    print(f"Dict {i + 1}: {dict_item}")

print("\n" + "=" * 60)
print("Step 2: Merging dictionaries with conflict resolution...")
print("=" * 60)

# Step 2: Create one common dictionary by merging all dictionaries
# Initialize the result dictionary that will contain our merged data
merged_dict = {}

# Create a tracking dictionary to store which dictionary each key came from
# This will help us rename keys when there are conflicts
key_sources = {}

# Iterate through each dictionary with its index
for dict_index, current_dict in enumerate(list_of_dicts):
    print(f"\nProcessing dictionary #{dict_index + 1}: {current_dict}")

    # Iterate through each key-value pair in the current dictionary
    for key, value in current_dict.items():
        print(f"  Processing key '{key}' with value {value}")

        # Check if this key already exists in our merged dictionary
        if key in merged_dict:
            print(f"    Key '{key}' already exists with value {merged_dict[key]}")

            # Get the current value for this key in merged dictionary
            existing_value = merged_dict[key]

            # Compare values to determine which one to keep (we want the maximum)
            if value > existing_value:
                print(f"    New value {value} is greater than existing {existing_value}")

                # The new value is larger, so we need to:
                # 1. Rename the old key with its dictionary number
                old_dict_number = key_sources[key]
                old_key_name = f"{key}_{old_dict_number + 1}"
                merged_dict[old_key_name] = existing_value
                print(f"    Renamed old key to '{old_key_name}' with value {existing_value}")

                # 2. Update the current key with new value and source
                merged_dict[key] = value
                key_sources[key] = dict_index
                print(f"    Updated '{key}' with new value {value}")

            else:
                print(f"    Existing value {existing_value} is greater or equal")

                # The existing value is larger or equal, so rename the new key
                new_key_name = f"{key}_{dict_index + 1}"
                merged_dict[new_key_name] = value
                print(f"    Added new key '{new_key_name}' with value {value}")

        else:
            # Key doesn't exist in merged dictionary, add it directly
            merged_dict[key] = value
            key_sources[key] = dict_index
            print(f"    Added new key '{key}' with value {value}")

# Display the final merged dictionary
print(f"\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)

print(f"Original list of dictionaries:")
for i, dict_item in enumerate(list_of_dicts):
    print(f"  Dict {i + 1}: {dict_item}")

print(f"\nMerged dictionary: {merged_dict}")

