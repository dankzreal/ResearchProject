import os


def scrape_reviews():
    """ Function to scrape reviews from the website. """
    print("Starting review scraping...")
    # Call the zomato-review-scraper.py here
    os.system("python zomato-review-scraper.py")


def analyze_sentiments():
    """ Function to run sentiment analysis on the scraped reviews. """
    print("Running sentiment analysis...")
    # Call the sentiment-analyzer.py here
    os.system("python sentiment-analyzer.py")


def launch_dashboard():
    """ Function to launch the dashboard. """
    print("Launching dashboard...")
    # Call the overview_dashboard.py here
    os.system("python overview_dashboard.py")


def main():
    """ Main function to control the workflow. """
    print("Welcome to the Review Analysis Tool!")

    # Options to skip steps
    scrape = input("Do you want to scrape reviews? (y/n): ").strip().lower()
    analyze = input("Do you want to run sentiment analysis? (y/n): ").strip().lower()
    launch = input("Do you want to launch the dashboard? (y/n): ").strip().lower()

    if scrape == 'y':
        scrape_reviews()
    else:
        print("Skipping review scraping.")

    if analyze == 'y':
        analyze_sentiments()
    else:
        print("Skipping sentiment analysis.")

    if launch == 'y':
        launch_dashboard()
    else:
        print("Skipping dashboard launch.")


if __name__ == "__main__":
    main()
