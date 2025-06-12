"""
Data processor for the Memecoin Tweet Tracker.
Aggregates and analyzes tweet data to extract trends and insights.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processes tweet data to extract trends, statistics, and insights.
    Performs historical analysis and aggregation of memecoin tweet data.
    """
    
    def __init__(self, db_handler):
        """
        Initialize the data processor with database connection.
        
        Args:
            db_handler: DatabaseHandler instance for data access
        """
        self.db = db_handler
        logger.info("Data processor initialized")
    
    def process_recent_data(self, hours=24):
        """
        Process recent tweet data to update trends and statistics.
        This method is called periodically from the main loop.
        
        Args:
            hours (int): Number of hours of data to process
        """
        try:
            logger.info(f"Processing data from the last {hours} hours")
            
            # Get recent tweets
            start_time = datetime.now() - timedelta(hours=hours)
            tweets = self.db.get_tweets(start_date=start_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            if not tweets:
                logger.info("No recent tweets to process")
                return
            
            # Update trend data in database
            self._update_trends(tweets)
            
            # Update statistics in database
            self._update_statistics(tweets)
            
            logger.info(f"Processed {len(tweets)} recent tweets")
        except Exception as e:
            logger.error(f"Error in process_recent_data: {e}")
    
    def _update_trends(self, tweets):
        """
        Update trend data based on recent tweets.
        
        Args:
            tweets (list): List of tweet dictionaries
        """
        try:
            # Extract all coin mentions
            all_coins = []
            for tweet in tweets:
                coins = tweet.get("coins_mentioned", [])
                if isinstance(coins, str):
                    # Handle case where coins might be stored as comma-separated string
                    coins = [coin.strip() for coin in coins.split(",")]
                all_coins.extend(coins)
            
            # Count mentions for each coin
            coin_counts = Counter(all_coins)
            
            # Store in database
            for coin, count in coin_counts.items():
                self.db.update_coin_trend(
                    coin=coin,
                    mention_count=count,
                    timestamp=datetime.now()
                )
        except Exception as e:
            logger.error(f"Error in _update_trends: {e}")
    
    def _update_statistics(self, tweets):
        """
        Update tweet statistics based on recent tweet data.
        
        Args:
            tweets (list): List of tweet dictionaries
        """
        try:
            # Convert to pandas DataFrame for easier analysis
            df = pd.DataFrame(tweets)
            
            if df.empty:
                return
            
            # Calculate statistics
            total_tweets = len(df)
            
            # Sentiment distribution
            sentiment_counts = df['sentiment'].value_counts().to_dict()
            
            # Tweets per celebrity
            celebrity_counts = df['username'].value_counts().to_dict()
            
            # Most mentioned coins
            all_coins = []
            for coins in df['coins_mentioned']:
                if isinstance(coins, list):
                    all_coins.extend(coins)
                elif isinstance(coins, str):
                    all_coins.extend([coin.strip() for coin in coins.split(",")])
            
            top_coins = Counter(all_coins).most_common(10)
            
            # Store statistics in database
            stats = {
                'timestamp': datetime.now(),
                'total_tweets': total_tweets,
                'sentiment_distribution': sentiment_counts,
                'tweets_by_celebrity': celebrity_counts,
                'top_coins': dict(top_coins)
            }
            
            self.db.update_statistics(stats)
            
        except Exception as e:
            logger.error(f"Error in _update_statistics: {e}")
    
    def get_trends(self, timeframe='day', start_date=None, end_date=None):
        """
        Get trending memecoins for the specified timeframe.
        
        Args:
            timeframe (str): Time period to analyze ('day', 'week', 'month', 'custom')
            start_date (str, optional): Start date for custom timeframe
            end_date (str, optional): End date for custom timeframe
            
        Returns:
            list: List of trending coins with metrics
        """
        try:
            # Determine date range based on timeframe
            if timeframe == 'custom' and start_date and end_date:
                # Use custom date range
                pass
            elif timeframe == 'day':
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            elif timeframe == 'week':
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            elif timeframe == 'month':
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            else:
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get trend data from database
            trends = self.db.get_coin_trends(start_date=start_date, end_date=end_date)
            
            if not trends:
                return []
            
            # Aggregate by coin
            coin_data = {}
            for trend in trends:
                coin = trend.get('coin')
                if coin not in coin_data:
                    coin_data[coin] = {
                        'coin': coin,
                        'mention_count': 0,
                        'sentiment_score': 0,
                        'celebrity_mentions': 0
                    }
                
                coin_data[coin]['mention_count'] += trend.get('mention_count', 0)
                coin_data[coin]['sentiment_score'] += trend.get('sentiment_score', 0)
                coin_data[coin]['celebrity_mentions'] += trend.get('celebrity_mentions', 0)
            
            # Convert to list and sort by mention count
            result = list(coin_data.values())
            result.sort(key=lambda x: x['mention_count'], reverse=True)
            
            # Take top 20
            return result[:20]
        
        except Exception as e:
            logger.error(f"Error in get_trends: {e}")
            return []
    
    def get_statistics(self, timeframe='day'):
        """
        Get aggregated statistics for the specified timeframe.
        
        Args:
            timeframe (str): Time period for statistics ('day', 'week', 'month')
            
        Returns:
            dict: Dictionary containing various statistics
        """
        try:
            # Determine date range based on timeframe
            if timeframe == 'day':
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            elif timeframe == 'week':
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            elif timeframe == 'month':
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            else:
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Get statistics from database
            all_stats = self.db.get_statistics(start_date=start_date)
            
            if not all_stats:
                return {
                    'total_tweets': 0,
                    'sentiment_distribution': {},
                    'tweets_by_celebrity': {},
                    'top_coins': {}
                }
            
            # Aggregate statistics
            total_tweets = sum(stat.get('total_tweets', 0) for stat in all_stats)
            
            # Merge sentiment distributions
            sentiment_distribution = {}
            for stat in all_stats:
                for sentiment, count in stat.get('sentiment_distribution', {}).items():
                    sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + count
            
            # Merge celebrity counts
            tweets_by_celebrity = {}
            for stat in all_stats:
                for celebrity, count in stat.get('tweets_by_celebrity', {}).items():
                    tweets_by_celebrity[celebrity] = tweets_by_celebrity.get(celebrity, 0) + count
            
            # Merge coin counts
            top_coins = {}
            for stat in all_stats:
                for coin, count in stat.get('top_coins', {}).items():
                    top_coins[coin] = top_coins.get(coin, 0) + count
            
            # Sort and limit
            tweets_by_celebrity = dict(sorted(tweets_by_celebrity.items(), key=lambda x: x[1], reverse=True)[:10])
            top_coins = dict(sorted(top_coins.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                'total_tweets': total_tweets,
                'sentiment_distribution': sentiment_distribution,
                'tweets_by_celebrity': tweets_by_celebrity,
                'top_coins': top_coins
            }
            
        except Exception as e:
            logger.error(f"Error in get_statistics: {e}")
            return {
                'total_tweets': 0,
                'sentiment_distribution': {},
                'tweets_by_celebrity': {},
                'top_coins': {}
            }
    
    def analyze_coin_performance(self, coin, timeframe='week'):
        """
        Analyze performance and metrics for a specific coin.
        
        Args:
            coin (str): Coin symbol or name to analyze
            timeframe (str): Time period for analysis ('day', 'week', 'month')
            
        Returns:
            dict: Dictionary with performance metrics
        """
        try:
            # Determine date range
            if timeframe == 'day':
                start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            elif timeframe == 'week':
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            elif timeframe == 'month':
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            else:
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                
            # Get tweets mentioning this coin
            tweets = self.db.get_tweets(keyword=coin, start_date=start_date)
            
            if not tweets:
                return {
                    'coin': coin,
                    'total_mentions': 0,
                    'sentiment_breakdown': {},
                    'top_influencers': {},
                    'mention_trend': []
                }
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(tweets)
            
            # Calculate metrics
            total_mentions = len(df)
            
            # Sentiment breakdown
            sentiment_breakdown = df['sentiment'].value_counts().to_dict()
            
            # Top influencers mentioning this coin
            top_influencers = df['username'].value_counts().to_dict()
            top_influencers = dict(sorted(top_influencers.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Daily mention trend
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            mention_trend = df.groupby('date').size().reset_index()
            mention_trend.columns = ['date', 'count']
            mention_trend = mention_trend.to_dict('records')
            
            return {
                'coin': coin,
                'total_mentions': total_mentions,
                'sentiment_breakdown': sentiment_breakdown,
                'top_influencers': top_influencers,
                'mention_trend': mention_trend
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_coin_performance: {e}")
            return {
                'coin': coin,
                'total_mentions': 0,
                'sentiment_breakdown': {},
                'top_influencers': {},
                'mention_trend': []
            }