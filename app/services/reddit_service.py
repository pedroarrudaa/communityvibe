from typing import List, Optional
import praw
from praw.models import Submission
from app.core.config import settings
from app.schemas.post import PostCreate
from app.services.keyword_service import KeywordService
import logging

logger = logging.getLogger(__name__)

class RedditService:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT
        )
        self.keyword_service = KeywordService()
    
    def _get_fetch_limit(self, requested_limit: Optional[int] = None) -> int:
        """
        Determine the appropriate fetch limit based on development mode and requested limit
        """
        if requested_limit is not None:
            return requested_limit
            
        if settings.DEV_MODE:
            logger.info(f"Development mode active. Limiting fetch to {settings.DEV_POST_LIMIT} posts")
            return settings.DEV_POST_LIMIT
            
        return 100  # Default production limit
    
    def fetch_subreddit_posts(self, subreddit_name: str, limit: Optional[int] = None) -> List[PostCreate]:
        """
        Fetch posts from a specific subreddit
        """
        fetch_limit = self._get_fetch_limit(limit)
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        logger.info(f"Fetching {fetch_limit} posts from r/{subreddit_name}")
        
        for submission in subreddit.new(limit=fetch_limit):
            post = self._convert_submission_to_post(submission, subreddit_name)
            posts.append(post)
        
        return posts
    
    def search_subreddit(self, subreddit_name: str, query: str, limit: Optional[int] = None) -> List[PostCreate]:
        """
        Search for posts in a subreddit with a specific query
        """
        fetch_limit = self._get_fetch_limit(limit)
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        
        logger.info(f"Searching r/{subreddit_name} for '{query}' with limit {fetch_limit}")
        
        for submission in subreddit.search(query, limit=fetch_limit):
            post = self._convert_submission_to_post(submission, subreddit_name)
            posts.append(post)
        
        return posts
    
    def _convert_submission_to_post(self, submission: Submission, subreddit_name: str) -> PostCreate:
        """
        Convert a Reddit submission to our PostCreate model
        """
        # Combine title and selftext for more complete categorization
        full_text = f"{submission.title} {submission.selftext if submission.is_self else ''}"
        
        # Categorize the post based on keywords
        categories = self.keyword_service.categorize_text(full_text)
        
        # Store raw Reddit API data
        additional_data = {
            "reddit": {
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self,
                "is_original_content": submission.is_original_content,
                "is_reddit_media_domain": submission.is_reddit_media_domain,
                "is_video": submission.is_video,
                "over_18": submission.over_18,
                "spoiler": submission.spoiler,
                "stickied": submission.stickied,
                "locked": submission.locked,
                "archived": submission.archived,
                "distinguished": submission.distinguished,
                "edited": submission.edited,
                "created_utc": submission.created_utc,
                "author_flair_text": submission.author_flair_text if submission.author else None,
                "author_flair_css_class": submission.author_flair_css_class if submission.author else None,
                "link_flair_text": submission.link_flair_text,
                "link_flair_css_class": submission.link_flair_css_class,
                "url": submission.url,
                "permalink": submission.permalink,
                "domain": submission.domain,
                "media": submission.media if hasattr(submission, 'media') else None,
                "preview": submission.preview if hasattr(submission, 'preview') else None,
                "secure_media": submission.secure_media if hasattr(submission, 'secure_media') else None,
                "secure_media_embed": submission.secure_media_embed if hasattr(submission, 'secure_media_embed') else None,
                "media_embed": submission.media_embed if hasattr(submission, 'media_embed') else None,
                "gildings": submission.gildings if hasattr(submission, 'gildings') else None,
                "all_awardings": submission.all_awardings if hasattr(submission, 'all_awardings') else None,
                "awarders": submission.awarders if hasattr(submission, 'awarders') else None,
                "total_awards_received": submission.total_awards_received if hasattr(submission, 'total_awards_received') else None,
                "treatment_tags": submission.treatment_tags if hasattr(submission, 'treatment_tags') else None,
                "removed_by_category": submission.removed_by_category if hasattr(submission, 'removed_by_category') else None,
                "banned_by": submission.banned_by if hasattr(submission, 'banned_by') else None,
                "allow_live_comments": submission.allow_live_comments if hasattr(submission, 'allow_live_comments') else None,
                "selftext_html": submission.selftext_html if hasattr(submission, 'selftext_html') else None,
                "likes": submission.likes if hasattr(submission, 'likes') else None,
                "suggested_sort": submission.suggested_sort if hasattr(submission, 'suggested_sort') else None,
                "user_reports": submission.user_reports if hasattr(submission, 'user_reports') else None,
                "link_flair_background_color": submission.link_flair_background_color if hasattr(submission, 'link_flair_background_color') else None,
                "link_flair_template_id": submission.link_flair_template_id if hasattr(submission, 'link_flair_template_id') else None,
                "link_flair_text_color": submission.link_flair_text_color if hasattr(submission, 'link_flair_text_color') else None,
                "link_flair_type": submission.link_flair_type if hasattr(submission, 'link_flair_type') else None,
                "wls": submission.wls if hasattr(submission, 'wls') else None,
                "whitelist_status": submission.whitelist_status if hasattr(submission, 'whitelist_status') else None,
                "contest_mode": submission.contest_mode if hasattr(submission, 'contest_mode') else None,
                "mod_reports": submission.mod_reports if hasattr(submission, 'mod_reports') else None,
                "author_patreon_flair": submission.author_patreon_flair if hasattr(submission, 'author_patreon_flair') else None,
                "author_flair_type": submission.author_flair_type if hasattr(submission, 'author_flair_type') else None,
                "can_gild": submission.can_gild if hasattr(submission, 'can_gild') else None,
                "can_mod_post": submission.can_mod_post if hasattr(submission, 'can_mod_post') else None,
                "clicked": submission.clicked if hasattr(submission, 'clicked') else None,
                "hidden": submission.hidden if hasattr(submission, 'hidden') else None,
                "is_crosspostable": submission.is_crosspostable if hasattr(submission, 'is_crosspostable') else None,
                "is_meta": submission.is_meta if hasattr(submission, 'is_meta') else None,
                "is_robot_indexable": submission.is_robot_indexable if hasattr(submission, 'is_robot_indexable') else None,
                "is_self": submission.is_self if hasattr(submission, 'is_self') else None,
                "is_shareable": submission.is_shareable if hasattr(submission, 'is_shareable') else None,
                "is_web_creatable": submission.is_web_creatable if hasattr(submission, 'is_web_creatable') else None,
                "link_flair_richtext": submission.link_flair_richtext if hasattr(submission, 'link_flair_richtext') else None,
                "link_flair_template_id": submission.link_flair_template_id if hasattr(submission, 'link_flair_template_id') else None,
                "link_flair_text_color": submission.link_flair_text_color if hasattr(submission, 'link_flair_text_color') else None,
                "link_flair_type": submission.link_flair_type if hasattr(submission, 'link_flair_type') else None,
                "parent_whitelist_status": submission.parent_whitelist_status if hasattr(submission, 'parent_whitelist_status') else None,
                "permalink": submission.permalink if hasattr(submission, 'permalink') else None,
                "pinned": submission.pinned if hasattr(submission, 'pinned') else None,
                "pwls": submission.pwls if hasattr(submission, 'pwls') else None,
                "quarantine": submission.quarantine if hasattr(submission, 'quarantine') else None,
                "removal_reason": submission.removal_reason if hasattr(submission, 'removal_reason') else None,
                "removed_by": submission.removed_by if hasattr(submission, 'removed_by') else None,
                "report_reasons": submission.report_reasons if hasattr(submission, 'report_reasons') else None,
                "rte_mode": submission.rte_mode if hasattr(submission, 'rte_mode') else None,
                "saved": submission.saved if hasattr(submission, 'saved') else None,
                "score": submission.score if hasattr(submission, 'score') else None,
                "send_replies": submission.send_replies if hasattr(submission, 'send_replies') else None,
                "show_media": submission.show_media if hasattr(submission, 'show_media') else None,
                "show_media_preview": submission.show_media_preview if hasattr(submission, 'show_media_preview') else None,
                "spoiler": submission.spoiler if hasattr(submission, 'spoiler') else None,
                "stickied": submission.stickied if hasattr(submission, 'stickied') else None,
                "subreddit_type": submission.subreddit_type if hasattr(submission, 'subreddit_type') else None,
                "suggested_sort": submission.suggested_sort if hasattr(submission, 'suggested_sort') else None,
                "thumbnail": submission.thumbnail if hasattr(submission, 'thumbnail') else None,
                "thumbnail_height": submission.thumbnail_height if hasattr(submission, 'thumbnail_height') else None,
                "thumbnail_width": submission.thumbnail_width if hasattr(submission, 'thumbnail_width') else None,
                "title": submission.title if hasattr(submission, 'title') else None,
                "top_awarded_type": submission.top_awarded_type if hasattr(submission, 'top_awarded_type') else None,
                "total_awards_received": submission.total_awards_received if hasattr(submission, 'total_awards_received') else None,
                "treatment_tags": submission.treatment_tags if hasattr(submission, 'treatment_tags') else None,
                "unlocked": submission.unlocked if hasattr(submission, 'unlocked') else None,
                "upvote_ratio": submission.upvote_ratio if hasattr(submission, 'upvote_ratio') else None,
                "url_overridden_by_dest": submission.url_overridden_by_dest if hasattr(submission, 'url_overridden_by_dest') else None,
                "view_count": submission.view_count if hasattr(submission, 'view_count') else None,
                "visited": submission.visited if hasattr(submission, 'visited') else None,
                "whitelist_status": submission.whitelist_status if hasattr(submission, 'whitelist_status') else None,
                "wls": submission.wls if hasattr(submission, 'wls') else None,
            }
        }
        
        return PostCreate(
            platform="reddit",
            platform_id=submission.id,
            platform_url=f"https://reddit.com{submission.permalink}",
            author_username=submission.author.name if submission.author else "[deleted]",
            author_platform_id=str(submission.author.id) if submission.author else None,
            author_avatar_url=None,  # Reddit doesn't provide this easily
            content_text=submission.selftext if submission.is_self else submission.title,
            source_type="reddit",
            source_name=subreddit_name,
            categories=categories,
            additional_data=additional_data
        ) 