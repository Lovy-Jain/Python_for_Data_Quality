
import datetime
import random

# Output file
output_file = "news_feed.txt"

# Append formatted text to file
def append_to_file(text):
    with open(output_file, "a") as file:
        file.write(text)
    print("Record published successfully!\n")

# News record
def publish_news():
    text = input("Enter news text: ")
    city = input("Enter city: ")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    formatted = f"News -------------------------\n{text}\n{city}, {date}\n\n"
    append_to_file(formatted)

# Private Ad record
def publish_private_ad():
    text = input("Enter ad text: ")
    exp_date_str = input("Enter expiration date (YYYY-MM-DD): ")
    try:
        exp_date = datetime.datetime.strptime(exp_date_str, "%Y-%m-%d")
        days_left = (exp_date - datetime.datetime.now()).days
        formatted = f"Private Ad -------------------\n{text}\nActual until: {exp_date_str}, {days_left} days left\n\n"
        append_to_file(formatted)
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.\n")

# Unique record (Motivational Quote)
def publish_unique():
    quote = input("Enter motivational quote: ")
    author = input("Enter author name: ")
    rating = random.randint(1, 5)
    formatted = f"Motivational Quote -----------\n\"{quote}\"\n- {author} (Rating: {rating}/5)\n\n"
    append_to_file(formatted)

# Main loop
def main():
    while True:
        print("\nSelect record type to publish:")
        print("1. News")
        print("2. Private Ad")
        print("3. Motivational Quote (Unique)")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            publish_news()
        elif choice == "2":
            publish_private_ad()
        elif choice == "3":
            publish_unique()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select again.\n")

if __name__ == "__main__":
    main()
