from flask import Flask, render_template
from dash import Dash, dcc, html
import dash
import plotly.express as px
import pandas as pd
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Initialize Flask server
server = Flask(__name__)

# Initialize Dash app
app_dash = Dash(__name__, server=server, url_base_pathname='/dash/')

# Dash Layout
app_dash.layout = html.Div([
    html.H1("Sentiment Analysis Dashboard"),
    dcc.Dropdown(
        id="file-dropdown",
        options=[
            {"label": file, "value": file} for file in os.listdir("Sentiments") if file.endswith('_sentiment.csv')
        ],
        placeholder="Select a CSV File",
    ),
    dcc.Graph(id="sentiment-bar-graph"),
    html.Img(id="wordcloud-image", style={'width': '50%', 'margin': 'auto'})
])


@app_dash.callback(
    [dash.dependencies.Output("sentiment-bar-graph", "figure"),
     dash.dependencies.Output("wordcloud-image", "src")],
    [dash.dependencies.Input("file-dropdown", "value")]
)
def update_dashboard(file_name):
    if file_name is None:
        return {}, ""

    # Load sentiment CSV data
    file_path = os.path.join("Sentiments", file_name)
    df = pd.read_csv(file_path)

    # Create sentiment bar chart
    sentiment_labels = ['Negative', 'Neutral', 'Positive', 'Compound']
    sentiment_values = [
        df['Sentiment'].apply(lambda x: eval(x)['neg']).mean(),
        df['Sentiment'].apply(lambda x: eval(x)['neu']).mean(),
        df['Sentiment'].apply(lambda x: eval(x)['pos']).mean(),
        df['Sentiment'].apply(lambda x: eval(x)['compound']).mean(),
    ]

    fig = px.bar(
        x=sentiment_labels,
        y=sentiment_values,
        labels={"x": "Sentiment", "y": "Average Score"},
        title=f"Aggregated Sentiment for {file_name.split('_sentiment')[0]}"
    )

    # Generate word cloud
    reviews = df['Review'].dropna().tolist()
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(reviews))

    # Convert the wordcloud to a base64 image for embedding
    buffer = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Return the figure and the image in base64 format
    return fig, f"data:image/png;base64,{image_base64}"


# Flask route
@server.route('/')
def index():
    return render_template("index.html")


# Run the Flask server
if __name__ == '__main__':
    server.run(debug=True)
