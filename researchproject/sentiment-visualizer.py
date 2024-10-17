import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud


# Load sentiment results from CSV files in the Sentiments directory
def load_sentiment_results(directory='Sentiments'):
    # List all sentiment result CSV files in the specified directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('_sentiment.csv')]

    if not csv_files:
        print("No sentiment result CSV files found in the directory.")
        return None

    return csv_files


# Plot sentiment results
def plot_sentiment(results_df, restaurant_name):
    # Assuming the results DataFrame has a 'Sentiment' column with dictionary-like strings
    sentiment_labels = ['Negative', 'Neutral', 'Positive', 'Compound']
    sentiment_values = [
        results_df['Sentiment'].apply(lambda x: eval(x)['neg']).mean(),
        results_df['Sentiment'].apply(lambda x: eval(x)['neu']).mean(),
        results_df['Sentiment'].apply(lambda x: eval(x)['pos']).mean(),
        results_df['Sentiment'].apply(lambda x: eval(x)['compound']).mean(),
    ]

    # Create a bar plot for sentiment scores
    plt.figure(figsize=(10, 6))
    plt.bar(sentiment_labels, sentiment_values, color=['red', 'blue', 'green', 'orange'])
    plt.title(f'Aggregated Sentiment Scores for {restaurant_name}')
    plt.xlabel('Sentiment')
    plt.ylabel('Average Score')
    plt.ylim(0, 1)
    plt.grid(axis='y')
    plt.show()


# Generate and display a word cloud from the reviews
def generate_word_cloud(reviews):
    # Join all reviews into a single string
    all_reviews = ' '.join(reviews)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_reviews)

    # Display the word cloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Reviews')
    plt.show()


# Let user select a CSV file to visualize
def select_csv_file(directory='Sentiments'):
    # List all sentiment result CSV files in the specified directory
    csv_files = [f for f in os.listdir(directory) if f.endswith('_sentiment.csv')]

    if not csv_files:
        print("No sentiment result CSV files found in the directory.")
        return None

    # Display the available CSV files for selection
    print("Available Sentiment CSV files:")
    for idx, file in enumerate(csv_files):
        print(f"{idx + 1}. {file}")

    # Prompt the user to select a file
    while True:
        try:
            choice = int(input("Enter the number of the file you want to visualize: "))
            if 1 <= choice <= len(csv_files):
                return os.path.join(directory, csv_files[choice - 1])
            else:
                print(f"Invalid selection. Please select a number between 1 and {len(csv_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")


# Main function
def main():
    # Let the user select a sentiment CSV file
    file_path = select_csv_file()

    if file_path:
        print(f"Loading {file_path} for visualization...")

        # Load the sentiment analysis results
        results_df = pd.read_csv(file_path)

        # Extract the restaurant name from the file name
        restaurant_name = os.path.basename(file_path).split('_sentiment')[0]

        # Plot the aggregated sentiment scores
        plot_sentiment(results_df, restaurant_name)

        # Generate the word cloud using the reviews
        reviews = results_df['Review'].dropna().tolist()  # Ensure we only use non-NaN reviews
        generate_word_cloud(reviews)


# Run the program
if __name__ == "__main__":
    main()
