"""
Utility to refresh materialized views for optimal performance.
Run this periodically via cron or scheduled task.
"""
from sqlalchemy import text
from db.base import engine
import asyncio
from datetime import datetime


async def refresh_materialized_views():
    """
    Refresh all materialized views.

    Should be run:
    - Every 5 minutes for published articles
    - Every hour for statistics
    - Daily for metrics

    Can be run concurrently for faster refresh.
    """
    views_to_refresh = [
        ('mv_published_articles', 'CONCURRENTLY'),  # Can refresh without locking
        ('mv_manuscript_stats', 'CONCURRENTLY'),
        ('mv_reviewer_workload', 'CONCURRENTLY'),
        ('mv_journal_metrics', ''),  # Not concurrent (smaller table)
    ]

    print(f"[{datetime.now()}] Starting materialized view refresh...")

    with engine.connect() as conn:
        for view_name, mode in views_to_refresh:
            try:
                start_time = datetime.now()
                sql = f"REFRESH MATERIALIZED VIEW {mode} {view_name}"
                conn.execute(text(sql))
                conn.commit()
                duration = (datetime.now() - start_time).total_seconds()
                print(f"✓ Refreshed {view_name} in {duration:.2f}s")
            except Exception as e:
                print(f"✗ Failed to refresh {view_name}: {e}")

    print(f"[{datetime.now()}] Materialized view refresh complete!\n")


if __name__ == "__main__":
    asyncio.run(refresh_materialized_views())
