# Database Connection Guide

This guide explains how to connect to the PostgreSQL database used by the CommunityVibe backend.

## Database Summary

From the analysis of posts in the database, we have:
- Total posts: 296
- All posts are from Reddit (296)
- Main subreddits: webdev (64), programming (54), vscode (53)
- 77 posts have assigned categories based on keywords

## Connecting to the Database

### Option 1: Using psql Command Line

If you have the PostgreSQL client installed, you can connect using:

```bash
# Connect with the database URL from the .env file
psql postgresql://postgres:postgres@localhost:5432/communityvibe

# Or connect with individual parameters
psql -h localhost -p 5432 -U postgres -d communityvibe
```

When prompted, enter the password (which is "postgres" according to the .env file).

### Option 2: Using a GUI Client

You can use PostgreSQL GUI clients like:
- pgAdmin 4
- DBeaver
- TablePlus
- DataGrip

Connect with these parameters:
- Host: localhost
- Port: 5432
- Database: communityvibe
- Username: postgres
- Password: postgres

## Useful SQL Queries

Here are some useful queries to explore the data:

### Count all posts
```sql
SELECT COUNT(*) FROM posts;
```

### View recent posts
```sql
SELECT id, platform, source_name, content_text, categories, created_at 
FROM posts 
ORDER BY created_at DESC 
LIMIT 10;
```

### Count posts by category
```sql
SELECT 
  jsonb_array_elements_text(categories::jsonb) as category,
  COUNT(*) 
FROM posts 
WHERE categories IS NOT NULL AND categories::text != '[]'
GROUP BY category
ORDER BY COUNT(*) DESC;
```

### Find posts with multiple categories
```sql
SELECT 
  id, 
  content_text, 
  categories,
  jsonb_array_length(categories::jsonb) as category_count
FROM posts 
WHERE jsonb_array_length(categories::jsonb) > 1
ORDER BY category_count DESC;
```

## Using the Python Scripts

Several scripts are provided to help you analyze the database:

- `scripts/count_posts.py` - Counts and summarizes posts in the database
- `scripts/list_categories.py` - Lists posts by category
- `scripts/test_keyword_categorization.py` - Tests keyword categorization
- `scripts/test_api_filtering.py` - Tests the API filtering by category 