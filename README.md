# Memecoin Tweet Tracker

A data analysis system for tracking and analyzing memecoin-related tweets from celebrities and influencers using historical tweet datasets.

## Features

- Historical tweet dataset processing and analysis
- Celebrity and influencer tweet tracking
- Sentiment analysis of tweets
- Memecoin mention detection
- Trend analysis and statistics
- Email notifications for significant events
- REST API for data access
- Interactive dashboard for visualization

## Prerequisites

- Python 3.8+
- MongoDB
- Tweet dataset in JSONL format
- SMTP server for email notifications (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/memecoin-info.git
cd memecoin-info
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirement.txt
```

4. Set up NLP components:
```bash
python setup_nlp.py
```

5. Prepare your dataset:
   - Place your tweet dataset in JSONL format at `data/tweets.jsonl`
   - Each tweet should include: id, text, created_at, author (username, name), engagement metrics

6. Configure the application:
   - Copy `config/dataset_config.json.example` to `config/dataset_config.json`
   - Update the configuration with your dataset settings
   - Configure email settings for notifications (optional)

## Dataset Format

The system expects tweets in JSONL format with the following structure:
```json
{
    "id": "tweet_id",
    "text": "tweet content",
    "created_at": "2023-01-01T00:00:00Z",
    "author": {
        "username": "username",
        "name": "display name",
        "followers_count": 1000
    },
    "like_count": 100,
    "retweet_count": 50,
    "reply_count": 10,
    "mentions": ["user1", "user2"],
    "hashtags": ["memecoin", "crypto"],
    "urls": ["https://example.com"]
}
```

## Usage

1. Process the dataset:
```bash
python main.py
```

2. Access the dashboard:
   - Open `http://localhost:8050` in your browser

3. Use the REST API:
   - Base URL: `http://localhost:5001`
   - Available endpoints:
     - `/api/tweets`: Get tweets with filters
     - `/api/celebrities`: Get tracked celebrities
     - `/api/keywords`: Get tracked keywords
     - `/api/statistics`: Get analysis statistics
     - `/api/trends`: Get trending memecoins

## Project Structure

```
memecoin-info/
├── src/
│   ├── api.py              # REST API implementation
│   ├── dashboard.py        # Interactive dashboard
│   ├── data_processor.py   # Data analysis and processing
│   ├── notification_service.py  # Email notifications
│   └── twitter_listener.py # Dataset processing
├── config/
│   ├── dataset_config.json
│   ├── database_config.json
│   └── email_config.json
├── data/
│   ├── tweets.jsonl       # Tweet dataset
│   └── nltk_data/         # NLP models and data
├── tests/
│   ├── test_twitter.py
│   └── test_db.py
├── main.py
├── setup_nlp.py
└── requirement.txt
```

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NLTK for natural language processing
- MongoDB for data storage
- Flask and Dash for web interfaces 