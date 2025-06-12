"""
Notification Service for the Memecoin Tweet Tracker.
Handles alerts and notifications for significant events and trends.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the notification service with configuration."""
        self.config = config
        self.email_config = config.get('email', {})
        self.alert_thresholds = config.get('alert_thresholds', {})
        self.notification_history = []

    def send_email_alert(self, subject: str, body: str, recipients: List[str]) -> bool:
        """Send email alert to specified recipients."""
        try:
            if not self.email_config.get('enabled', False):
                logger.info("Email notifications are disabled")
                return False

            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(
                    self.email_config['sender_email'],
                    self.email_config['password']
                )
                server.send_message(msg)

            logger.info(f"Email alert sent to {len(recipients)} recipients")
            return True
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False

    def check_trend_alert(self, trend_data: Dict[str, Any]) -> bool:
        """Check if trend data meets alert criteria."""
        try:
            # Check volume threshold
            if trend_data['volume'] > self.alert_thresholds.get('volume_threshold', 1000):
                self.send_trend_alert(trend_data)
                return True

            # Check sentiment threshold
            if trend_data['sentiment_score'] > self.alert_thresholds.get('sentiment_threshold', 0.8):
                self.send_trend_alert(trend_data)
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking trend alert: {e}")
            return False

    def send_trend_alert(self, trend_data: Dict[str, Any]) -> None:
        """Send alert for significant trend."""
        try:
            subject = f"Memecoin Alert: {trend_data['coin_name']} Trending"
            
            body = f"""
            <h2>Memecoin Trend Alert</h2>
            <p><strong>Coin:</strong> {trend_data['coin_name']}</p>
            <p><strong>Volume:</strong> {trend_data['volume']}</p>
            <p><strong>Sentiment Score:</strong> {trend_data['sentiment_score']}</p>
            <p><strong>Top Mentions:</strong></p>
            <ul>
            """
            
            for mention in trend_data.get('top_mentions', [])[:5]:
                body += f"<li>{mention['username']}: {mention['text']}</li>"
            
            body += "</ul>"

            recipients = self.email_config.get('recipients', [])
            self.send_email_alert(subject, body, recipients)
            
            # Log notification
            self.notification_history.append({
                'timestamp': datetime.utcnow(),
                'type': 'trend_alert',
                'data': trend_data
            })
        except Exception as e:
            logger.error(f"Error sending trend alert: {e}")

    def send_celeb_alert(self, tweet_data: Dict[str, Any]) -> None:
        """Send alert for significant celebrity tweet."""
        try:
            subject = f"Celebrity Alert: {tweet_data['author']['username']} Tweeted About Memecoin"
            
            body = f"""
            <h2>Celebrity Tweet Alert</h2>
            <p><strong>Author:</strong> {tweet_data['author']['name']} (@{tweet_data['author']['username']})</p>
            <p><strong>Followers:</strong> {tweet_data['author']['followers_count']}</p>
            <p><strong>Tweet:</strong> {tweet_data['text']}</p>
            <p><strong>Engagement:</strong></p>
            <ul>
                <li>Likes: {tweet_data['engagement']['likes']}</li>
                <li>Retweets: {tweet_data['engagement']['retweets']}</li>
                <li>Replies: {tweet_data['engagement']['replies']}</li>
            </ul>
            """

            recipients = self.email_config.get('recipients', [])
            self.send_email_alert(subject, body, recipients)
            
            # Log notification
            self.notification_history.append({
                'timestamp': datetime.utcnow(),
                'type': 'celeb_alert',
                'data': tweet_data
            })
        except Exception as e:
            logger.error(f"Error sending celebrity alert: {e}")

    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history."""
        return self.notification_history[-limit:]

    def save_notification_history(self) -> None:
        """Save notification history to file."""
        try:
            history_file = Path("data/notification_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(history_file, 'w') as f:
                json.dump(self.notification_history, f, default=str)
            
            logger.info("Notification history saved successfully")
        except Exception as e:
            logger.error(f"Error saving notification history: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    from config import load_config
    config = load_config()
    
    # Initialize notification service
    notification_service = NotificationService(config) 