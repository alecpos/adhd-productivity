"""Test base model independently."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Create a completely independent base for testing
Base = declarative_base()


class IDMixin:
    """ID mixin for test models."""

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TestUser(IDMixin, Base):
    """Test user model."""

    __tablename__ = "test_users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    tasks = relationship("TestTask", back_populates="user")


class TestTask(IDMixin, Base):
    """Test task model."""

    __tablename__ = "test_tasks"

    title = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("test_users.id"))

    user = relationship("TestUser", back_populates="tasks")


# Set up an in-memory SQLite test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a new database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_id_mixin():
    """Test ID mixin."""
    assert hasattr(IDMixin, "id")
    assert hasattr(IDMixin, "created_at")
    assert hasattr(IDMixin, "updated_at")


def test_user_model_create(db_session):
    """Test creating a user."""
    user_id = str(uuid4())
    user = TestUser(id=user_id, username="test_user", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    # Get the user from the database
    user_from_db = db_session.query(TestUser).filter_by(id=user_id).first()
    assert user_from_db is not None
    assert user_from_db.id == user_id
    assert user_from_db.username == "test_user"
    assert user_from_db.email == "test@example.com"


def test_relationship(db_session):
    """Test a relationship between user and task."""
    user_id = str(uuid4())
    user = TestUser(id=user_id, username="test_user", email="test@example.com")
    db_session.add(user)

    task = TestTask(title="Test Task", user_id=user_id)
    db_session.add(task)
    db_session.commit()

    # Verify relationship
    user_from_db = db_session.query(TestUser).filter_by(id=user_id).first()
    tasks = db_session.query(TestTask).filter_by(user_id=user_id).all()

    assert user_from_db is not None
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"
    assert len(user_from_db.tasks) == 1
