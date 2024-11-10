from flask import Flask, render_template
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import dash_table

# Initialize Flask server
server = Flask(__name__)

# Initialize Dash app
app_dash = Dash(__name__, server=server, url_base_pathname='/dash/')

# Dash Layout
app_dash.layout = html.Div([
    html.H1("Sentiment Analysis Dashboard"),

    # Clickable Restaurant URL
    html.Div(id='restaurant-url', children=[], style={'margin-bottom': '20px'}),

    # Key Metrics (below restaurant URL and above filters)
    html.Div([
        html.Div([
            html.P("Compound Score", style={'fontWeight': 'bold'}),
            html.P(id="compound-score", style={'fontSize': '20px'})
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.P("Restaurant Rating", style={'fontWeight': 'bold'}),
            html.P(id="avg-rating", style={'fontSize': '20px'})
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),

        html.Div([
            html.P("Total Reviews", style={'fontWeight': 'bold'}),
            html.P(id="total-reviews", style={'fontSize': '20px'})
        ], style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'})
    ], style={'margin-bottom': '20px', 'display': 'flex', 'justify-content': 'space-between'}),

    dcc.Dropdown(
        id="file-dropdown",
        options=[
            {"label": file, "value": file} for file in os.listdir("Sentiments") if file.endswith('_sentiment.csv')
        ],
        placeholder="Select a CSV File",
    ),

    dcc.Dropdown(
        id="sentiment-filter",
        options=[
            {"label": "Positive (Compound > 0)", "value": "positive"},
            {"label": "Neutral (Compound = 0)", "value": "neutral"},
            {"label": "Negative (Compound < 0)", "value": "negative"}
        ],
        placeholder="Filter by Sentiment Type",
    ),

    # Month Filter Dropdown
    dcc.Dropdown(
        id="month-filter",
        options=[],  # This will be populated dynamically in the callback
        placeholder="Filter by Month",
    ),

    # Flexbox Layout for Table and Graphs
    html.Div([
        # Left side: Table
        html.Div([
            dash_table.DataTable(id='reviews-table',
                                 style_table={'height': '80vh', 'overflowY': 'auto'},
                                 style_cell={'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto',
                                             'lineHeight': '1.5'},
                                 style_data_conditional=[
                                     {
                                         'if': {'column_id': 'Category', 'filter_query': '{Category} = "Positive"'},
                                         'color': 'green',
                                         'fontWeight': 'bold'
                                     },
                                     {
                                         'if': {'column_id': 'Category', 'filter_query': '{Category} = "Neutral"'},
                                         'color': 'yellow',
                                         'fontWeight': 'bold'
                                     },
                                     {
                                         'if': {'column_id': 'Category', 'filter_query': '{Category} = "Negative"'},
                                         'color': 'red',
                                         'fontWeight': 'bold'
                                     }
                                 ]),

        ], style={'width': '40%', 'display': 'inline-block', 'padding': '20px'}),

        # Right side: Graphs
        html.Div([
            dcc.Graph(id="sentiment-bar-graph"),
            html.Img(id="wordcloud-image", style={'width': '50%', 'margin': 'auto'}),
            dcc.Graph(id="monthly-reviews-graph")  # New graph for monthly reviews
        ], style={'width': '55%', 'display': 'inline-block', 'padding': '20px'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
])


# Update the dashboard callback
@app_dash.callback(
    [Output("sentiment-bar-graph", "figure"),
     Output("wordcloud-image", "src"),
     Output("reviews-table", "data"),
     Output("reviews-table", "columns"),
     Output("restaurant-url", "children"),
     Output("monthly-reviews-graph", "figure"),  # New Output for the monthly reviews chart
     Output("month-filter", "options"),  # New Output for dynamically updating the month filter
     Output("compound-score", "children"),  # Output for compound score
     Output("avg-rating", "children"),  # Output for restaurant rating
     Output("total-reviews", "children")],  # Output for total reviews
    [Input("file-dropdown", "value"),
     Input("sentiment-filter", "value"),
     Input("month-filter", "value")]  # New Input for the month filter
)
def update_dashboard(file_name, sentiment_filter, selected_month):
    if file_name is None:
        return {}, "", [], [], "", {}, [], "", "", ""

    # Load sentiment CSV data
    file_path = os.path.join("Sentiments", file_name)

    # Read the first row to extract the restaurant URL and skip it in the actual data frame
    first_row = pd.read_csv(file_path, nrows=1, header=None)
    restaurant_url = first_row.iloc[0, 0]  # URL is in the first column of the first row

    # Load the rest of the CSV without the URL header
    df = pd.read_csv(file_path, skiprows=1)

    # Parse the 'Date' column as datetime and extract the 'Month-Year'
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Handle invalid dates
    df['Month-Year'] = df['Date'].dt.to_period('M').astype(str)  # Format as 'YYYY-MM'

    # Generate month filter options dynamically
    month_options = [{"label": month, "value": month} for month in df['Month-Year'].unique()]

    # Apply sentiment filtering based on the sentiment filter
    if sentiment_filter == "positive":
        filtered_df = df[df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) > 0)]
    elif sentiment_filter == "neutral":
        filtered_df = df[df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) == 0)]
    elif sentiment_filter == "negative":
        filtered_df = df[df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) < 0)]
    else:
        filtered_df = df  # If no filter is selected, use the entire dataset

    # Apply month filter if selected
    if selected_month:
        filtered_df = filtered_df[filtered_df['Month-Year'] == selected_month]

    # Create sentiment bar chart
    sentiment_labels = ['Negative', 'Neutral', 'Positive', 'Compound']
    sentiment_values = [
        filtered_df['Sentiment'].apply(lambda x: eval(x).get('neg', 0)).mean(),
        filtered_df['Sentiment'].apply(lambda x: eval(x).get('neu', 0)).mean(),
        filtered_df['Sentiment'].apply(lambda x: eval(x).get('pos', 0)).mean(),
        filtered_df['Sentiment'].apply(lambda x: eval(x).get('compound', 0)).mean(),
    ]

    fig_sentiment = px.bar(
        x=sentiment_labels,
        y=sentiment_values,
        labels={"x": "Sentiment", "y": "Average Score"},
        title=f"Aggregated Sentiment for {file_name.split('_sentiment')[0]} (Filtered: {sentiment_filter})"
    )

    # Generate word cloud for the filtered reviews
    reviews = filtered_df['Review'].dropna().tolist()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(reviews))

    # Convert the word cloud to a base64 image for embedding
    buffer = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Prepare data for the reviews table
    reviews_data = []
    for index, row in filtered_df.iterrows():
        sentiment = eval(row['Sentiment'])
        category = "Positive" if sentiment.get('compound', 0) > 0 else "Neutral" if sentiment.get('compound', 0) == 0 else "Negative"
        reviews_data.append({
            "Review": row['Review'],
            "Category": category,
            "Sentiment": sentiment
        })

    # Define the columns for the table
    columns = [
        {"name": "Review", "id": "Review"},
        {"name": "Category", "id": "Category"}
    ]

    # Use html.A for clickable restaurant URL
    restaurant_url_link = html.A(
        "Click to go to restaurant's page",
        href=restaurant_url,
        target="_blank"
    )

    # Calculate key metrics
    compound_score = sentiment_values[3]  # Compound sentiment score
    avg_rating = df['Rating'].mean() if 'Rating' in df.columns else "N/A"  # If 'Rating' is present in the CSV
    total_reviews = len(filtered_df)

    # Check if the filtered DataFrame is empty before plotting the monthly reviews graph
    if not filtered_df.empty:
        # Generate Monthly Reviews Chart
        monthly_reviews_count = filtered_df.groupby('Month-Year').size().reset_index(name='Review Count')
        fig_monthly_reviews = px.bar(
            monthly_reviews_count, x='Month-Year', y='Review Count',
            title="Monthly Review Count", labels={"Month-Year": "Month", "Review Count": "Number of Reviews"}
        )
    else:
        # If no data is available, return an empty plot
        fig_monthly_reviews = {}

    # Return all outputs
    return fig_sentiment, f"data:image/png;base64,{image_base64}", reviews_data, columns, restaurant_url_link, fig_monthly_reviews, month_options, compound_score, avg_rating, total_reviews


# Flask route
@server.route('/')
def index():
    return render_template("index.html")


# Run the Flask server
if __name__ == '__main__':
    server.run(debug=True)
