from api.config.setup import DATABASE_URL
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")

# Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models (and Base) to make sure Alembic knows about them
from api.db.models import Base, User, Music, Playlist  # <-- Import models here!

target_metadata = Base.metadata  # Alembic needs this to detect changes in your models


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
