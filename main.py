#!/usr/bin/env python3
"""
Main entry point for the Memecoin Tweet Tracker application.
Initializes and coordinates all the components of the system.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
import threading

from config import load_config
from twitter_listener import TwitterListener
from tweet_analyzer import TweetAnalyzer
from database import DatabaseHandler
from src.notifcation_service import NotificationService
from src.data_processor import DataProcessor
from src.api import init_api, start_api
from src.dashboard import start_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("memecoin_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Initialize and start all components of the application."""
    logger.info("Starting Memecoin Tweet Tracker")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize components
        db_handler = DatabaseHandler(config["database"])
        db_handler.initialize_test_data()  # Initialize test data
        tweet_analyzer = TweetAnalyzer()
        notification_service = NotificationService(config["notifications"])
        data_processor = DataProcessor(db_handler)
        
        # Initialize and start Twitter listener
        twitter_listener = TwitterListener(
            config["twitter_api"], 
            db_handler,
            tweet_analyzer,
            notification_service
        )
        
        # Initialize API
        init_api(db_handler, data_processor)
        
        # Start components in separate threads
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Start the Twitter listener
            executor.submit(twitter_listener.start_stream)
            
            # Start the API server in a separate thread
            api_thread = threading.Thread(
                target=start_api,
                args=(config["api"],),
                daemon=True
            )
            api_thread.start()
            
            # Start the dashboard server
            start_dashboard(config["dashboard"])
            
            # Start periodic data processing
            while True:
                try:
                    # Process data periodically
                    data_processor.process_recent_data()
                    time.sleep(config["processing_interval"])
                except KeyboardInterrupt:
                    logger.info("Shutting down Memecoin Tweet Tracker")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(10)  # Wait before retrying

    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main()