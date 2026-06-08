from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, DateTime
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class Coin(Base):
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
