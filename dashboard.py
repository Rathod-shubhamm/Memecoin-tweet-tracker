"""
Dashboard for visualizing memecoin tweet data and insights.
Provides an interactive web interface using Dash by Plotly.
"""

import logging
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Global variables for API configuration
API_BASE_URL = None

def create_layout():
    """Create the layout for the dashboard."""
    return html.Div([
        # Header
        html.Div([
            html.H1("Memecoin Tweet Tracker", className="dashboard-title"),
            html.P("Track and analyze memecoin-related tweets from influential personalities", 
                  style={'textAlign': 'center', 'color': '#666', 'marginTop': '-20px'})
        ], className="header"),
        
        # Main Content
        html.Div([
            # Left Sidebar - Filters
            html.Div([
                html.Div([
                    html.H3("Filters", style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id='date-range',
                            start_date=(datetime.now() - timedelta(days=7)).date(),
                            end_date=datetime.now().date(),
                            display_format='YYYY-MM-DD',
                            style={'marginBottom': '20px'}
                        ),
                        
                        html.Label("Celebrities"),
                        dcc.Dropdown(
                            id='celebrity-dropdown',
                            options=[],
                            multi=True,
                            placeholder="Select celebrities",
                            style={'marginBottom': '20px'}
                        ),
                        
                        html.Label("Keywords"),
                        dcc.Dropdown(
                            id='keyword-dropdown',
                            options=[],
                            multi=True,
                            placeholder="Select keywords",
                            style={'marginBottom': '20px'}
                        ),
                        
                        html.Button(
                            "Apply Filters",
                            id="apply-filters",
                            className="filter-button",
                            style={'width': '100%'}
                        )
                    ], style={'padding': '20px'})
                ], className="filter-panel")
            ], className="sidebar"),
            
            # Main Content Area
            html.Div([
                # Top Row - Tweet Activity
                html.Div([
                    html.Div([
                        html.H3("Tweet Activity Over Time"),
                        dcc.Graph(id='tweet-activity-chart')
                    ], className="chart-container")
                ], className="top-row"),
                
                # Middle Row - Trends and Sentiment
                html.Div([
                    html.Div([
                        html.H3("Trending Memecoins"),
                        dcc.Graph(id='trending-coins-chart')
                    ], className="chart-container"),
                    
                    html.Div([
                        html.H3("Sentiment Analysis"),
                        dcc.Graph(id='sentiment-chart')
                    ], className="chart-container")
                ], className="middle-row"),
                
                # Bottom Row - Recent Tweets
                html.Div([
                    html.Div([
                        html.H3("Recent Tweets"),
                        dash_table.DataTable(
                            id='tweet-table',
                            columns=[
                                {"name": "Time", "id": "created_at", "type": "datetime"},
                                {"name": "Celebrity", "id": "username"},
                                {"name": "Tweet", "id": "text"},
                                {"name": "Coins Mentioned", "id": "coins_mentioned"},
                                {"name": "Sentiment", "id": "sentiment"}
                            ],
                            page_size=10,
                            style_table={
                                'overflowX': 'auto',
                                'borderRadius': '10px',
                                'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                            },
                            style_cell={
                                'textAlign': 'left',
                                'padding': '12px',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'backgroundColor': 'white'
                            },
                            style_header={
                                'backgroundColor': '#2c3e50',
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'left',
                                'padding': '12px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{sentiment} = "positive"'},
                                    'backgroundColor': 'rgba(46, 204, 113, 0.1)'
                                },
                                {
                                    'if': {'filter_query': '{sentiment} = "negative"'},
                                    'backgroundColor': 'rgba(231, 76, 60, 0.1)'
                                }
                            ]
                        )
                    ], className="chart-container")
                ], className="bottom-row")
            ], className="main-content")
        ], className="dashboard-container")
    ], className="app-container")

