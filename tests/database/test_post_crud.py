import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.models.post import Post
from app.crud.post import create_post, get_post
from datetime import datetime
from app.schemas.post import PostCreate

# Test database setup
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

def test_create_and_get_post(db_session):
    # Test data
    post_data = PostCreate(
        platform="twitter",
        platform_id="123456789",
        platform_url="https://twitter.com/test_user/status/123456789",
        content_text="Test post content",
        author_username="test_user",
        source_type="twitter",
        source_name="twitter",
        categories=["question"],
        additional_data={"test": "data"}
    )
    
    # Create post
    post = create_post(db_session, post_in=post_data)
    
    # Assertions
    assert post is not None
    assert post.platform == post_data.platform
    assert post.platform_id == post_data.platform_id
    assert post.content_text == post_data.content_text
    assert post.author_username == post_data.author_username
    assert post.categories == post_data.categories
    assert post.additional_data == post_data.additional_data
    
    # Retrieve post
    retrieved_post = get_post(db_session, post.id)
    
    # Assertions for retrieved post
    assert retrieved_post is not None
    assert retrieved_post.id == post.id
    assert retrieved_post.platform == post.platform
    assert retrieved_post.content_text == post.content_text
    assert retrieved_post.additional_data == post.additional_data
    
    # Test non-existent post
    non_existent_post = get_post(db_session, 99999)
    assert non_existent_post is None 