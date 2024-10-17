import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh;'
                         ' Intel Mac OS X 10_15_4)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/83.0.4103.97 Safari/537.36'}


def clean_reviews(html_text):
    """ Cleans and collects the reviews from the html """
    reviews = html_text.find_all('script', type='application/ld+json')[1]
    reviews = json.loads(reviews.string)['reviews']
    data = []
    for review in reviews:
        data.append((
            review['author'],
            review['url'],
            review['description'],
            review['reviewRating']['ratingValue']
        ))
    return data


def save_df(file_name, df):
    """ Save the dataframe """

    # Define a directory to save reviews
    directory = "Reviews"

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Save the DataFrame to a CSV file in the specified directory
    df.to_csv(f"{directory}/{file_name}.csv", index=False)


def get_reviews(url, max_reviews, sort='popular', save=True):
    """ Get all Reviews from the passed url """

    global headers

    # Setting variables for the scraping
    max_reviews = max_reviews // 5  # Convert to number of pages (5 reviews per page)
    if sort == 'popular':
        sort = '&sort=rd'
    elif sort == 'new':
        sort = '&sort=dd'

    reviews = []
    prev_data = None

    # Collecting the reviews
    for i in range(1, max_reviews):
        link = url + f"/reviews?page={i}{sort}"
        webpage = requests.get(link, headers=headers, timeout=5)
        html_text = BeautifulSoup(webpage.text, 'lxml')
        restaurant_name = html_text.head.find('title').text
        data = clean_reviews(html_text)
        if prev_data == data:  # If the same reviews are being fetched, stop
            break
        reviews.extend(data)
        prev_data = data

    # Extracting the restaurant name from the URL
    restaurant_name = url.split("/")[-1].replace("-", "_")

    columns = ['Author', 'Review URL', 'Description', 'Rating']
    review_df = pd.DataFrame(reviews, columns=columns)

    # Saving the dataframe
    if save:
        save_df(restaurant_name, review_df)

    return review_df


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
    get_reviews(url, max_reviews, sort)
