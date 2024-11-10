import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout
from datetime import datetime, timedelta
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}


def convert_relative_time(relative_time):
    """Converts relative time (e.g., 'Yesterday', '19 hours ago', 'one month ago') to an absolute date."""
    now = datetime.now()

    # Handle "Yesterday" specifically
    if relative_time.strip().lower() == "yesterday":
        absolute_date = now - timedelta(days=1)
        return absolute_date.strftime("%Y-%m-%d")

    # Handle "one" as a number and singular units (e.g., "one month ago")
    relative_time = re.sub(r"\bone\b", "1", relative_time)
    relative_time = re.sub(r"(\d+)\s+(second|minute|hour|day|week|month|year)\s+ago", r"\1 \2s ago", relative_time)

    # Extract the number and unit from other relative time strings
    match = re.match(r"(\d+)\s+(seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago", relative_time)
    if match:
        number = int(match.group(1))
        unit = match.group(2)

        # Calculate the absolute date based on the unit
        if unit.startswith("second"):
            absolute_date = now - timedelta(seconds=number)
        elif unit.startswith("minute"):
            absolute_date = now - timedelta(minutes=number)
        elif unit.startswith("hour"):
            absolute_date = now - timedelta(hours=number)
        elif unit.startswith("day"):
            absolute_date = now - timedelta(days=number)
        elif unit.startswith("week"):
            absolute_date = now - timedelta(weeks=number)
        elif unit.startswith("month"):
            absolute_date = now - timedelta(days=number * 30)  # Approximate each month as 30 days
        elif unit.startswith("year"):
            absolute_date = now - timedelta(days=number * 365)  # Approximate each year as 365 days

        return absolute_date.strftime("%Y-%m-%d")

    return "N/A"


def clean_reviews(html_text):
    """Cleans and collects the reviews from the HTML"""
    try:
        reviews = html_text.find_all('script', type='application/ld+json')[1]
        reviews = json.loads(reviews.string)['reviews']
        data = []
        review_date_tags = html_text.find_all('p', class_='sc-1hez2tp-0 fKvqMN time-stamp')

        for i, review in enumerate(reviews):
            # Extract the relative date from the <p> tag
            relative_date = review_date_tags[i].get_text(strip=True) if i < len(review_date_tags) else 'N/A'
            absolute_date = convert_relative_time(relative_date) if relative_date != 'N/A' else 'N/A'

            # Append data with the new Date column
            data.append((
                review['author'],
                review['url'],
                review['description'],
                review['reviewRating']['ratingValue'],
                absolute_date  # New Date column with converted absolute date
            ))
        return data
    except (IndexError, KeyError) as e:
        print(f"Error extracting reviews: {e}")
        return []


def save_df(file_name, df, restaurant_url, sort_order, num_reviews):
    """Save the DataFrame with better filepathing and avoid blank rows"""
    directory = "Reviews"

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Create the file name with sorting and review count
    file_name = f"{file_name}_{sort_order}_{num_reviews}_reviews.csv"

    # Open the file and write the restaurant URL as the first line
    with open(f"{directory}/{file_name}", "w", encoding="utf-8", newline='') as file:
        file.write(f"{restaurant_url}\n")  # Add restaurant URL at the top
        # Write the DataFrame to CSV without adding extra blank lines
        df.to_csv(file, index=False, header=True)  # header=True ensures column names are written

    print(f"File saved as: {directory}/{file_name}")


def get_reviews(url, max_reviews, sort='popular', save=True):
    """Get all reviews from the passed URL"""

    global headers

    # Setting variables for the scraping
    max_reviews = max_reviews // 5  # Convert to number of pages (5 reviews per page)
    sort_order = 'popular' if sort == 'popular' else 'new'
    if sort == 'popular':
        sort = '&sort=rd'
    elif sort == 'new':
        sort = '&sort=dd'

    reviews = []
    prev_data = None

    print("Scraping...")  # Show scraping message

    # Collecting the reviews
    try:
        for i in range(1, max_reviews + 1):  # +1 to ensure the correct number of pages
            link = url + f"/reviews?page={i}{sort}"
            try:
                webpage = requests.get(link, headers=headers, timeout=10)  # 10 seconds timeout
                webpage.raise_for_status()  # Raise exception for bad status codes

            except Timeout:
                print(f"Request timed out for page {i}. Skipping this page...")
                continue  # Skip to the next page

            except RequestException as e:
                print(f"Error occurred while making a request: {e}")
                return pd.DataFrame()  # Return an empty DataFrame on request failure

            html_text = BeautifulSoup(webpage.text, 'lxml')
            data = clean_reviews(html_text)

            if not data:  # If no reviews were extracted, stop scraping
                print("No more reviews found or an error occurred.")
                break

            if prev_data == data:  # If the same reviews are being fetched, stop
                print("Duplicate reviews found. Stopping...")
                break

            reviews.extend(data)
            prev_data = data

        if not reviews:
            print("No reviews were scraped.")
            return pd.DataFrame()  # Return empty DataFrame if no reviews were found

        # Extracting the restaurant name from the URL
        restaurant_name = url.split("/")[-1].replace("-", "_")

        columns = ['Author', 'Review URL', 'Description', 'Rating', 'Date']
        review_df = pd.DataFrame(reviews, columns=columns)

        # Save reviews in CSV file with restaurant URL and other details
        if save:
            save_df(restaurant_name, review_df, url, sort_order, len(reviews))

        return review_df

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return pd.DataFrame()  # Return empty DataFrame on general failure


if __name__ == "__main__":
    # Get inputs from the user
    url = input("Enter the Zomato restaurant URL: ").strip()

    # Prompt user for number of reviews to scrape
    try:
        max_reviews = int(input("Enter the number of reviews to scrape (e.g., 50): ").strip())
    except ValueError:
        print("Invalid input, defaulting to 50 reviews.")
        max_reviews = 50

    # Prompt user for sorting preference
    sort = input("Enter sorting preference ('new' or 'popular', default is 'popular'): ").strip().lower()
    if sort not in ['new', 'popular']:
        print("Invalid sorting option, defaulting to 'popular'.")
        sort = 'popular'

    # Call the function with user inputs
    reviews_df = get_reviews(url, max_reviews, sort)

    if not reviews_df.empty:
        print(f"Scraped {len(reviews_df)} reviews successfully!")
    else:
        print("No reviews were scraped.")
