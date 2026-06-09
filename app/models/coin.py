from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, DateTime
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class Coin(Base):
    """
    SQLAlchemy model representing a cryptocurrency coin and its price data.
    This model defines the structure of the 'coins' table in the database, including fields for coin ID, symbol, name, current price, market cap, volume, and timestamps.

    Attributes:
        id: The primary key for the coin record in the database
        coin_id: The unique identifier of the coin (e.g., 'bitcoin')
        coin_symbol: The symbol of the coin (e.g., 'btc')
        coin_name: The full name of the coin (e.g., 'Bitcoin')
        current_price_usd: The current price of the coin in USD
        market_cap: The market capitalization of the coin in USD
        market_cap_rank: The rank of the coin based on market capitalization
        total_volume: The total trading volume of the coin in the last 24 hours in USD
        price_change_percentage_24h: The percentage change in price over the last 24 hours
        timestamp: The timestamp when the record was created in the database
        last_updated: The timestamp of the last update for the coin data
    """
    __tablename__ = "coins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    coin_id: Mapped[str] = mapped_column(String(50))
    coin_symbol: Mapped[str] = mapped_column(String(20))
    coin_name: Mapped[str] = mapped_column(String(100))
    current_price_usd: Mapped[float] = mapped_column(Numeric(18, 6))
    market_cap: Mapped[float] = mapped_column(Numeric(20, 6))
    market_cap_rank: Mapped[int] = mapped_column(Integer)
    total_volume: Mapped[float] = mapped_column(Numeric(20, 6))
    price_change_percentage_24h: Mapped[float] = mapped_column(Numeric(10, 4))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True))
