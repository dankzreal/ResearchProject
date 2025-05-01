import os
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.corpus import stopwords
from nltk.tree import Tree

# Download necessary NLTK resources
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')


# Function to perform text processing
def process_text(text):
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [t.lower() for t in tokens if t.isalpha()]
    filtered_tokens = [t for t in tokens if t not in stop_words and len(t) > 2]

    pos_tags = pos_tag(filtered_tokens)
    named_entities = []
    chunked = ne_chunk(pos_tags)

    for chunk in chunked:
        if isinstance(chunk, Tree):
            entity = " ".join(c[0] for c in chunk)
            named_entities.append(entity)

    return {
        'tokens': filtered_tokens,
        'pos_tags': pos_tags,
        'bag_of_words': list(set(filtered_tokens)),
        'named_entities': named_entities
    }


# Function to analyze sentiment of a review
def analyze_sentiment(review):
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(review)
    return sentiment_scores


# Load CSV file
def load_reviews_from_csv(file_path):
    first_row = pd.read_csv(file_path, nrows=1, header=None)
    restaurant_url = first_row.iloc[0, 0]

    data = pd.read_csv(file_path, skiprows=1)

    print(f"Columns in {file_path}: {data.columns.tolist()}")

    if 'Description' in data.columns:
        return data['Description'].tolist(), data, restaurant_url
    else:
        print(f"Error: No 'Description' column found in {file_path}.")
        return [], None, restaurant_url


# Analyze reviews in the CSV file
def analyze_reviews(file_path):
    reviews, data, restaurant_url = load_reviews_from_csv(file_path)
    results = []

    num_reviews = len(reviews)
    avg_rating = data['Rating'].mean() if 'Rating' in data.columns else 0

    for review in reviews:
        if isinstance(review, str) and review.strip():
            sentiment_scores = analyze_sentiment(review)
            text_features = process_text(review)
            results.append({
                'Review': ' '.join(text_features['tokens']),
                'Sentiment': sentiment_scores,
                'TextFeatures': text_features
            })
        else:
            print(f"Warning: Invalid review encountered (skipped): {review}")

    if results:
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
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the directory.")
        return None

    print("Available CSV files:")
    for idx, file in enumerate(csv_files):
        print(f"{idx + 1}. {file}")

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
def save_sentiment_results(original_file_path, sentiment_results, aggregated_scores, num_reviews, avg_rating, data, restaurant_url):
    os.makedirs("Sentiments", exist_ok=True)

    results_data = []
    for idx, result in enumerate(sentiment_results):
        review = result['Review']
        sentiment = result['Sentiment']
        rating = data.iloc[idx]['Rating']
        date = data.iloc[idx]['Date']
        text_features = result['TextFeatures']

        results_data.append({
            'Review': review,
            'Sentiment': str(sentiment),
            'Rating': rating,
            'Date': date,
            'BagOfWordsSize': len(text_features['bag_of_words']),
            'NamedEntitiesCount': len(text_features['named_entities'])
        })

    results_df = pd.DataFrame(results_data)

    original_file_name = os.path.basename(original_file_path)
    base_file_name = os.path.splitext(original_file_name)[0]
    new_file_name = base_file_name.replace('_reviews', '') + '_sentiment.csv'
    new_file_path = os.path.join("Sentiments", new_file_name)

    with open(new_file_path, mode='w', newline='', encoding='utf-8') as f:
        f.write(f"{restaurant_url}\n")
        results_df.to_csv(f, index=False)

    aggregated_scores_df = pd.DataFrame([aggregated_scores])
    aggregated_file_name = base_file_name.replace('_reviews', '') + '_aggregated.csv'
    aggregated_file_path = os.path.join("Sentiments", aggregated_file_name)
    aggregated_scores_df.to_csv(aggregated_file_path, index=False)

    restaurant_name = base_file_name.replace('_reviews', '')
    master_data = {
        'Name': restaurant_name,
        'URL': restaurant_url,
        'Reviews': num_reviews,
        'Rating': avg_rating,
        'Positive': aggregated_scores['pos'],
        'Neutral': aggregated_scores['neu'],
        'Negative': aggregated_scores['neg'],
        'Compound': aggregated_scores['compound']
    }

    update_master_sentiment_csv(master_data)


# Function to update master sentiment CSV
def update_master_sentiment_csv(master_data):
    master_file_path = "Sentiments/master_sentiment.csv"

    if os.path.exists(master_file_path):
        master_df = pd.read_csv(master_file_path)
        master_df = pd.concat([master_df, pd.DataFrame([master_data])], ignore_index=True)
    else:
        columns = ['Name', 'URL', 'Reviews', 'Rating', 'Positive', 'Neutral', 'Negative', 'Compound']
        master_df = pd.DataFrame([master_data], columns=columns)

    master_df.to_csv(master_file_path, index=False)


# Main function
def main():
    while True:
        file_path = select_csv_file()

        if file_path:
            print(f"Analyzing {file_path}...\n")
            sentiment_results, aggregated_scores, num_reviews, avg_rating, data, restaurant_url = analyze_reviews(file_path)

            for result in sentiment_results:
                print(f"Review: {result['Review']}")
                print(f"Sentiment Scores: {result['Sentiment']}")
                print('-' * 50)

            print("\nAggregated Sentiment Scores (Average for the Restaurant):")
            print(f"Negative: {aggregated_scores['neg']:.2f}")
            print(f"Neutral: {aggregated_scores['neu']:.2f}")
            print(f"Positive: {aggregated_scores['pos']:.2f}")
            print(f"Compound: {aggregated_scores['compound']:.2f}")

            save_sentiment_results(file_path, sentiment_results, aggregated_scores, num_reviews, avg_rating, data, restaurant_url)

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
