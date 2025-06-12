"""
Tweet Dataset Processor for the Memecoin Tweet Tracker.
Processes and analyzes tweets from a dataset instead of real-time streaming.
"""

import logging
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Generator
from pathlib import Path
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

class TweetProcessor:
    def __init__(self, config: Dict[str, Any], db_handler):
        """Initialize the tweet processor with configuration and database handler."""
        self.config = config
        self.db_handler = db_handler
        self.dataset_path = Path(config['dataset']['path'])
        self.batch_size = config['dataset'].get('batch_size', 1000)
        self.celebrities = self._load_celebrities()
        self.keywords = self._load_keywords()
        self.memecoin_patterns = self._load_memecoin_patterns()

    def _load_celebrities(self) -> List[str]:
        """Load list of celebrities to track from database."""
        try:
            celebrities = self.db_handler.get_celebrities()
            return [c['username'] for c in celebrities]
        except Exception as e:
            logger.error(f"Error loading celebrities: {e}")
            return []

    def _load_keywords(self) -> List[str]:
        """Load list of keywords to track from database."""
        try:
            return self.db_handler.get_keywords()
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            return []

    def _load_memecoin_patterns(self) -> List[str]:
        """Load patterns for identifying memecoins in text."""
        return [
            r'\b(DOGE|Dogecoin)\b',
            r'\b(SHIB|Shiba Inu)\b',
            r'\b(PEPE|PepeCoin)\b',
            r'\b(FLOKI|Floki Inu)\b',
            r'\b(BONK|Bonk)\b',
            r'\b(MOON|MoonCoin)\b',
            r'\b(WOJAK|Wojak)\b'
        ]

    def _process_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tweet and extract relevant information."""
        try:
            # Extract basic tweet information
            tweet_data = {
                'tweet_id': str(tweet['id']),
                'text': tweet['text'],
                'created_at': datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')),
                'author': {
                    'username': tweet['author']['username'],
                    'name': tweet['author']['name'],
                    'followers_count': tweet['author'].get('followers_count', 0)
                },
                'engagement': {
                    'likes': tweet.get('like_count', 0),
                    'retweets': tweet.get('retweet_count', 0),
                    'replies': tweet.get('reply_count', 0)
                },
                'mentions': tweet.get('mentions', []),
                'hashtags': tweet.get('hashtags', []),
                'urls': tweet.get('urls', []),
                'processed_at': datetime.utcnow()
            }

            # Add sentiment analysis
            tweet_data['sentiment'] = self._analyze_sentiment(tweet['text'])

            # Identify memecoin mentions
            tweet_data['memecoin_mentions'] = self._identify_memecoins(tweet['text'])

            return tweet_data
        except Exception as e:
            logger.error(f"Error processing tweet {tweet.get('id')}: {e}")
            return None

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of tweet text using TextBlob."""
        try:
            analysis = TextBlob(text)
            # Get polarity (-1 to 1) and convert to positive/negative/neutral
            polarity = analysis.sentiment.polarity
            
            if polarity > 0.1:
                return {'positive': 1.0, 'negative': 0.0, 'neutral': 0.0}
            elif polarity < -0.1:
                return {'positive': 0.0, 'negative': 1.0, 'neutral': 0.0}
            else:
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}

    def _identify_memecoins(self, text: str) -> List[str]:
        """Identify memecoin mentions in tweet text."""
        try:
            found_memecoins = []
            for pattern in self.memecoin_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    found_memecoins.append(match.group())
            return list(set(found_memecoins))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error identifying memecoins: {e}")
            return []

    def process_dataset(self) -> None:
        """Process the entire dataset in batches."""
        try:
            logger.info(f"Starting dataset processing from {self.dataset_path}")
            
            # Read the dataset in chunks
            for chunk in pd.read_json(self.dataset_path, lines=True, chunksize=self.batch_size):
                for _, tweet in chunk.iterrows():
                    # Convert tweet to dict and process
                    tweet_dict = tweet.to_dict()
                    processed_tweet = self._process_tweet(tweet_dict)
                    
                    if processed_tweet:
                        # Store in database
                        self.db_handler.store_tweet(processed_tweet)
                        logger.info(f"Processed tweet {processed_tweet['tweet_id']}")
            
            logger.info("Dataset processing completed")
        except Exception as e:
            logger.error(f"Error processing dataset: {e}")
            raise

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics about the dataset."""
        try:
            df = pd.read_json(self.dataset_path, lines=True)
            return {
                'total_tweets': len(df),
                'date_range': {
                    'start': df['created_at'].min(),
                    'end': df['created_at'].max()
                },
                'unique_users': df['author.username'].nunique(),
                'memecoin_mentions': sum(df['text'].str.contains('|'.join(self.memecoin_patterns), case=False))
            }
        except Exception as e:
            logger.error(f"Error getting dataset stats: {e}")
            return {}

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    from config import load_config
    config = load_config()
    
    # Initialize database handler
    from database import DatabaseHandler
    db_handler = DatabaseHandler(config["database"])
    
    # Initialize tweet processor
    processor = TweetProcessor(config, db_handler)
    
    # Process dataset
    processor.process_dataset() 