import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import os

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Function to load sentiment CSV
def load_sentiment(file):
    df = pd.read_csv('Sentiments/' + file, skiprows=1)
    return df

# List available sentiment CSV files
sentiment_files = [f for f in os.listdir('Sentiments') if f.endswith('.csv')]

# App Layout
app.layout = dbc.Container([
    html.H1("Restaurant Sentiment Comparison Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select First Restaurant File:"),
            dcc.Dropdown(
                id='file1',
                options=[{'label': f, 'value': f} for f in sentiment_files],
                value=None,
                placeholder="Select a file..."
            )
        ], width=6),
        dbc.Col([
            html.Label("Select Second Restaurant File:"),
            dcc.Dropdown(
                id='file2',
                options=[{'label': f, 'value': f} for f in sentiment_files],
                value=None,
                placeholder="Select a file..."
            )
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.H4("Metrics", className="text-center"),
            html.Div(id='metrics1', className="border p-3 rounded bg-light")
        ], width=6),
        dbc.Col([
            html.H4("Metrics", className="text-center"),
            html.Div(id='metrics2', className="border p-3 rounded bg-light")
        ], width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='ratings1')], width=6),
        dbc.Col([dcc.Graph(id='ratings2')], width=6),
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='sentiments1')], width=6),
        dbc.Col([dcc.Graph(id='sentiments2')], width=6),
    ]),

    dbc.Row([
        dbc.Col([dcc.Graph(id='wordcloud1')], width=6),
        dbc.Col([dcc.Graph(id='wordcloud2')], width=6),
    ])
], fluid=True)

# Update graphs and metrics
@app.callback(
    Output('metrics1', 'children'),
    Output('metrics2', 'children'),
    Output('ratings1', 'figure'),
    Output('ratings2', 'figure'),
    Output('sentiments1', 'figure'),
    Output('sentiments2', 'figure'),
    Output('wordcloud1', 'figure'),
    Output('wordcloud2', 'figure'),
    Input('file1', 'value'),
    Input('file2', 'value')
)
def update_comparison(file1, file2):
    import plotly.graph_objects as go
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    empty_fig = go.Figure()
    empty_fig.update_layout(template=None, xaxis={'visible': False}, yaxis={'visible': False})

    if not file1 or not file2:
        return "", "", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    df1 = load_sentiment(file1)
    df2 = load_sentiment(file2)

    # Process Sentiments
    df1['Compound'] = df1['Sentiment'].apply(lambda x: eval(x)['compound'])
    df2['Compound'] = df2['Sentiment'].apply(lambda x: eval(x)['compound'])

    df1['Sentiment_Label'] = df1['Compound'].apply(
        lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))
    df2['Sentiment_Label'] = df2['Compound'].apply(
        lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))

    # Metrics Calculation
    metrics1_data = {
        'Average Rating': round(df1['Rating'].mean(), 2),
        'Total Reviews': len(df1),
        '% Positive Reviews': round((df1['Sentiment_Label'] == 'Positive').mean() * 100, 2),
        '% Neutral Reviews': round((df1['Sentiment_Label'] == 'Neutral').mean() * 100, 2),
        '% Negative Reviews': round((df1['Sentiment_Label'] == 'Negative').mean() * 100, 2),
        'Avg Review Length': round(df1['Review'].dropna().apply(lambda x: len(x.split())).mean(), 2)
    }

    metrics2_data = {
        'Average Rating': round(df2['Rating'].mean(), 2),
        'Total Reviews': len(df2),
        '% Positive Reviews': round((df2['Sentiment_Label'] == 'Positive').mean() * 100, 2),
        '% Neutral Reviews': round((df2['Sentiment_Label'] == 'Neutral').mean() * 100, 2),
        '% Negative Reviews': round((df2['Sentiment_Label'] == 'Negative').mean() * 100, 2),
        'Avg Review Length': round(df2['Review'].dropna().apply(lambda x: len(x.split())).mean(), 2)
    }

    def create_metric_cards(metrics):
        return dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H6(metric, className="card-title"),
                html.P(f"{value}", className="card-text")
            ]), className="mb-2"), width=6) for metric, value in metrics.items()
        ])

    metrics_card1 = create_metric_cards(metrics1_data)
    metrics_card2 = create_metric_cards(metrics2_data)

    # Ratings Histogram
    fig_ratings1 = px.histogram(df1, x='Rating', nbins=5, title='Rating Distribution')
    fig_ratings2 = px.histogram(df2, x='Rating', nbins=5, title='Rating Distribution')

    # Sentiment Pie Chart (Colored)
    fig_sentiments1 = px.pie(df1, names='Sentiment_Label', title='Sentiment Distribution',
                             color='Sentiment_Label',
                             color_discrete_map={'Positive': 'green', 'Neutral': 'gold', 'Negative': 'red'})
    fig_sentiments2 = px.pie(df2, names='Sentiment_Label', title='Sentiment Distribution',
                             color='Sentiment_Label',
                             color_discrete_map={'Positive': 'green', 'Neutral': 'gold', 'Negative': 'red'})

    # Word Clouds
    def create_wordcloud(df):
        text = ' '.join(df['Review'].dropna().astype(str))
        wordcloud = WordCloud(width=400, height=300, background_color='white').generate(text)
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        encoded = base64.b64encode(buf.getbuffer()).decode("utf8")
        return f"data:image/png;base64,{encoded}"

    img1 = create_wordcloud(df1)
    img2 = create_wordcloud(df2)

    fig_wordcloud1 = px.imshow([[]])
    fig_wordcloud1.update_layout(
        images=[dict(source=img1, x=0, y=1, sizex=1, sizey=1, xref="paper", yref="paper", opacity=1, layer="below")],
        xaxis_visible=False, yaxis_visible=False
    )

    fig_wordcloud2 = px.imshow([[]])
    fig_wordcloud2.update_layout(
        images=[dict(source=img2, x=0, y=1, sizex=1, sizey=1, xref="paper", yref="paper", opacity=1, layer="below")],
        xaxis_visible=False, yaxis_visible=False
    )

    return metrics_card1, metrics_card2, fig_ratings1, fig_ratings2, fig_sentiments1, fig_sentiments2, fig_wordcloud1, fig_wordcloud2


if __name__ == '__main__':
    app.run(debug=True)
