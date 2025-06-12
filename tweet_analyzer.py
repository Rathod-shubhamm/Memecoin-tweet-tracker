"""
Tweet Analyzer module for processing and analyzing tweets related to memecoins.
"""

import logging
import re
from textblob import TextBlob
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TweetAnalyzer:
    """Class for analyzing tweets and extracting memecoin-related information."""
    
    def __init__(self):
        """Initialize the TweetAnalyzer."""
        self.memecoin_patterns = {
            'DOGE': r'\b(dogecoin|doge coin|\$doge)\b',
            'SHIB': r'\b(shiba|shib|\$shib)\b',
            'PEPE': r'\b(pepe coin|\$pepe)\b',
            # Add more patterns as needed
        }
    
    def analyze_tweet(self, tweet_text: str) -> Dict[str, Any]:
        """
        Analyze a tweet and extract relevant information.
        
        Args:
            tweet_text (str): The text content of the tweet
            
        Returns:
            Dict[str, Any]: Dictionary containing analysis results
        """
        try:
            # Initialize analysis results
            analysis = {
                'coins_mentioned': [],
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'is_crypto_related': False
            }
            
            # Check for memecoin mentions
            for coin, pattern in self.memecoin_patterns.items():
                if re.search(pattern, tweet_text.lower()):
                    analysis['coins_mentioned'].append(coin)
                    analysis['is_crypto_related'] = True
            
            # Perform sentiment analysis
            blob = TextBlob(tweet_text)
            sentiment_score = blob.sentiment.polarity
            
            # Categorize sentiment
            if sentiment_score > 0.1:
                analysis['sentiment'] = 'positive'
            elif sentiment_score < -0.1:
                analysis['sentiment'] = 'negative'
            else:
                analysis['sentiment'] = 'neutral'
            
            analysis['sentiment_score'] = sentiment_score
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing tweet: {e}")
            return {
                'coins_mentioned': [],
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'is_crypto_related': False
            }
    
    def extract_hashtags(self, tweet_text: str) -> List[str]:
        """
        Extract hashtags from tweet text.
        
        Args:
            tweet_text (str): The text content of the tweet
            
        Returns:
            List[str]: List of hashtags found in the tweet
        """
        try:
            hashtags = re.findall(r'#(\w+)', tweet_text)
            return [tag.lower() for tag in hashtags]
        except Exception as e:
            logger.error(f"Error extracting hashtags: {e}")
            return []
    
    def is_crypto_related(self, tweet_text: str) -> bool:
        """
        Check if a tweet is related to cryptocurrency.
        
        Args:
            tweet_text (str): The text content of the tweet
            
        Returns:
            bool: True if the tweet is crypto-related, False otherwise
        """
        try:
            crypto_terms = [
                'crypto', 'token', 'memecoin', 'coin', 'moon', 'hodl',
                'blockchain', 'bitcoin', 'ethereum', 'altcoin'
            ]
            
            # Check for crypto terms
            text_lower = tweet_text.lower()
            if any(term in text_lower for term in crypto_terms):
                return True
            
            # Check for memecoin mentions
            if any(re.search(pattern, text_lower) for pattern in self.memecoin_patterns.values()):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking crypto relation: {e}")
            return False 