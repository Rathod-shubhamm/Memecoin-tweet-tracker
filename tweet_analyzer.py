"""
Tweet analyzer for the Memecoin Tweet Tracker.
Analyzes tweets to extract mentions of memecoins and sentiment.
"""

import logging
import re
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

logger = logging.getLogger(__name__)

class TweetAnalyzer:
    """
    Analyzes tweets to identify mentioned coins, determine sentiment,
    and calculate importance scores.
    """
    
    def __init__(self):
        """Initialize the tweet analyzer with required components."""
        # Initialize NLTK components
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.error(f"Error initializing NLTK: {e}")
            self.sentiment_analyzer = None
        
        # Load custom sentiment lexicon for crypto terms
        self.crypto_lexicon = self._load_crypto_lexicon()
        
        logger.info("Tweet analyzer initialized")
    
    def _load_crypto_lexicon(self):
        """
        Load custom sentiment lexicon for crypto-specific terms.
        
        Returns:
            dict: Dictionary of crypto terms and their sentiment scores
        """
        try:
            # This would typically load from a file, but for simplicity,
            # we'll define it directly here
            return {
                "moon": 0.8,
                "mooning": 0.8,
                "bullish": 0.6,
                "bearish": -0.6,
                "dump": -0.7,
                "pumping": 0.7,
                "scam": -0.9,
                "rugpull": -0.9,
                "gem": 0.7,
                "hodl": 0.5,
                "lambo": 0.6,
                "fomo": 0.3,
                "to the moon": 0.8,
                "going to zero": -0.8,
                "worthless": -0.9,
                "rocket": 0.7,
                "🚀": 0.7,
                "💎": 0.6,
                "🌙": 0.7,
                "💪": 0.5,
                "📉": -0.7,
                "📈": 0.7,
                "🔥": 0.6
            }
        except Exception as e:
            logger.error(f"Error loading crypto lexicon: {e}")
            return {}
    
    def analyze_tweet(self, tweet, keywords):
        """
        Analyze a tweet to extract information about mentioned coins and sentiment.
        
        Args:
            tweet (dict): Tweet data
            keywords (list): List of keywords to look for
            
        Returns:
            dict: Analysis results including mentioned coins, sentiment, etc.
        """
        try:
            text = tweet.get("text", "").lower()
            
            # Extract mentioned coins
            coins_mentioned = self._extract_coins(text, keywords)
            
            # Determine sentiment
            sentiment = self._analyze_sentiment(text)
            
            # Calculate importance score
            importance_score = self._calculate_importance(tweet, coins_mentioned, sentiment)
            
            return {
                "coins_mentioned": coins_mentioned,
                "sentiment": sentiment,
                "importance_score": importance_score
            }
        except Exception as e:
            logger.error(f"Error analyzing tweet: {e}")
            return {
                "coins_mentioned": [],
                "sentiment": "neutral",
                "importance_score": 0.0
            }
    
    def _extract_coins(self, text, keywords):
        """
        Extract mentions of coins from tweet text.
        
        Args:
            text (str): Tweet text
            keywords (list): List of keywords to look for
            
        Returns:
            list: List of mentioned coins
        """
        coins = []
        text_lower = text.lower()
        
        # Look for keyword matches
        for keyword in keywords:
            if keyword.lower() in text_lower:
                coins.append(keyword)
        
        # Look for cashtag mentions (e.g., $DOGE, $SHIB)
        cashtag_pattern = r'\$([a-zA-Z0-9]+)'
        cashtags = re.findall(cashtag_pattern, text)
        coins.extend(cashtags)
        
        # Remove duplicates
        return list(set(coins))
    
    def _analyze_sentiment(self, text):
        """
        Analyze sentiment of tweet text.
        
        Args:
            text (str): Tweet text
            
        Returns:
            str: Sentiment category ('positive', 'negative', 'neutral')
        """
        if not self.sentiment_analyzer:
            return "neutral"
        
        # Get base sentiment scores from NLTK
        sentiment_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Adjust with crypto-specific lexicon
        for term, score in self.crypto_lexicon.items():
            if term in text.lower():
                sentiment_scores['compound'] += score
                # Ensure the score stays within bounds
                sentiment_scores['compound'] = max(-1.0, min(1.0, sentiment_scores['compound']))
        
        # Determine sentiment category based on compound score
        if sentiment_scores['compound'] >= 0.05:
            return "positive"
        elif sentiment_scores['compound'] <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_importance(self, tweet, coins_mentioned, sentiment):
        """
        Calculate importance score for a tweet based on various factors.
        
        Args:
            tweet (dict): Tweet data
            coins_mentioned (list): List of coins mentioned in the tweet
            sentiment (str): Sentiment of the tweet
            
        Returns:
            float: Importance score between 0 and 1
        """
        score = 0.0
        
        # Base score from engagement metrics
        retweet_count = tweet.get("retweet_count", 0)
        like_count = tweet.get("like_count", 0)
        engagement_score = min(1.0, (retweet_count * 0.01 + like_count * 0.005) / 10)
        score += engagement_score * 0.4  # 40% weight
        
        # Score from number of coins mentioned (more specific is better)
        coin_count = len(coins_mentioned)
        if coin_count == 1:
            score += 0.3  # 30% weight - perfect, specific mention
        elif coin_count > 1:
            score += 0.2  # 20% weight - multiple coins
        else:
            score += 0.0  # No coins specifically identified
        
        # Score from sentiment (extreme sentiments are more interesting)
        if sentiment == "positive":
            score += 0.2  # 20% weight
        elif sentiment == "negative":
            score += 0.15  # 15% weight
        
        # Additional factors could be considered:
        # - Celebrity's influence level
        # - Presence of links
        # - Presence of price predictions
        # - Previous impact of tweets from this celebrity
        
        return round(min(1.0, score), 2)