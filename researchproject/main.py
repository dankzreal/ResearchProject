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


def launch_overview_dashboard():
    """ Function to launch the overview dashboard. """
    print("Launching overview dashboard...")
    # Call the overview_dashboard.py here
    os.system("python overview_dashboard.py")

def launch_comparative_dashboard():
    """ Function to launch the comparative dashboard. """
    print("Launching comparative dashboard...")
    # Call the comparative_dashboard.py here
    os.system("python comparative_dashboard.py")

def main():
    """ Main function to control the workflow. """
    print("Welcome to the Review Analysis Tool!")

    # Options to skip steps
    scrape = input("Do you want to scrape reviews? (y/n): ").strip().lower()
    analyze = input("Do you want to run sentiment analysis? (y/n): ").strip().lower()
    launch_overview = input("Do you want to launch the overview dashboard? (y/n): ").strip().lower()
    launch_comparative = input("Do you want to launch the comparative dashboard? (y/n): ").strip().lower()

    if scrape == 'y':
        scrape_reviews()
    else:
        print("Skipping review scraping.")

    if analyze == 'y':
        analyze_sentiments()
    else:
        print("Skipping sentiment analysis.")

    if launch_overview == 'y':
        launch_overview_dashboard()
    else:
        print("Skipping overview dashboard launch.")

    if launch_comparative == 'y':
        launch_comparative_dashboard()
    else:
        print("Skipping comparative dashboard launch.")


if __name__ == "__main__":
    main()
