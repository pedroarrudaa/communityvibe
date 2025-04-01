from typing import List, Dict, Any, Optional
import openai
from app.core.config import settings
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors"""
    pass

class OpenAIAnalysisError(OpenAIServiceError):
    """Raised when OpenAI analysis fails"""
    pass

class OpenAITimeoutError(OpenAIServiceError):
    """Raised when OpenAI request times out"""
    pass

class OpenAIService:
    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_retries = settings.OPENAI_MAX_RETRIES
        self.timeout = settings.OPENAI_TIMEOUT
        self.supported_products = [
            "cursor",
            "lovable",
            "bolt",
            "intellij",
            "vs code",
            "windsurf ide"
        ]
        self.supported_categories = [
            "Bug Reports",
            "Feature Requests",
            "General Feedback",
            "Questions",
            "Praise",
            "Issues"
        ]

    @retry(
        stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def analyze_sentiment(self, content: str, products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of content using ChatGPT-4.
        If products are provided, analyze sentiment for each product.
        """
        try:
            # Construct the prompt
            prompt = self._create_sentiment_prompt(content, products)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Analyze the sentiment of the given content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                logger.info(f"Sentiment analysis completed for content: {content[:100]}...")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {str(e)}")
                raise OpenAIAnalysisError("Invalid response format from OpenAI")
            
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI request timed out: {str(e)}")
            raise OpenAITimeoutError(f"Request timed out after {settings.OPENAI_TIMEOUT} seconds")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIAnalysisError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in sentiment analysis: {str(e)}")
            raise OpenAIServiceError(f"Unexpected error: {str(e)}")

    @retry(
        stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def extract_products(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract product mentions from content using ChatGPT-4.
        Returns a list of dictionaries containing product information.
        """
        try:
            # Construct the prompt
            prompt = self._create_product_extraction_prompt(content)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product mention extraction expert. Identify all product names mentioned in the content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                logger.info(f"Product extraction completed for content: {content[:100]}...")
                return result["products"]
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {str(e)}")
                raise OpenAIAnalysisError("Invalid response format from OpenAI")
            
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI request timed out: {str(e)}")
            raise OpenAITimeoutError(f"Request timed out after {settings.OPENAI_TIMEOUT} seconds")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIAnalysisError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in product extraction: {str(e)}")
            raise OpenAIServiceError(f"Unexpected error: {str(e)}")

    @retry(
        stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def categorize_content(self, content: str, available_categories: List[str], products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Categorize content using ChatGPT-4.
        """
        try:
            # Construct the prompt
            prompt = self._create_categorization_prompt(content, available_categories, products)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content categorization expert. Categorize the given content into the provided categories."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parse the response
            try:
                result = json.loads(response.choices[0].message.content)
                logger.info(f"Content categorization completed for content: {content[:100]}...")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response: {str(e)}")
                raise OpenAIAnalysisError("Invalid response format from OpenAI")
            
        except openai.APITimeoutError as e:
            logger.error(f"OpenAI request timed out: {str(e)}")
            raise OpenAITimeoutError(f"Request timed out after {settings.OPENAI_TIMEOUT} seconds")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIAnalysisError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in content categorization: {str(e)}")
            raise OpenAIServiceError(f"Unexpected error: {str(e)}")

    def _create_sentiment_prompt(self, content: str, products: Optional[List[str]] = None) -> str:
        """Create prompt for sentiment analysis"""
        if products:
            return (
                "You are a sentiment analysis expert. Your task is to analyze the sentiment of the content "
                "for specific products. You must respond with ONLY a valid JSON object and no other text.\n\n"
                f"Content: {content}\n"
                f"Products to analyze: {', '.join(products)}\n\n"
                "Required JSON format:\n"
                "{\n"
                '    "sentiment": "positive|negative|neutral|mixed",\n'
                '    "product_sentiments": {\n'
                '        "product_name": {\n'
                '            "sentiment": "positive|negative|neutral|mixed",\n'
                '            "aspects": {\n'
                '                "aspect_name": "positive|negative|neutral|mixed"\n'
                "            },\n"
                '            "intensity": 0.8,\n'
                '            "confidence": 0.9,\n'
                '            "context": "Brief context of the product mention"\n'
                "        }\n"
                "    },\n"
                '    "confidence": 0.9,\n'
                '    "explanation": "Brief explanation"\n'
                "}\n\n"
                "Notes:\n"
                "1. Default to 'neutral' if sentiment is unclear\n"
                "2. Use 'mixed' when there are both positive and negative aspects\n"
                "3. Only analyze products from the supported list\n"
                "4. Include relevant context for each product mention"
            )
        else:
            return (
                "You are a sentiment analysis expert. Your task is to analyze the sentiment of the content. "
                "You must respond with ONLY a valid JSON object and no other text.\n\n"
                f"Content: {content}\n\n"
                "Required JSON format:\n"
                "{\n"
                '    "sentiment": "positive|negative|neutral|mixed",\n'
                '    "intensity": 0.8,\n'
                '    "confidence": 0.9,\n'
                '    "explanation": "Brief explanation"\n'
                "}"
            )

    def _create_product_extraction_prompt(self, content: str) -> str:
        """Create prompt for product extraction"""
        return (
            "You are a product mention extraction expert. Your task is to identify all product mentions "
            "in the content, focusing on these specific products: cursor, lovable, bolt, intellij, vs code, windsurf ide. "
            "You must respond with ONLY a valid JSON object and no other text.\n\n"
            f"Content: {content}\n\n"
            "Required JSON format:\n"
            "{\n"
            '    "products": [\n'
            "        {\n"
            '            "name": "product_name",\n'
            '            "confidence": 0.9,\n'
            '            "context": "Brief context of how the product is mentioned",\n'
            '            "sentiment": "positive|negative|neutral|mixed",\n'
            '            "aspects": ["feature", "performance", "ui", "etc"],\n'
            '            "is_primary_mention": true|false,\n'
            '            "version": "version if mentioned",\n'
            '            "features": ["specific features mentioned"],\n'
            '            "comparisons": ["other products compared to"],\n'
            '            "user_type": "developer|designer|student|etc"\n'
            "        }\n"
            "    ],\n"
            '    "confidence": 0.9,\n'
            '    "explanation": "Brief explanation of the extraction"\n'
            "}\n\n"
            "Rules:\n"
            "1. Only include products from the specified list\n"
            "2. Include confidence scores (0.0 to 1.0)\n"
            "3. Provide context for each mention\n"
            "4. Mark primary mentions (where the product is the main topic)\n"
            "5. Include relevant aspects being discussed\n"
            "6. Include sentiment for each mention\n"
            "7. Extract version numbers if mentioned\n"
            "8. List specific features discussed\n"
            "9. Note any product comparisons\n"
            "10. Identify the type of user discussing the product"
        )

    def _create_categorization_prompt(self, content: str, categories: List[str], products: Optional[List[str]] = None) -> str:
        """Create prompt for content categorization"""
        category_descriptions = {
            "Bug Reports": "Identifies specific technical issues or malfunctions in the tool",
            "Feature Requests": "Suggestions for new functionalities or improvements",
            "General Feedback": "Comments or opinions that don't fit neatly into other categories",
            "Questions": "User inquiries or requests for clarification",
            "Praise": "Positive feedback or testimonials",
            "Issues": "Problems that aren't bugs but need attention"
        }
        
        categories_info = "\n".join([f"- {cat}: {category_descriptions.get(cat, '')}" for cat in categories])
        
        return (
            "You are a content categorization expert. Your task is to categorize the given content "
            "into the most appropriate category. You must respond with ONLY a valid JSON object and no other text.\n\n"
            f"Content: {content}\n\n"
            "Available categories with descriptions:\n"
            f"{categories_info}\n\n"
            f"Products mentioned: {', '.join(products) if products else 'None'}\n\n"
            "Required JSON format:\n"
            "{\n"
            '    "category": "Category name",\n'
            '    "confidence": 0.9,\n'
            '    "explanation": "Brief explanation of why this category was chosen",\n'
            '    "secondary_categories": ["Category1", "Category2"],\n'
            '    "keywords": ["keyword1", "keyword2"],\n'
            '    "product_context": {\n'
            '        "product_name": "Category specific to this product"\n'
            "    }\n"
            "}"
        ) 