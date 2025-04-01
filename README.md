# CommunityVibe

A powerful social media analytics platform that collects, analyzes, and provides insights from Reddit and Twitter data.

## Features

- Real-time data collection from Reddit and Twitter
- Sentiment analysis and product mention detection
- RESTful API endpoints for data access
- Background task processing with Celery
- PostgreSQL database for data storage
- OpenAI integration for advanced analytics

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- Celery
- OpenAI API
- Reddit API (PRAW)
- Twitter API (Tweepy)

## Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- OpenAI API Key
- Reddit API Credentials
- Twitter API Credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/communityvibe.git
cd communityvibe
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/communityvibe
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
OPENAI_API_KEY=your_openai_api_key
```

5. Initialize the database:
```bash
alembic upgrade head
```

## Running the Application

1. Start Redis:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A app.tasks.worker worker --loglevel=info
```

3. Start the FastAPI application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

This project is configured for deployment on Replit. See the `.replit` and `replit.nix` files for configuration details.

## License

MIT License - see LICENSE file for details 