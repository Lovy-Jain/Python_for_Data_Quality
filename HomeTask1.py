# Import the random module to generate random numbers
import random

# Create a list of 100 random numbers between 0 and 1000
print("Generating 100 random numbers between 0 and 1000...")
random_numbers = []  # Initialize an empty list to store random numbers

# Loop 100 times to generate random numbers
for i in range(100):
    # Generate a random integer between 0 and 1000 (inclusive)
    random_number = random.randint(0, 1000)
    # Add the generated number to our list
    random_numbers.append(random_number)

# Display the first 10 numbers to show what we generated
print(f"First 10 random numbers: {random_numbers[:10]}")

# Sort the list from min to max without using built-in sort() function
# We'll use bubble sort algorithm for this purpose
print("\nSorting numbers using bubble sort algorithm...")

# Get the length of the list for our sorting loops
n = len(random_numbers)

# Bubble sort implementation - outer loop for number of passes
for i in range(n):
    # Inner loop for comparing adjacent elements
    # We reduce the range by i because the largest elements "bubble up" to the end
    for j in range(0, n - i - 1):
        # Compare current element with the next element
        if random_numbers[j] > random_numbers[j + 1]:
            # Swap elements if they are in wrong order (current > next)
            random_numbers[j], random_numbers[j + 1] = random_numbers[j + 1], random_numbers[j]

# Display the first and last 10 sorted numbers to verify sorting
print(f"First 10 sorted numbers: {random_numbers[:10]}")
print(f"Last 10 sorted numbers: {random_numbers[-10:]}")

# Separate even and odd numbers from the sorted list
even_numbers = []  # List to store even numbers
odd_numbers = []   # List to store odd numbers

# Iterate through each number in the sorted list
for number in random_numbers:
    # Check if the number is even (divisible by 2 with no remainder)
    if number % 2 == 0:
        # Add to even numbers list
        even_numbers.append(number)
    else:
        # Add to odd numbers list (if not even, then it's odd)
        odd_numbers.append(number)

# Calculate average for even numbers
# First check if we have any even numbers to avoid division by zero
if len(even_numbers) > 0:
    # Sum all even numbers and divide by count to get average
    even_sum = sum(even_numbers)
    even_count = len(even_numbers)
    even_average = even_sum / even_count
else:
    # Set average to 0 if no even numbers found
    even_average = 0

# Calculate average for odd numbers
# First check if we have any odd numbers to avoid division by zero
if len(odd_numbers) > 0:
    # Sum all odd numbers and divide by count to get average
    odd_sum = sum(odd_numbers)
    odd_count = len(odd_numbers)
    odd_average = odd_sum / odd_count
else:
    # Set average to 0 if no odd numbers found
    odd_average = 0

# Print the results to console with detailed information
print("\n" + "="*50)
print("ANALYSIS RESULTS")
print("="*50)

# Display total count of numbers
print(f"Total numbers generated: {len(random_numbers)}")

# Display count and average of even numbers
print(f"Count of even numbers: {len(even_numbers)}")
print(f"Average of even numbers: {even_average:.2f}")

# Display count and average of odd numbers
print(f"Count of odd numbers: {len(odd_numbers)}")
print(f"Average of odd numbers: {odd_average:.2f}")

# Display the range of numbers (min and max from sorted list)
print(f"Smallest number: {random_numbers[0]}")
print(f"Largest number: {random_numbers[-1]}")

print("="*50)