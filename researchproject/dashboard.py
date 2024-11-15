import os
import base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib
import plotly.express as px
from flask import Flask, render_template
from dash import Dash, dcc, html, Input, Output, dash_table

matplotlib.use('Agg')  # For non-interactive backend

# Initialize Flask server
server = Flask(__name__)

# Custom CSS to import Montserrat font
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap'
]

# Initialize Dash app with external stylesheets
app_dash = Dash(__name__, server=server, url_base_pathname='/dash/', external_stylesheets=external_stylesheets)

# Dash Layout
app_dash.layout = html.Div([
    html.H1("Sentiment Analysis Dashboard", style={'fontFamily': 'Montserrat'}),

    # Restaurant URL
    html.Div(id='restaurant-url', style={'margin-bottom': '20px', 'fontFamily': 'Montserrat'}),

    # Key Metrics
    html.Div([
        html.Div([
            html.P("Compound Score", style={'fontWeight': 'bold', 'fontFamily': 'Montserrat'}),
            html.P(id="compound-score", style={'fontSize': '20px', 'fontFamily': 'Montserrat'})
        ], style={'width': '30%', 'textAlign': 'center', 'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '5px'}),

        html.Div([
            html.P("Restaurant Rating", style={'fontWeight': 'bold', 'fontFamily': 'Montserrat'}),
            html.P(id="avg-rating", style={'fontSize': '20px', 'fontFamily': 'Montserrat'})
        ], style={'width': '30%', 'textAlign': 'center', 'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '5px'}),

        html.Div([
            html.P("Total Reviews", style={'fontWeight': 'bold', 'fontFamily': 'Montserrat'}),
            html.P(id="total-reviews", style={'fontSize': '20px', 'fontFamily': 'Montserrat'})
        ], style={'width': '30%', 'textAlign': 'center', 'backgroundColor': '#f0f0f0', 'padding': '10px', 'borderRadius': '5px'}),
    ], style={'margin-bottom': '20px', 'display': 'flex', 'justify-content': 'space-between'}),

    # Dropdowns for file, sentiment, and month filters
    dcc.Dropdown(
        id="file-dropdown",
        options=[{"label": file, "value": file} for file in os.listdir("Sentiments") if file.endswith('_sentiment.csv')],
        placeholder="Select a CSV File",
        style={'fontFamily': 'Montserrat'}
    ),

    dcc.Dropdown(
        id="sentiment-filter",
        options=[
            {"label": "Positive (Compound > 0)", "value": "positive"},
            {"label": "Neutral (Compound = 0)", "value": "neutral"},
            {"label": "Negative (Compound < 0)", "value": "negative"}
        ],
        placeholder="Filter by Sentiment Type",
        multi=True,
        style={'fontFamily': 'Montserrat'}
    ),

    dcc.Dropdown(
        id="month-filter",
        options=[],
        placeholder="Filter by Month",
        multi=True,
        style={'fontFamily': 'Montserrat'}
    ),

    # Search bar
    dcc.Input(
        id="search-bar",
        type="text",
        placeholder="Search reviews...",
        debounce=True,
        style={'width': '100%', 'margin': '10px 0', 'fontFamily': 'Montserrat'}
    ),

    # Layout for Table and Graphs
    html.Div([
        # Table
        html.Div([
            dash_table.DataTable(
                id='reviews-table',
                style_table={'height': '80vh', 'overflowY': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'lineHeight': '1.5',
                    'fontFamily': 'Montserrat'
                },
                style_data_conditional=[
                    {'if': {'column_id': 'Category', 'filter_query': '{Category} = "Positive"'}, 'color': 'green', 'fontWeight': 'bold'},
                    {'if': {'column_id': 'Category', 'filter_query': '{Category} = "Neutral"'}, 'color': 'yellow', 'fontWeight': 'bold'},
                    {'if': {'column_id': 'Category', 'filter_query': '{Category} = "Negative"'}, 'color': 'red', 'fontWeight': 'bold'}
                ]
            )
        ], style={'width': '40%', 'padding': '20px'}),  # Removed backgroundColor here

        # Graphs
        html.Div([
            # Pie chart and word cloud side by side
            html.Div([
                dcc.Graph(id="sentiment-pie-chart", style={'width': '50%', 'height': '325px'}),
                html.Img(id="wordcloud-image", style={'width': '52.5%', 'height': '200px', 'margin': 'auto'})
            ], style={'display': 'flex', 'justify-content': 'space-between', 'max-width': '100%'}),

            # Full-width line chart below pie chart and word cloud
            dcc.Graph(id="monthly-sentiment-line-chart", style={'width': '100%', 'height': '400px'}),

            dcc.Graph(id="monthly-reviews-graph")
        ], style={'width': '55%', 'padding': '20px'})  # Removed backgroundColor here
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
], style={'fontFamily': 'Montserrat'})


# Updated callback function to filter based on search term
@app_dash.callback(
    [Output("sentiment-pie-chart", "figure"),
     Output("wordcloud-image", "src"),
     Output("reviews-table", "data"),
     Output("reviews-table", "columns"),
     Output("restaurant-url", "children"),
     Output("monthly-reviews-graph", "figure"),
     Output("month-filter", "options"),
     Output("compound-score", "children"),
     Output("avg-rating", "children"),
     Output("total-reviews", "children"),
     Output("monthly-sentiment-line-chart", "figure")],
    [Input("file-dropdown", "value"),
     Input("sentiment-filter", "value"),
     Input("month-filter", "value"),
     Input("search-bar", "value")]
)
def update_dashboard(file_name, sentiment_filter, selected_month, search_term):
    if file_name is None:
        return {}, "", [], [], "", {}, [], "", "", "", {}

    # Load data
    file_path = os.path.join("Sentiments", file_name)
    first_row = pd.read_csv(file_path, nrows=1, header=None)
    restaurant_url = first_row.iloc[0, 0]
    df = pd.read_csv(file_path, skiprows=1)

    # Convert date to datetime and create Month-Year column
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Month-Year'] = df['Date'].dt.to_period('M').astype(str)
    month_options = [{"label": month, "value": month} for month in df['Month-Year'].unique()]

    # Apply sentiment filtering based on multi-select sentiment filter
    if sentiment_filter:
        conditions = []
        if "positive" in sentiment_filter:
            conditions.append(df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) > 0))
        if "neutral" in sentiment_filter:
            conditions.append(df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) == 0))
        if "negative" in sentiment_filter:
            conditions.append(df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) < 0))
        if conditions:
            sentiment_condition = conditions[0]
            for condition in conditions[1:]:
                sentiment_condition |= condition
            filtered_df = df[sentiment_condition]
        else:
            filtered_df = df
    else:
        filtered_df = df

    # Apply month filtering based on multi-select month filter
    if selected_month:
        filtered_df = filtered_df[filtered_df['Month-Year'].isin(selected_month)]

    # Apply search filtering to match the term with reviews
    if search_term:
        search_term = search_term.lower()
        filtered_df = filtered_df[filtered_df['Review'].str.contains(search_term, case=False, na=False)]

    # Sentiment Distribution
    sentiment_counts = {
        'Positive': (filtered_df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) > 0)).sum(),
        'Neutral': (filtered_df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) == 0)).sum(),
        'Negative': (filtered_df['Sentiment'].apply(lambda x: eval(x).get('compound', 0) < 0)).sum()
    }
    fig_sentiment = px.pie(
        names=list(sentiment_counts.keys()),
        values=list(sentiment_counts.values()),
        color=list(sentiment_counts.keys()),
        color_discrete_map={'Positive': 'green', 'Neutral': 'yellow', 'Negative': 'red'},
        title="Review Sentiment Distribution"
    )

    # Monthly Sentiment Trend (Line Chart)
    monthly_sentiment_counts = filtered_df.groupby(['Month-Year']).apply(lambda x: pd.Series({
        'Positive': (x['Sentiment'].apply(lambda s: eval(s).get('compound', 0) > 0)).sum(),
        'Neutral': (x['Sentiment'].apply(lambda s: eval(s).get('compound', 0) == 0)).sum(),
        'Negative': (x['Sentiment'].apply(lambda s: eval(s).get('compound', 0) < 0)).sum()
    })).reset_index()

    fig_monthly_sentiment = px.line(
        monthly_sentiment_counts, x='Month-Year', y=['Positive', 'Neutral', 'Negative'],
        title="Monthly Sentiment Trend",
        labels={'value': 'Number of Reviews', 'variable': 'Sentiment'},
        color_discrete_map={'Positive': 'green', 'Neutral': 'yellow', 'Negative': 'red'}
    )

    # Reviews per Rating
    rating_counts = filtered_df['Rating'].value_counts().reset_index(name='Review Count')
    rating_counts.columns = ['Rating', 'Review Count']
    fig_reviews_per_rating = px.bar(
        rating_counts, x='Rating', y='Review Count',
        title="Reviews per Rating", color='Review Count', color_discrete_sequence=['yellow']
    )

    # Word Cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(
        ' '.join(filtered_df['Review'].dropna()))
    buffer = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Reviews Table
    reviews_data = [{"Review": row['Review'],
                     "Category": "Positive" if eval(row['Sentiment']).get('compound', 0) > 0 else "Neutral" if eval(
                         row['Sentiment']).get('compound', 0) == 0 else "Negative"} for _, row in
                    filtered_df.iterrows()]
    columns = [{"name": "Review", "id": "Review"}, {"name": "Category", "id": "Category"}]

    # URL link
    restaurant_url_link = html.A("Click to go to restaurant's page", href=restaurant_url, target="_blank")

    # Key Metrics
    compound_score = filtered_df['Sentiment'].apply(lambda x: eval(x).get('compound', 0)).mean().round(3)
    avg_rating = df['Rating'].mean().round(2) if 'Rating' in df.columns else "N/A"
    total_reviews = len(filtered_df)

    # Monthly Reviews
    if not filtered_df.empty:
        monthly_reviews_count = filtered_df.groupby('Month-Year').size().reset_index(name='Review Count')
        fig_monthly_reviews = px.bar(monthly_reviews_count, x='Month-Year', y='Review Count',
                                     title="Monthly Review Count")
    else:
        fig_monthly_reviews = {}

    return fig_sentiment, f"data:image/png;base64,{image_base64}", reviews_data, columns, restaurant_url_link, fig_monthly_reviews, month_options, compound_score, avg_rating, total_reviews, fig_monthly_sentiment


# Flask route
@server.route('/')
def index():
    return render_template("index.html")


# Run Flask server
if __name__ == '__main__':
    server.run(debug=True)
