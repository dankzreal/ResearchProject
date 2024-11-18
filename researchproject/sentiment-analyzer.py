import os
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download necessary NLTK resources
nltk.download('vader_lexicon')


# Function to analyze sentiment of a review
def analyze_sentiment(review):
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(review)
    return sentiment_scores


# Load CSV file
def load_reviews_from_csv(file_path):
    # Read the first row separately to extract the URL
    first_row = pd.read_csv(file_path, nrows=1, header=None)
    restaurant_url = first_row.iloc[0, 0]  # URL is in the first column of the first row

    # Read the rest of the file for reviews (skip the first row)
    data = pd.read_csv(file_path, skiprows=1)

    # Print columns for confirmation (debugging stuff)
    print(f"Columns in {file_path}: {data.columns.tolist()}")

    # Assuming the reviews are in a column named 'Description'
    if 'Description' in data.columns:
        return data['Description'].tolist(), data, restaurant_url
    else:
        print(f"Error: No 'Description' column found in {file_path}.")
        return [], None, restaurant_url


# Analyze reviews in the CSV file
def analyze_reviews(file_path):
    reviews, data, restaurant_url = load_reviews_from_csv(file_path)
    results = []

    # Aggregate variables
    num_reviews = len(reviews)
    avg_rating = data['Rating'].mean() if 'Rating' in data.columns else 0

    # Iterate over each review and analyze sentiment
    for review in reviews:
        # Check if the review is a valid string
        if isinstance(review, str) and review.strip():  # Skip NaN and empty strings
            sentiment_scores = analyze_sentiment(review)
            results.append({
                'Review': review,
                'Sentiment': sentiment_scores
            })
        else:
            # Skip NaN or empty entries
            print(f"Warning: Invalid review encountered (skipped): {review}")

    # Aggregate scores
    if results:  # Ensure there are results to aggregate
        aggregated_scores = {
            'pos': sum(result['Sentiment']['pos'] for result in results) / len(results),
            'neu': sum(result['Sentiment']['neu'] for result in results) / len(results),
            'neg': sum(result['Sentiment']['neg'] for result in results) / len(results),
            'compound': sum(result['Sentiment']['compound'] for result in results) / len(results),
        }
    else:
        aggregated_scores = {'pos': 0, 'neu': 0, 'neg': 0, 'compound': 0}

    return results, aggregated_scores, num_reviews, avg_rating, data, restaurant_url


# Let user select a CSV file to analyze
def select_csv_file(directory='Reviews'):
    # List all CSV files in the specified directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the directory.")
        return None

    # Display the available CSV files for selection
    print("Available CSV files:")
    for idx, file in enumerate(csv_files):
        print(f"{idx + 1}. {file}")

    # Prompt the user to select a file
    while True:
        try:
            choice = int(input("Enter the number of the file you want to analyze: "))
            if 1 <= choice <= len(csv_files):
                return os.path.join(directory, csv_files[choice - 1])
            else:
                print(f"Invalid selection. Please select a number between 1 and {len(csv_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Save results to a CSV file
def save_sentiment_results(original_file_path, sentiment_results, aggregated_scores, num_reviews, avg_rating, data,
                           restaurant_url):
    # Ensure the 'Sentiments' directory exists
    os.makedirs("Sentiments", exist_ok=True)

    # Prepare results DataFrame
    results_data = []
    for idx, result in enumerate(sentiment_results):
        review = result['Review']
        sentiment = result['Sentiment']
        rating = data.iloc[idx]['Rating']  # Get the Rating from the DataFrame
        date = data.iloc[idx]['Date']  # Get the Date from the DataFrame
        results_data.append({
            'Review': review,
            'Sentiment': sentiment,
            'Rating': rating,
            'Date': date
        })

    # Create the results DataFrame
    results_df = pd.DataFrame(results_data)

    # Get original file name and remove '_reviews' part for the sentiment file
    original_file_name = os.path.basename(original_file_path)
    base_file_name = os.path.splitext(original_file_name)[0]  # Remove file extension
    new_file_name = base_file_name.replace('_reviews', '') + '_sentiment.csv'  # Remove '_reviews' and add '_sentiment'

    new_file_path = os.path.join("Sentiments", new_file_name)

    # Save the results DataFrame to CSV
    with open(new_file_path, mode='w', newline='', encoding='utf-8') as f:
        # Write the restaurant URL in the first row as a header
        f.write(f"{restaurant_url}\n")

        # Now, write the column headers (without the restaurant URL)
        results_df.to_csv(f, index=False)

    # Save aggregated scores with '_aggregated' suffix (no restaurant URL)
    aggregated_scores_df = pd.DataFrame([aggregated_scores])
    aggregated_file_name = base_file_name.replace('_reviews', '') + '_aggregated.csv'
    aggregated_file_path = os.path.join("Sentiments", aggregated_file_name)
    aggregated_scores_df.to_csv(aggregated_file_path, index=False)

    # Prepare master data for CSV (including restaurant name and URL)
    restaurant_name = base_file_name.replace('_reviews', '')  # Extract restaurant name from base file name
    master_data = {
        'Name': restaurant_name,  # Add restaurant name
        'URL': restaurant_url,  # Add restaurant URL
        'Reviews': num_reviews,
        'Rating': avg_rating,
        'Positive': aggregated_scores['pos'],
        'Neutral': aggregated_scores['neu'],
        'Negative': aggregated_scores['neg'],
        'Compound': aggregated_scores['compound']
    }

    # Update the master sentiment CSV (restaurant URL included here)
    update_master_sentiment_csv(master_data)


# Function to update master sentiment CSV
def update_master_sentiment_csv(master_data):
    master_file_path = "Sentiments/master_sentiment.csv"

    # Check if the master CSV exists
    if os.path.exists(master_file_path):
        # If exists, read the existing data and append the new data
        master_df = pd.read_csv(master_file_path)
        master_df = pd.concat([master_df, pd.DataFrame([master_data])], ignore_index=True)
    else:
        # If doesn't exist, create it and add header
        columns = ['Name', 'URL', 'Reviews', 'Rating', 'Positive', 'Neutral', 'Negative', 'Compound']
        master_df = pd.DataFrame([master_data], columns=columns)

    # Save back to the master CSV
    master_df.to_csv(master_file_path, index=False)


# Main function
def main():
    while True:
        file_path = select_csv_file()

        if file_path:
            print(f"Analyzing {file_path}...\n")
            sentiment_results, aggregated_scores, num_reviews, avg_rating, data, restaurant_url = analyze_reviews(
                file_path)

            for result in sentiment_results:
                print(f"Review: {result['Review']}")
                print(f"Sentiment Scores: {result['Sentiment']}")
                print('-' * 50)

            print("\nAggregated Sentiment Scores (Average for the Restaurant):")
            print(f"Negative: {aggregated_scores['neg']:.2f}")
            print(f"Neutral: {aggregated_scores['neu']:.2f}")
            print(f"Positive: {aggregated_scores['pos']:.2f}")
            print(f"Compound: {aggregated_scores['compound']:.2f}")

            # Save results to CSV
            save_sentiment_results(file_path, sentiment_results, aggregated_scores, num_reviews, avg_rating, data,
                                   restaurant_url)

        while True:
            choice = input("\nWould you like to analyze another file? (y/n): ").strip().lower()
            if choice == 'y':
                break
            elif choice == 'n':
                print("Ending the program.")
                return
            else:
                print("Invalid choice. Please enter 'y' for yes or 'n' for no.")


# Run the program
if __name__ == "__main__":
    main()
