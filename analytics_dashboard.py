"""
================================================================================
ANALYTICS DASHBOARD — Track Performance & Revenue
================================================================================
Features:
    1. Unified analytics from all platforms (YouTube, TikTok, Blog, etc.)
    2. Revenue tracking (AdSense, Gumroad, Patreon, Affiliate)
    3. Growth metrics (followers, views, engagement)
    4. Daily/Weekly/Monthly reports
    5. Goal tracking & projections
================================================================================
Revenue Impact: Better insights = better optimization = more revenue
================================================================================
"""

import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "analytics.db"


@dataclass
class PlatformMetrics:
    """Metrics from a single platform"""
    platform: str
    date: str
    followers: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    revenue: float = 0.0
    engagement_rate: float = 0.0


@dataclass
class RevenueEntry:
    """Revenue entry"""
    date: str
    source: str
    amount: float
    currency: str = "USD"
    description: str = ""


class AnalyticsDatabase:
    """SQLite database for analytics"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    date TEXT NOT NULL,
                    followers INTEGER DEFAULT 0,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0,
                    engagement_rate REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, date)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    current_value REAL DEFAULT 0,
                    metric_type TEXT NOT NULL,
                    deadline TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_date 
                ON platform_metrics(date)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_revenue_date 
                ON revenue(date)
            """)
    
    def save_metrics(self, metrics: PlatformMetrics):
        """Save platform metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO platform_metrics 
                (platform, date, followers, views, likes, comments, shares, revenue, engagement_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.platform,
                metrics.date,
                metrics.followers,
                metrics.views,
                metrics.likes,
                metrics.comments,
                metrics.shares,
                metrics.revenue,
                metrics.engagement_rate
            ))
    
    def save_revenue(self, entry: RevenueEntry):
        """Save revenue entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO revenue (date, source, amount, currency, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry.date,
                entry.source,
                entry.amount,
                entry.currency,
                entry.description
            ))
    
    def get_metrics_range(self, start_date: str, end_date: str, platform: str = None) -> List[Dict]:
        """Get metrics for date range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if platform:
                cursor = conn.execute("""
                    SELECT * FROM platform_metrics 
                    WHERE date >= ? AND date <= ? AND platform = ?
                    ORDER BY date
                """, (start_date, end_date, platform))
            else:
                cursor = conn.execute("""
                    SELECT * FROM platform_metrics 
                    WHERE date >= ? AND date <= ?
                    ORDER BY date
                """, (start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_revenue_range(self, start_date: str, end_date: str, source: str = None) -> List[Dict]:
        """Get revenue for date range"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if source:
                cursor = conn.execute("""
                    SELECT * FROM revenue 
                    WHERE date >= ? AND date <= ? AND source = ?
                    ORDER BY date
                """, (start_date, end_date, source))
            else:
                cursor = conn.execute("""
                    SELECT * FROM revenue 
                    WHERE date >= ? AND date <= ?
                    ORDER BY date
                """, (start_date, end_date))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_total_revenue(self, start_date: str, end_date: str) -> float:
        """Get total revenue for date range"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(amount) FROM revenue 
                WHERE date >= ? AND date <= ?
            """, (start_date, end_date))
            result = cursor.fetchone()[0]
            return result if result else 0.0


