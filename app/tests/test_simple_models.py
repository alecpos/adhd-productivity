"""Simple model tests that don't rely on relationships."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine

# Create a separate base for test models to avoid importing relationships
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship, declared_attr, Mapped, mapped_column

class TestBaseModel(DeclarativeBase):
    """Base model for test models to prevent loading the full model hierarchy."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create simplified models for testing
class SimpleUser(TestBaseModel):
    """Simple user model for testing."""

    __tablename__ = "simple_users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

class SimpleTask(TestBaseModel):
    """Simple task model for testing."""

    __tablename__ = "simple_tasks"

    title = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("simple_users.id"))

    # Relationship
    user = relationship("SimpleUser")

# Set up an in-memory SQLite test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for each test."""
    TestBaseModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    TestBaseModel.metadata.drop_all(bind=engine)

def test_base_model_init():
    """Test BaseModel initialization."""
    assert hasattr(TestBaseModel, 'id')
    assert hasattr(TestBaseModel, 'created_at')
    assert hasattr(TestBaseModel, 'updated_at')

def test_simple_user_model_create(db_session):
    """Test creating a simple user."""
    user_id = str(uuid4())
    user = SimpleUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()

    # Get the user from the database
    user_from_db = db_session.query(SimpleUser).filter_by(id=user_id).first()
    assert user_from_db is not None
    assert user_from_db.id == user_id
    assert user_from_db.username == "test_user"
    assert user_from_db.email == "test@example.com"

def test_simple_relationship(db_session):
    """Test a simple relationship between user and task."""
    user_id = str(uuid4())
    user = SimpleUser(
        id=user_id,
        username="test_user",
        email="test@example.com"
    )
    db_session.add(user)

    task = SimpleTask(
        title="Test Task",
        user_id=user_id
    )
    db_session.add(task)
    db_session.commit()

    # Verify relationship
    user_from_db = db_session.query(SimpleUser).filter_by(id=user_id).first()
    tasks = db_session.query(SimpleTask).filter_by(user_id=user_id).all()

    assert user_from_db is not None
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"
