import pytest
from app.services.openai_service import OpenAIService
from app.core.config import settings

@pytest.fixture
def openai_service():
    return OpenAIService()

def test_create_sentiment_prompt(openai_service):
    # Test data
    content = "I love using VSCode for development!"
    products = ["VSCode", "GitHub Copilot"]
    
    # Generate prompt
    prompt = openai_service._create_sentiment_prompt(content, products)
    
    # Assertions
    assert isinstance(prompt, str)
    assert content in prompt
    assert all(product in prompt for product in products)
    assert "sentiment analysis expert" in prompt
    assert "JSON object" in prompt
    assert "sentiment" in prompt.lower()
    assert "confidence" in prompt.lower()
    assert "explanation" in prompt.lower()
    
    # Test with empty products list
    prompt_empty = openai_service._create_sentiment_prompt(content, [])
    assert content in prompt_empty
    assert "products" not in prompt_empty.lower() 