def fetch_from_api(endpoint, params=None):
    """Helper function to fetch data from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching from API {endpoint}: {e}")
        return None

# Initialize callbacks
def init_callbacks(app):
    """Initialize all the callbacks for the dashboard."""
    
    @app.callback(
        [Output('celebrity-dropdown', 'options'),
         Output('keyword-dropdown', 'options')],
        [Input('date-range', 'start_date')]  # Trigger on page load
    )
    def populate_dropdowns(start_date):
        """Populate the dropdown options with data from the API."""
        try:
            celebrities = fetch_from_api('/api/celebrities')
            celebrity_options = [{"label": celeb["name"], "value": celeb["username"]} for celeb in celebrities]
            
            keywords = fetch_from_api('/api/keywords')
            keyword_options = [{"label": kw, "value": kw} for kw in keywords]
            
            return celebrity_options, keyword_options
        except Exception as e:
            logger.error(f"Error in populate_dropdowns: {e}")
            return [], []
    
    @app.callback(
        [Output('tweet-activity-chart', 'figure'),
         Output('trending-coins-chart', 'figure'),
         Output('sentiment-chart', 'figure'),
         Output('tweet-table', 'data')],
        [Input('apply-filters', 'n_clicks')],
        [dash.dependencies.State('date-range', 'start_date'),
         dash.dependencies.State('date-range', 'end_date'),
         dash.dependencies.State('celebrity-dropdown', 'value'),
         dash.dependencies.State('keyword-dropdown', 'value')]
    )
    def update_dashboard(n_clicks, start_date, end_date, celebrities, keywords):
        """Update all dashboard components based on the selected filters."""
        try:
            # Get filtered data from API
            params = {
                'start_date': start_date,
                'end_date': end_date
            }
            if celebrities:
                params['celebrities'] = celebrities
            if keywords:
                params['keywords'] = keywords
                
            tweets = fetch_from_api('/api/tweets', params)
            if not tweets:
                empty_fig = px.line(title="No data available for the selected filters")
                empty_table = []
                return empty_fig, empty_fig, empty_fig, empty_table
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(tweets)
            
            # Process data for charts
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
            
            # Tweet Activity Chart
            tweet_counts = df.groupby('date').size().reset_index(name='count')
            activity_fig = px.line(
                tweet_counts, 
                x='date', 
                y='count', 
                title='Tweet Activity Over Time',
                labels={'date': 'Date', 'count': 'Number of Tweets'},
                template='plotly_white'
            )
            activity_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50'),
                title_font=dict(size=20),
                margin=dict(t=40, l=40, r=40, b=40)
            )
            activity_fig.update_traces(
                line=dict(color='#3498db', width=3),
                marker=dict(size=8)
            )
            
            # Trending Coins Chart
            trends = fetch_from_api('/api/trends', params)
            trending_fig = px.bar(
                trends,
                x='coin',
                y='mention_count',
                title='Trending Memecoins by Mention Count',
                labels={'coin': 'Memecoin', 'mention_count': 'Number of Mentions'},
                template='plotly_white'
            )
            trending_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50'),
                title_font=dict(size=20),
                margin=dict(t=40, l=40, r=40, b=40)
            )
            trending_fig.update_traces(
                marker_color='#3498db',
                marker_line_color='#2980b9',
                marker_line_width=1.5,
                opacity=0.8
            )
            
            # Sentiment Analysis Chart
            sentiment_data = df.groupby('sentiment').size().reset_index(name='count')
            sentiment_fig = px.pie(
                sentiment_data,
                values='count',
                names='sentiment',
                title='Tweet Sentiment Distribution',
                color='sentiment',
                color_discrete_map={
                    'positive': '#2ecc71',
                    'neutral': '#95a5a6',
                    'negative': '#e74c3c'
                },
                template='plotly_white'
            )
            sentiment_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50'),
                title_font=dict(size=20),
                margin=dict(t=40, l=40, r=40, b=40),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Recent Tweets Table
            recent_tweets = df.sort_values('created_at', ascending=False).head(10).to_dict('records')
            
            return activity_fig, trending_fig, sentiment_fig, recent_tweets
            
        except Exception as e:
            logger.error(f"Error in update_dashboard: {e}")
            empty_fig = px.line(title=f"Error loading data: {str(e)}")
            return empty_fig, empty_fig, empty_fig, []

def start_dashboard(config):
    """Initialize and start the dashboard server."""
    global API_BASE_URL
    
    # Set API base URL
    API_BASE_URL = f"http://{config.get('api_host', 'localhost')}:{config.get('api_port', 5001)}"
    
    # Set up the app layout
    app.layout = create_layout()
    
    # Initialize callbacks
    init_callbacks(app)
    
    # Start the Dash server
    port = config.get('port', 8050)
    host = config.get('host', '0.0.0.0')
    debug = config.get('debug', False)
    
    logger.info(f"Starting Dashboard server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # This block allows for testing the dashboard directly
    from config import load_config
    
    config = load_config()
    start_dashboard(config["dashboard"])