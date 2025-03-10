import sys
import os

# Adds the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from httpx import AsyncClient, ASGITransport  # HTTP client for testing
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.setup import Base  # Base class (holds metadata for models)
from app.db.core import get_async_db  # Function to retrieve the database session
from app.main import app  # Import FastAPI application
from app.db.models import User, Music, Playlist  # Import database models

# Define an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create an async database engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Create a session factory for generating async database sessions
TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)


# Function to seed initial test data into the database
async def seed_database(session):
    seed_user = User(
        id=1,
        username="seed_user",
        email="seed_user@email.com",
        password="$2a$12$TDJFaiwRleVEBYnvd/CVbuGIjbu/zVhImLgXuGlQgDrV8a734kK.2",
    )
    seed_music_in_playlist = Music(
        id=1,
        title="Seed Song",
        artist="Seed Artist",
        link="https://example.com/seed",
        added_by=seed_user.id,
    )
    seed_music_left_out = Music(
        id=2,
        title="When Orange is the Sky",
        artist="Fabrizio Paterlini",
        link="https://open.spotify.com/track/67u3IsSI1tmEsF7jZWPQWc?si=cbaf4b10c6de485c",
        added_by=seed_user.id,
    )
    public_seed_playlist = Playlist(
        id=1,
        name="Seed Playlist 1",
        private=False,
        owner_id=seed_user.id,
        musics=[seed_music_in_playlist],
    )
    private_seed_playlist = Playlist(
        id=2,
        name="Seed Playlist 2",
        private=True,
        owner_id=seed_user.id,
        musics=[seed_music_in_playlist],
    )
    session.add_all(
        [
            seed_user,
            seed_music_in_playlist,
            public_seed_playlist,
            private_seed_playlist,
            seed_music_left_out,
        ]
    )
    await session.commit()


# This fixture sets up and tears down the test database schema
# since its a function and not session scope, it runs for each test
@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    # Create all tables before running tests
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)  # Creates tables

    # Create a session and seed data
    async with TestingSessionLocal() as session:
        await seed_database(session)

    yield  # This allows tests to run while the database exists

    # ? This drops all tables after tests complete, since I need seed to persist It'll be left commented
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)  # Deletes tables


# This fixture provides a single database session shared across all tests
@pytest.fixture(scope="session")
async def db():
    session = TestingSessionLocal()  # Create a session
    yield session  # Keep it open for all tests
    await session.close()  # Close after all tests finish


# This fixture overrides FastAPI's database dependency to use the test database
@pytest.fixture(scope="function")
async def client(db):
    # Override the get_async_db function to provide the test database session
    async def override_get_db():
        yield db

    app.dependency_overrides[get_async_db] = override_get_db

    # Use ASGITransport to run FastAPI app in tests
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # Provide the test client to the test cases
