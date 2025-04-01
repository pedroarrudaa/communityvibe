import logging
from celery import Celery
from app.core.config import settings
from app.tasks.post_processing import process_posts_with_openai
from app.db.session import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Celery
celery = Celery(
    'communityvibe',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task(name='process_posts')
def process_posts_task():
    """Process posts with OpenAI as a background task"""
    try:
        db = SessionLocal()
        result = process_posts_with_openai(db)
        logger.info(f"Posts processed with OpenAI: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing posts with OpenAI: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == '__main__':
    celery.start() 