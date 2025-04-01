import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.session import get_db
from app.db.base_class import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.crud.post import create_post
from app.schemas.post import PostCreate
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_posts(db_session):
    # Create test posts
    posts = []
    for i in range(5):
        post_data = PostCreate(
            platform="twitter",
            platform_id=f"123456789{i}",
            platform_url=f"https://twitter.com/test_user/status/123456789{i}",
            content_text=f"Test post content {i}",
            author_username=f"test_user_{i}",
            source_type="twitter",
            source_name="twitter",
            categories=[f"category_{i}"],
            additional_data={"test": f"data_{i}"}
        )
        post = create_post(db_session, post_in=post_data)
        posts.append(post)
    return posts

def test_get_posts(client, test_posts):
    # Test the GET /api/v1/posts/ endpoint
    response = client.get("/api/v1/posts/?limit=5")  # Limit to 5 posts
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    
    # Verify the structure of returned posts
    for post in data:
        assert "id" in post
        assert "platform" in post
        assert "platform_id" in post
        assert "content_text" in post
        assert "author_username" in post
        assert "categories" in post
        assert isinstance(post["categories"], list)
    
    # Test pagination parameters
    response = client.get("/api/v1/posts/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Test with invalid parameters
    response = client.get("/api/v1/posts/?skip=-1")
    assert response.status_code == 422  # Validation error
    
    # Test with non-existent endpoint
    response = client.get("/api/v1/nonexistent/")
    assert response.status_code == 404 