# Memecoin Tweet Tracker

A web application for tracking and analyzing tweets about memecoins, with features for monitoring celebrity mentions, sentiment analysis, and trend tracking.

## Features

- Real-time tweet tracking for memecoins
- Celebrity mention monitoring
- Sentiment analysis
- Trend analysis and visualization
- Customizable keyword tracking
- Interactive dashboard
- RESTful API

## Tech Stack

### Backend
- Python
- Flask
- SQLite/PostgreSQL
- Twitter API
- Natural Language Processing

### Frontend
- React
- Material-UI
- Chart.js
- React Query
- Axios

## Setup

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the backend server:
```bash
python main.py
```

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## API Endpoints

- `GET /api/tweets` - Get tweets with optional filters
- `GET /api/celebrities` - Get list of tracked celebrities
- `GET /api/keywords` - Get list of tracked keywords
- `GET /api/statistics` - Get statistics and insights
- `GET /api/trends` - Get trending memecoins
- `POST /api/celebrities` - Add a new celebrity to track
- `POST /api/keywords` - Add a new keyword to track
- `DELETE /api/celebrities/{name}` - Remove a celebrity from tracking
- `DELETE /api/keywords/{keyword}` - Remove a keyword from tracking

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 