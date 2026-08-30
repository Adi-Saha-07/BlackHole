import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import Integer, String, Float, Boolean, DateTime, func, select, desc
from sqlalchemy.orm import Mapped, mapped_column
from app.models import db, Base

logger = logging.getLogger(__name__)

class QueryLog(Base):
    """
    Tracks and logs every search query executed on Black-Hole
    for analytics, recent activity, and trending queries.
    """
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_query: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_query: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    search_time: Mapped[float] = mapped_column(Float, default=0.0)
    cached: Mapped[bool] = mapped_column(Boolean, default=False)
    client_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<QueryLog id={self.id} query='{self.search_query}' cached={self.cached}>"

    @classmethod
    def log(
        cls, 
        query: str, 
        result_count: int = 0, 
        search_time: float = 0.0, 
        cached: bool = False, 
        client_ip: Optional[str] = None
    ) -> Optional["QueryLog"]:
        """
        Helper to create and commit a query log record safely.
        Returns the created QueryLog instance or None on error.
        """
        if not query or not query.strip():
            return None

        try:
            record = cls(
                search_query=query.strip(),
                normalized_query=query.strip().lower(),
                result_count=result_count,
                search_time=search_time,
                cached=cached,
                client_ip=client_ip
            )
            db.session.add(record)
            db.session.commit()
            return record
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to log query '{query}': {e}")
            return None

    @classmethod
    def get_trending(cls, limit: int = 8, days: int = 7) -> List[Dict[str, Any]]:
        """
        Calculates trending/most-searched queries over the specified time window.
        Returns a list of dicts: [{'query': '...', 'count': ...}, ...]
        """
        try:
            since = datetime.now(timezone.utc) - timedelta(days=days)
            stmt = (
                select(
                    cls.normalized_query,
                    func.max(cls.search_query).label("display_query"),
                    func.count(cls.id).label("count")
                )
                .where(cls.timestamp >= since)
                .group_by(cls.normalized_query)
                .order_by(desc(func.count(cls.id)))
                .limit(limit)
            )
            results = db.session.execute(stmt).all()
            return [
                {"query": row.display_query, "count": row.count}
                for row in results
            ]
        except Exception as e:
            logger.error(f"Failed to fetch trending queries: {e}")
            return []

    @classmethod
    def get_recent(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns the most recent unique queries."""
        try:
            stmt = select(cls).order_by(desc(cls.timestamp)).limit(limit)
            results = db.session.scalars(stmt).all()
            return [
                {
                    "query": r.search_query, 
                    "timestamp": r.timestamp.isoformat() if r.timestamp else "", 
                    "cached": r.cached
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Failed to fetch recent queries: {e}")
            return []
