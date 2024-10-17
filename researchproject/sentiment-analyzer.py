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
    # Read the CSV file into a pandas DataFrame
    data = pd.read_csv(file_path)
    # Assuming the reviews are in a column named 'Description'
    if 'Description' in data.columns:
        return data['Description'].tolist()
    else:
        print(f"Error: No 'Description' column found in {file_path}.")
        return []


# Analyze reviews in the CSV file
def analyze_reviews(file_path):
    reviews = load_reviews_from_csv(file_path)
    results = []

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

    return results, aggregated_scores


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
def save_sentiment_results(original_file_path, sentiment_results, aggregated_scores):
    # Prepare results DataFrame
    results_df = pd.DataFrame(sentiment_results)

    # Create directory if it doesn't exist
    os.makedirs("Sentiments", exist_ok=True)

    # Get original file name and create new file name with suffix
    original_file_name = os.path.basename(original_file_path)
    new_file_name = os.path.splitext(original_file_name)[0] + '_sentiment.csv'
    new_file_path = os.path.join("Sentiments", new_file_name)

    # Save individual reviews
    results_df.to_csv(new_file_path, index=False)

    # Save aggregated scores
    aggregated_scores_df = pd.DataFrame([aggregated_scores])
    aggregated_file_name = os.path.splitext(original_file_name)[0] + '_aggregated_scores.csv'
    aggregated_file_path = os.path.join("Sentiments", aggregated_file_name)
    aggregated_scores_df.to_csv(aggregated_file_path, index=False)


# Main function
def main():
    while True:
        file_path = select_csv_file()

        if file_path:
            print(f"Analyzing {file_path}...\n")
            sentiment_results, aggregated_scores = analyze_reviews(file_path)

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
            save_sentiment_results(file_path, sentiment_results, aggregated_scores)

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
