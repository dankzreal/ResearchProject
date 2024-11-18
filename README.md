# **Sentiment Analysis Dashboard for Zomato Reviews**

## **Overview**

This Python-based project was made as a part of a Research Project at <b> Symbiosis Centre for Management Studies</b>. It is a sentiment analysis framework designed for small businesses, particularly restaurants, to analyze customer reviews collected from **Zomato**. The application uses web scraping, sentiment analysis, and an interactive dashboard to provide actionable insights into customer sentiment, aiding businesses in improving their services and marketing strategies.

The project combines multiple technologies, including Flask for backend support, Dash and Plotly for visualizations, and Python libraries for data processing and sentiment analysis.

---

## **Features**

- **Web Scraping**: Extract over 1000 customer reviews from Zomato using BeautifulSoup.
- **Sentiment Analysis**: Classify reviews as positive, neutral, or negative using Natural Language Processing (NLP) techniques.
- **Interactive Dashboard**:
  - Visualizations: Sentiment distribution, word clouds, monthly review trends, and review ratings.
  - Filters: Drill down data by sentiment type, review month, and more.
  - Key Metrics: Display average sentiment scores, total reviews, and restaurant ratings.
- **Export Functionality**: Saves processed sentiment data as CSV files for future use.
- **User-Friendly UI**: A clean, responsive design tailored for non-technical users.

---

## **Project Structure**

```plaintext
root/
├── static/                # Contains static files like CSS
├── templates/             # HTML templates for Flask
├── Sentiments/            # Folder to store processed sentiment CSV files
├── main.py                # Main script
├── zomato-review-scraper.py # Script for scraping Zomato reviews
├── sentiment-analyzer.py  # Script for analyzing review sentiment
├── sentiment_visualizer.py # Script (if required) for additional visualizations
├── dashboard.py           # Dash and Flask-based interactive dashboard
├── README.md              # Documentation file
├── requirements.txt       # Python dependencies
```
---
## Usage Instructions

Once the setup is complete, the dashboard provides the following functionalities:

### 1. **Key Metrics**
   - **Compound Sentiment Score**: Overall sentiment polarity of the reviews.
   - **Restaurant Rating**: The average rating based on review data.
   - **Total Reviews**: Number of reviews analyzed.

### 2. **Sentiment Filters**
   - Filter reviews based on sentiment type:
     - Positive (Compound > 0)
     - Neutral (Compound = 0)
     - Negative (Compound < 0)

### 3. **Month Filter**
   - Analyze reviews for a specific month by selecting from a dropdown.

### 4. **Graphs and Word Cloud**
   - **Sentiment Distribution**: Pie chart categorizing reviews by sentiment.
   - **Reviews per Rating**: Bar graph showing the count of reviews per star rating.
   - **Monthly Review Trends**: Bar graph showing the number of reviews over time.
   - **Word Cloud**: Visual representation of frequently mentioned terms in reviews.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---