class PlatformCollector:
    """Collect analytics from various platforms"""
    
    def __init__(self):
        self.db = AnalyticsDatabase()
    
    def collect_youtube(self) -> Optional[PlatformMetrics]:
        """Collect YouTube analytics"""
        try:
            # Try to use YouTube API
            from googleapiclient.discovery import build
            
            api_key = os.getenv("YOUTUBE_API_KEY")
            channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
            
            if not api_key or not channel_id:
                logging.warning("⚠️ YouTube API not configured")
                return None
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Get channel stats
            response = youtube.channels().list(
                part='statistics',
                id=channel_id
            ).execute()
            
            if response['items']:
                stats = response['items'][0]['statistics']
                
                metrics = PlatformMetrics(
                    platform="youtube",
                    date=datetime.now().strftime("%Y-%m-%d"),
                    followers=int(stats.get('subscriberCount', 0)),
                    views=int(stats.get('viewCount', 0)),
                )
                
                self.db.save_metrics(metrics)
                return metrics
            
        except Exception as e:
            logging.error(f"❌ YouTube collection failed: {e}")
        
        return None
    
    def collect_tiktok(self) -> Optional[PlatformMetrics]:
        """Collect TikTok analytics (manual or API)"""
        # TikTok API is limited - usually need manual input
        # or use unofficial methods
        logging.info("ℹ️ TikTok analytics requires manual input or unofficial API")
        return None
    
    def collect_blog(self) -> Optional[PlatformMetrics]:
        """Collect blog analytics (Google Analytics or Plausible)"""
        try:
            # Using Plausible Analytics API (privacy-focused)
            plausible_api = os.getenv("PLAUSIBLE_API_KEY")
            site_id = os.getenv("PLAUSIBLE_SITE_ID")
            
            if plausible_api and site_id:
                import requests
                
                response = requests.get(
                    f"https://plausible.io/api/v1/stats/aggregate",
                    headers={"Authorization": f"Bearer {plausible_api}"},
                    params={
                        "site_id": site_id,
                        "period": "day",
                        "metrics": "visitors,pageviews,bounce_rate"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json().get("results", {})
                    
                    metrics = PlatformMetrics(
                        platform="blog",
                        date=datetime.now().strftime("%Y-%m-%d"),
                        views=data.get("pageviews", {}).get("value", 0),
                        followers=data.get("visitors", {}).get("value", 0),
                    )
                    
                    self.db.save_metrics(metrics)
                    return metrics
            
        except Exception as e:
            logging.error(f"❌ Blog analytics collection failed: {e}")
        
        return None
    
    def collect_all(self) -> Dict[str, PlatformMetrics]:
        """Collect from all platforms"""
        results = {}
        
        youtube = self.collect_youtube()
        if youtube:
            results["youtube"] = youtube
        
        tiktok = self.collect_tiktok()
        if tiktok:
            results["tiktok"] = tiktok
        
        blog = self.collect_blog()
        if blog:
            results["blog"] = blog
        
        return results
    
    def manual_input(self, platform: str, metrics: Dict):
        """Manually input metrics"""
        pm = PlatformMetrics(
            platform=platform,
            date=datetime.now().strftime("%Y-%m-%d"),
            followers=metrics.get("followers", 0),
            views=metrics.get("views", 0),
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0),
            revenue=metrics.get("revenue", 0.0),
            engagement_rate=metrics.get("engagement_rate", 0.0),
        )
        
        self.db.save_metrics(pm)
        logging.info(f"✅ Saved {platform} metrics for {pm.date}")
        return pm


class ReportGenerator:
    """Generate analytics reports"""
    
    def __init__(self):
        self.db = AnalyticsDatabase()
    
    def daily_report(self, date: str = None) -> Dict:
        """Generate daily report"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = self.db.get_metrics_range(date, date)
        revenue = self.db.get_revenue_range(date, date)
        
        total_views = sum(m.get("views", 0) for m in metrics)
        total_followers = sum(m.get("followers", 0) for m in metrics)
        total_revenue = sum(r.get("amount", 0) for r in revenue)
        
        report = {
            "date": date,
            "type": "daily",
            "summary": {
                "total_views": total_views,
                "total_followers": total_followers,
                "total_revenue": total_revenue,
            },
            "platforms": {m.get("platform"): m for m in metrics},
            "revenue_breakdown": revenue,
        }
        
        return report
    
    def weekly_report(self, end_date: str = None) -> Dict:
        """Generate weekly report"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        
        metrics = self.db.get_metrics_range(start_date, end_date)
        revenue = self.db.get_revenue_range(start_date, end_date)
        
        # Group by platform
        by_platform = {}
        for m in metrics:
            platform = m.get("platform")
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(m)
        
        # Calculate trends
        total_revenue = sum(r.get("amount", 0) for r in revenue)
        
        report = {
            "period": f"{start_date} to {end_date}",
            "type": "weekly",
            "summary": {
                "total_revenue": total_revenue,
                "revenue_per_day": total_revenue / 7,
            },
            "platforms": by_platform,
            "revenue_breakdown": revenue,
        }
        
        return report
    
    def monthly_report(self, year: int, month: int) -> Dict:
        """Generate monthly report"""
        start_date = f"{year}-{month:02d}-01"
        
        # Get last day of month
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        end_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        
        metrics = self.db.get_metrics_range(start_date, end_date)
        revenue = self.db.get_revenue_range(start_date, end_date)
        
        total_revenue = sum(r.get("amount", 0) for r in revenue)
        
        # Revenue by source
        by_source = {}
        for r in revenue:
            source = r.get("source")
            if source not in by_source:
                by_source[source] = 0
            by_source[source] += r.get("amount", 0)
        
        report = {
            "period": f"{year}-{month:02d}",
            "type": "monthly",
            "summary": {
                "total_revenue": total_revenue,
                "revenue_by_source": by_source,
            },
            "metrics": metrics,
            "revenue_entries": revenue,
        }
        
        return report
    
    def growth_projection(self, months: int = 12) -> Dict:
        """Project growth based on current trends"""
        today = datetime.now()
        
        # Get last 30 days
        start_30d = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_30d = today.strftime("%Y-%m-%d")
        
        revenue_30d = self.db.get_total_revenue(start_30d, end_30d)
        
        # Simple projection (assuming linear growth)
        projections = []
        monthly_revenue = revenue_30d
        
        for i in range(1, months + 1):
            # Assume 10% month-over-month growth
            monthly_revenue *= 1.1
            
            projections.append({
                "month": (today + timedelta(days=30 * i)).strftime("%Y-%m"),
                "projected_revenue": round(monthly_revenue, 2),
            })
        
        return {
            "base_monthly_revenue": revenue_30d,
            "growth_rate": 0.10,  # 10%
            "projections": projections,
        }
    
    def print_dashboard(self):
        """Print ASCII dashboard to console"""
        today = datetime.now().strftime("%Y-%m-%d")
        report = self.daily_report(today)
        
        print("\n" + "=" * 60)
        print("📊 TOPIK DAILY ANALYTICS DASHBOARD")
        print("=" * 60)
        print(f"Date: {today}")
        print("-" * 60)
        
        print("\n📈 TODAY'S SUMMARY")
        print(f"   Views:     {report['summary']['total_views']:,}")
        print(f"   Followers: {report['summary']['total_followers']:,}")
        print(f"   Revenue:   ${report['summary']['total_revenue']:.2f}")
        
        print("\n📱 BY PLATFORM")
        for platform, metrics in report.get("platforms", {}).items():
            print(f"   {platform.upper()}")
            print(f"      Views: {metrics.get('views', 0):,}")
            print(f"      Followers: {metrics.get('followers', 0):,}")
        
        print("\n💰 REVENUE BREAKDOWN")
        for entry in report.get("revenue_breakdown", []):
            print(f"   {entry.get('source')}: ${entry.get('amount', 0):.2f}")
        
        print("\n" + "=" * 60)


class GoalTracker:
    """Track goals and milestones"""
    
    def __init__(self):
        self.db = AnalyticsDatabase()
    
    def set_goal(self, name: str, target: float, metric_type: str, deadline: str = None):
        """Set a new goal"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute("""
                INSERT INTO goals (name, target_value, metric_type, deadline)
                VALUES (?, ?, ?, ?)
            """, (name, target, metric_type, deadline))
        
        logging.info(f"✅ Goal set: {name} - {target} {metric_type}")
    
    def update_progress(self, name: str, current_value: float):
        """Update goal progress"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute("""
                UPDATE goals SET current_value = ? WHERE name = ?
            """, (current_value, name))
    
    def get_goals(self) -> List[Dict]:
        """Get all active goals"""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM goals WHERE status = 'active'
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def check_milestones(self) -> List[Dict]:
        """Check if any goals have been reached"""
        goals = self.get_goals()
        achieved = []
        
        for goal in goals:
            if goal["current_value"] >= goal["target_value"]:
                achieved.append(goal)
                
                # Mark as completed
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.execute("""
                        UPDATE goals SET status = 'completed' WHERE id = ?
                    """, (goal["id"],))
        
        return achieved


# ==================== UTILITY FUNCTIONS ====================

def collect_all_analytics():
    """Collect analytics from all platforms"""
    collector = PlatformCollector()
    return collector.collect_all()


def generate_daily_report(date: str = None) -> Dict:
    """Generate daily analytics report"""
    generator = ReportGenerator()
    return generator.daily_report(date)


def add_revenue(source: str, amount: float, description: str = ""):
    """Add revenue entry"""
    db = AnalyticsDatabase()
    entry = RevenueEntry(
        date=datetime.now().strftime("%Y-%m-%d"),
        source=source,
        amount=amount,
        description=description
    )
    db.save_revenue(entry)
    logging.info(f"✅ Added revenue: ${amount} from {source}")


# ==================== MAIN ====================

if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Analytics Dashboard")
    parser.add_argument("command", choices=["collect", "report", "add-revenue", "monthly", "dashboard"],
                        help="Command to run")
    parser.add_argument("--source", help="Revenue source")
    parser.add_argument("--amount", type=float, help="Revenue amount")
    parser.add_argument("--year", type=int, help="Year for monthly report")
    parser.add_argument("--month", type=int, help="Month for monthly report")
    
    args = parser.parse_args()
    
    if args.command == "collect":
        results = collect_all_analytics()
        for platform, metrics in results.items():
            print(f"✅ {platform}: {metrics.views} views, {metrics.followers} followers")
    
    elif args.command == "report":
        report = generate_daily_report()
        print(json.dumps(report, indent=2))
    
    elif args.command == "add-revenue":
        if args.source and args.amount:
            add_revenue(args.source, args.amount)
        else:
            print("Usage: analytics_dashboard.py add-revenue --source youtube_adsense --amount 150.00")
    
    elif args.command == "monthly":
        if args.year and args.month:
            generator = ReportGenerator()
            report = generator.monthly_report(args.year, args.month)
            print(json.dumps(report, indent=2))
        else:
            print("Usage: analytics_dashboard.py monthly --year 2026 --month 2")
    
    elif args.command == "dashboard":
        generator = ReportGenerator()
        generator.print_dashboard()
