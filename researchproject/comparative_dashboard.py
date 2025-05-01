import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
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
        dbc.Col(html.Div(id='metric_comparison'), width=9),
        dbc.Col(html.Div(id='winner_card'), width=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='ratings1')], width=4),
        dbc.Col([dcc.Graph(id='ratings2')], width=4),
        dbc.Col([dcc.Graph(id='ratings_diff')], width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='sentiments1')], width=4),
        dbc.Col([dcc.Graph(id='sentiments2')], width=4),
        dbc.Col([dcc.Graph(id='sentiments_diff')], width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([dcc.Graph(id='wordcloud1')], width=6),
        dbc.Col([dcc.Graph(id='wordcloud2')], width=6),
    ])
], fluid=True)

# Helper functions
def create_metric_table(metrics1, metrics2):
    winning_keys = ['Average Rating', 'Total Reviews', '% Positive Reviews']  # Keys used in winner logic
    rows = []

    for key in metrics1.keys():
        if key in winning_keys:
            if metrics1[key] > metrics2[key]:
                better = '1 ⬆️'
            elif metrics2[key] > metrics1[key]:
                better = '2 ⬆️'
            else:
                better = '-'
        else:
            better = 'N/A'
        rows.append(html.Tr([html.Td(key), html.Td(metrics1[key]), html.Td(metrics2[key]), html.Td(better)]))

    table = dbc.Table([
        html.Thead(html.Tr([html.Th("Metric"), html.Th("Restaurant 1"), html.Th("Restaurant 2"), html.Th("Better")])),
        html.Tbody(rows)
    ], bordered=True, striped=True, hover=True)

    return table



def create_winner_card(metrics1, metrics2):
    # Only include these metrics in winner logic
    winning_keys = ['Average Rating', 'Total Reviews', '% Positive Reviews']

    score1 = 0
    score2 = 0
    for key in winning_keys:
        if metrics1[key] > metrics2[key]:
            score1 += 1
        elif metrics2[key] > metrics1[key]:
            score2 += 1
    winner = "Restaurant 1" if score1 > score2 else ("Restaurant 2" if score2 > score1 else "Tie")
    card = dbc.Card([
        dbc.CardBody([
            html.H4("Overall Winner", className="card-title"),
            html.P(winner, className="card-text")
        ])
    ], color="success" if winner != "Tie" else "secondary", inverse=True)
    return card


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


# Callback for updates
@app.callback(
    Output('metric_comparison', 'children'),
    Output('winner_card', 'children'),
    Output('ratings1', 'figure'),
    Output('ratings2', 'figure'),
    Output('ratings_diff', 'figure'),
    Output('sentiments1', 'figure'),
    Output('sentiments2', 'figure'),
    Output('sentiments_diff', 'figure'),
    Output('wordcloud1', 'figure'),
    Output('wordcloud2', 'figure'),
    Input('file1', 'value'),
    Input('file2', 'value')
)
def update_comparison(file1, file2):
    empty_fig = go.Figure()
    empty_fig.update_layout(template=None, xaxis={'visible': False}, yaxis={'visible': False})

    if not file1 or not file2:
        return "", "", empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    df1 = load_sentiment(file1)
    df2 = load_sentiment(file2)

    # Process Sentiments
    df1['Compound'] = df1['Sentiment'].apply(lambda x: eval(x)['compound'])
    df2['Compound'] = df2['Sentiment'].apply(lambda x: eval(x)['compound'])

    df1['Sentiment_Label'] = df1['Compound'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))
    df2['Sentiment_Label'] = df2['Compound'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))

    # Metrics Calculation
    metrics1 = {
        'Average Rating': round(df1['Rating'].mean(), 2),
        'Total Reviews': len(df1),
        '% Positive Reviews': round((df1['Sentiment_Label'] == 'Positive').mean() * 100, 2),
        '% Neutral Reviews': round((df1['Sentiment_Label'] == 'Neutral').mean() * 100, 2),
        '% Negative Reviews': round((df1['Sentiment_Label'] == 'Negative').mean() * 100, 2),
        'Avg Review Length': round(df1['Review'].dropna().apply(lambda x: len(x.split())).mean(), 2)
    }

    metrics2 = {
        'Average Rating': round(df2['Rating'].mean(), 2),
        'Total Reviews': len(df2),
        '% Positive Reviews': round((df2['Sentiment_Label'] == 'Positive').mean() * 100, 2),
        '% Neutral Reviews': round((df2['Sentiment_Label'] == 'Neutral').mean() * 100, 2),
        '% Negative Reviews': round((df2['Sentiment_Label'] == 'Negative').mean() * 100, 2),
        'Avg Review Length': round(df2['Review'].dropna().apply(lambda x: len(x.split())).mean(), 2)
    }

    metric_table = create_metric_table(metrics1, metrics2)
    winner_card = create_winner_card(metrics1, metrics2)

    # Rating Histograms
    fig_ratings1 = px.histogram(df1, x='Rating', nbins=5, title='Rating Distribution - Restaurant 1')
    fig_ratings2 = px.histogram(df2, x='Rating', nbins=5, title='Rating Distribution - Restaurant 2')

    ratings_diff = (df1['Rating'].value_counts().sort_index() - df2['Rating'].value_counts().sort_index()).fillna(0)
    fig_ratings_diff = px.bar(x=ratings_diff.index, y=ratings_diff.values, title='Rating Difference (1 vs 2)')

    # Sentiment Pie Charts
    fig_sentiments1 = px.pie(df1, names='Sentiment_Label', title='Sentiment Distribution - Restaurant 1',
                             color='Sentiment_Label', color_discrete_map={'Positive': 'green', 'Neutral': 'gold', 'Negative': 'red'})
    fig_sentiments2 = px.pie(df2, names='Sentiment_Label', title='Sentiment Distribution - Restaurant 2',
                             color='Sentiment_Label', color_discrete_map={'Positive': 'green', 'Neutral': 'gold', 'Negative': 'red'})

    sentiments_diff = (df1['Sentiment_Label'].value_counts(normalize=True) - df2['Sentiment_Label'].value_counts(normalize=True)).fillna(0) * 100
    fig_sentiments_diff = px.bar(x=sentiments_diff.index, y=sentiments_diff.values, title='Sentiment % Difference (1 vs 2)',
                                 color=sentiments_diff.index, color_discrete_map={'Positive': 'green', 'Neutral': 'gold', 'Negative': 'red'})

    # Wordclouds
    img1 = create_wordcloud(df1)
    img2 = create_wordcloud(df2)

    fig_wordcloud1 = px.imshow([[]])
    fig_wordcloud1.update_layout(images=[dict(source=img1, x=0, y=1, sizex=1, sizey=1, xref="paper", yref="paper")], xaxis_visible=False, yaxis_visible=False)

    fig_wordcloud2 = px.imshow([[]])
    fig_wordcloud2.update_layout(images=[dict(source=img2, x=0, y=1, sizex=1, sizey=1, xref="paper", yref="paper")], xaxis_visible=False, yaxis_visible=False)

    return metric_table, winner_card, fig_ratings1, fig_ratings2, fig_ratings_diff, fig_sentiments1, fig_sentiments2, fig_sentiments_diff, fig_wordcloud1, fig_wordcloud2


if __name__ == '__main__':
    app.run(debug=True)
