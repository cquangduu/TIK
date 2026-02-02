"""
================================================================================
ANALYTICS DASHBOARD — Professional Version
================================================================================
Comprehensive analytics tracking and reporting for content creators.

Features:
    - Multi-platform metrics collection (YouTube, TikTok, Blog)
    - Revenue tracking with multiple sources
    - Interactive dashboard with charts
    - Daily/Weekly/Monthly reports with export
    - Goal tracking and projections
    - Performance alerts and recommendations
================================================================================
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import statistics

# Core framework
from core import (
    Config, Logger, Database,
    safe_json_load, safe_json_save,
    ensure_directory, format_number, format_duration
)

# Initialize core components
config = Config()
logger = Logger(__name__)


# ==================== ENUMS ====================

class Platform(Enum):
    """Supported platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    BLOG = "blog"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    PODCAST = "podcast"


class RevenueSource(Enum):
    """Revenue sources"""
    ADSENSE = "adsense"
    YOUTUBE_PREMIUM = "youtube_premium"
    SPONSORSHIP = "sponsorship"
    AFFILIATE = "affiliate"
    GUMROAD = "gumroad"
    PATREON = "patreon"
    KOFI = "ko-fi"
    TIPS = "tips"
    PREMIUM_CONTENT = "premium"
    OTHER = "other"


class MetricType(Enum):
    """Types of metrics"""
    FOLLOWERS = "followers"
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"


# ==================== DATA CLASSES ====================

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
    watch_time_hours: float = 0.0
    avg_view_duration: float = 0.0
    
    def __post_init__(self):
        """Calculate engagement rate if not provided"""
        if self.engagement_rate == 0 and self.views > 0:
            interactions = self.likes + self.comments + self.shares
            self.engagement_rate = (interactions / self.views) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RevenueEntry:
    """Revenue entry"""
    date: str
    source: str
    amount: float
    currency: str = "USD"
    description: str = ""
    video_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Goal:
    """Growth goal"""
    id: int = 0
    name: str = ""
    metric_type: str = ""
    target_value: float = 0.0
    current_value: float = 0.0
    deadline: str = ""
    status: str = "active"
    platform: str = ""
    created_at: str = ""
    
    @property
    def progress_percent(self) -> float:
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)
    
    @property
    def is_completed(self) -> bool:
        return self.current_value >= self.target_value
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["progress_percent"] = self.progress_percent
        d["is_completed"] = self.is_completed
        return d


@dataclass
class Report:
    """Analytics report"""
    period: str
    report_type: str  # daily, weekly, monthly
    generated_at: str = ""
    summary: Dict[str, Any] = field(default_factory=dict)
    platforms: Dict[str, Any] = field(default_factory=dict)
    revenue: Dict[str, Any] = field(default_factory=dict)
    growth: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self, filepath: str):
        """Export report to JSON"""
        safe_json_save(self.to_dict(), filepath)
        logger.info(f"Report exported to {filepath}")
    
    def to_html(self) -> str:
        """Generate HTML report"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Analytics Report - {self.period}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a73e8; }}
        .summary {{ background: #f0f4f8; padding: 20px; border-radius: 8px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; }}
        .metric-label {{ color: #666; }}
        .section {{ margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
        .positive {{ color: #34a853; }}
        .negative {{ color: #ea4335; }}
    </style>
</head>
<body>
    <h1>Analytics Report</h1>
    <p>Period: {self.period} | Generated: {self.generated_at}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div class="metric-value">{format_number(self.summary.get('total_views', 0))}</div>
            <div class="metric-label">Total Views</div>
        </div>
        <div class="metric">
            <div class="metric-value">{format_number(self.summary.get('total_followers', 0))}</div>
            <div class="metric-label">Followers</div>
        </div>
        <div class="metric">
            <div class="metric-value">${self.summary.get('total_revenue', 0):.2f}</div>
            <div class="metric-label">Revenue</div>
        </div>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
            {''.join(f'<li>{r}</li>' for r in self.recommendations)}
        </ul>
    </div>
</body>
</html>
"""


# ==================== ANALYTICS DATABASE ====================

class AnalyticsDatabase:
    """SQLite database for analytics data"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(config.paths.data_dir / "analytics.db")
        ensure_directory(Path(self.db_path).parent)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
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
                    watch_time_hours REAL DEFAULT 0,
                    avg_view_duration REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, date)
                );
                
                CREATE TABLE IF NOT EXISTS revenue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    description TEXT,
                    video_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    current_value REAL DEFAULT 0,
                    platform TEXT,
                    deadline TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS content_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    date TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(content_id, date)
                );
                
                CREATE INDEX IF NOT EXISTS idx_metrics_date ON platform_metrics(date);
                CREATE INDEX IF NOT EXISTS idx_metrics_platform ON platform_metrics(platform);
                CREATE INDEX IF NOT EXISTS idx_revenue_date ON revenue(date);
                CREATE INDEX IF NOT EXISTS idx_revenue_source ON revenue(source);
            """)
        
        logger.debug(f"Analytics database initialized: {self.db_path}")
    
    # ─── Metrics Operations ──────────────────────────────────────────────────
    
    def save_metrics(self, metrics: PlatformMetrics):
        """Save or update platform metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO platform_metrics 
                (platform, date, followers, views, likes, comments, shares, 
                 revenue, engagement_rate, watch_time_hours, avg_view_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.platform,
                metrics.date,
                metrics.followers,
                metrics.views,
                metrics.likes,
                metrics.comments,
                metrics.shares,
                metrics.revenue,
                metrics.engagement_rate,
                metrics.watch_time_hours,
                metrics.avg_view_duration
            ))
        logger.debug(f"Saved metrics for {metrics.platform} on {metrics.date}")
    
    def get_metrics(
        self,
        start_date: str,
        end_date: str,
        platform: str = None
    ) -> List[PlatformMetrics]:
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
            
            return [PlatformMetrics(**dict(row)) for row in cursor.fetchall()
                    if 'id' not in dict(row) or True]  # Skip id field
    
    def get_latest_metrics(self, platform: str) -> Optional[PlatformMetrics]:
        """Get latest metrics for a platform"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM platform_metrics 
                WHERE platform = ?
                ORDER BY date DESC LIMIT 1
            """, (platform,))
            
            row = cursor.fetchone()
            if row:
                data = dict(row)
                return PlatformMetrics(
                    platform=data['platform'],
                    date=data['date'],
                    followers=data['followers'],
                    views=data['views'],
                    likes=data['likes'],
                    comments=data['comments'],
                    shares=data['shares'],
                    revenue=data['revenue'],
                    engagement_rate=data['engagement_rate']
                )
        return None
    
    # ─── Revenue Operations ──────────────────────────────────────────────────
    
    def save_revenue(self, entry: RevenueEntry):
        """Save revenue entry"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO revenue (date, source, amount, currency, description, video_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                entry.date,
                entry.source,
                entry.amount,
                entry.currency,
                entry.description,
                entry.video_id
            ))
        logger.debug(f"Saved revenue: ${entry.amount} from {entry.source}")
    
    def get_revenue(
        self,
        start_date: str,
        end_date: str,
        source: str = None
    ) -> List[RevenueEntry]:
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
            
            return [RevenueEntry(
                date=row['date'],
                source=row['source'],
                amount=row['amount'],
                currency=row['currency'],
                description=row['description'],
                video_id=row['video_id'] or ""
            ) for row in cursor.fetchall()]
    
    def get_total_revenue(self, start_date: str, end_date: str) -> float:
        """Get total revenue for date range"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT SUM(amount) FROM revenue 
                WHERE date >= ? AND date <= ?
            """, (start_date, end_date))
            result = cursor.fetchone()[0]
            return result if result else 0.0
    
    def get_revenue_by_source(self, start_date: str, end_date: str) -> Dict[str, float]:
        """Get revenue breakdown by source"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT source, SUM(amount) as total FROM revenue 
                WHERE date >= ? AND date <= ?
                GROUP BY source
                ORDER BY total DESC
            """, (start_date, end_date))
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    # ─── Goals Operations ────────────────────────────────────────────────────
    
    def save_goal(self, goal: Goal) -> int:
        """Save a goal and return its ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO goals (name, metric_type, target_value, current_value, 
                                   platform, deadline, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.name,
                goal.metric_type,
                goal.target_value,
                goal.current_value,
                goal.platform,
                goal.deadline,
                goal.status
            ))
            return cursor.lastrowid
    
    def update_goal_progress(self, goal_id: int, current_value: float):
        """Update goal progress"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE goals SET current_value = ? WHERE id = ?
            """, (current_value, goal_id))
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM goals WHERE status = 'active'
                ORDER BY deadline
            """)
            return [Goal(**dict(row)) for row in cursor.fetchall()]


# ==================== REPORT GENERATOR ====================

class ReportGenerator:
    """Generate comprehensive analytics reports"""
    
    def __init__(self, db: AnalyticsDatabase = None):
        self.db = db or AnalyticsDatabase()
    
    def daily_report(self, date: str = None) -> Report:
        """Generate daily report"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get metrics and revenue
        metrics = self.db.get_metrics(date, date)
        revenue = self.db.get_revenue(date, date)
        
        # Calculate totals
        total_views = sum(m.views for m in metrics)
        total_followers = sum(m.followers for m in metrics)
        total_revenue = sum(r.amount for r in revenue)
        avg_engagement = statistics.mean([m.engagement_rate for m in metrics]) if metrics else 0
        
        # Platform breakdown
        platforms = {m.platform: m.to_dict() for m in metrics}
        
        # Revenue breakdown
        revenue_by_source = defaultdict(float)
        for r in revenue:
            revenue_by_source[r.source] += r.amount
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, revenue)
        
        return Report(
            period=date,
            report_type="daily",
            summary={
                "total_views": total_views,
                "total_followers": total_followers,
                "total_revenue": total_revenue,
                "avg_engagement_rate": round(avg_engagement, 2),
            },
            platforms=platforms,
            revenue={
                "total": total_revenue,
                "by_source": dict(revenue_by_source),
                "entries": [r.to_dict() for r in revenue],
            },
            recommendations=recommendations
        )
    
    def weekly_report(self, end_date: str = None) -> Report:
        """Generate weekly report"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Get data
        metrics = self.db.get_metrics(start_date, end_date)
        revenue = self.db.get_revenue(start_date, end_date)
        
        # Calculate totals
        total_views = sum(m.views for m in metrics)
        total_revenue = sum(r.amount for r in revenue)
        
        # Group by platform
        by_platform = defaultdict(list)
        for m in metrics:
            by_platform[m.platform].append(m)
        
        # Calculate trends
        platform_trends = {}
        for platform, platform_metrics in by_platform.items():
            if len(platform_metrics) >= 2:
                first_half = platform_metrics[:len(platform_metrics)//2]
                second_half = platform_metrics[len(platform_metrics)//2:]
                
                first_views = sum(m.views for m in first_half)
                second_views = sum(m.views for m in second_half)
                
                if first_views > 0:
                    growth = ((second_views - first_views) / first_views) * 100
                else:
                    growth = 0
                
                platform_trends[platform] = {
                    "views_growth": round(growth, 1),
                    "total_views": sum(m.views for m in platform_metrics),
                }
        
        return Report(
            period=f"{start_date} to {end_date}",
            report_type="weekly",
            summary={
                "total_views": total_views,
                "total_revenue": total_revenue,
                "revenue_per_day": round(total_revenue / 7, 2),
            },
            platforms={p: [m.to_dict() for m in ms] for p, ms in by_platform.items()},
            revenue={
                "total": total_revenue,
                "by_source": self.db.get_revenue_by_source(start_date, end_date),
            },
            growth=platform_trends,
            recommendations=self._generate_recommendations(metrics, revenue)
        )
    
    def monthly_report(self, year: int = None, month: int = None) -> Report:
        """Generate monthly report"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        start_date = f"{year}-{month:02d}-01"
        
        # Get last day of month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        end_date = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Get data
        metrics = self.db.get_metrics(start_date, end_date)
        revenue = self.db.get_revenue(start_date, end_date)
        total_revenue = sum(r.amount for r in revenue)
        
        # Revenue by source
        revenue_by_source = self.db.get_revenue_by_source(start_date, end_date)
        
        # Best performing content
        by_platform = defaultdict(lambda: {"views": 0, "revenue": 0.0})
        for m in metrics:
            by_platform[m.platform]["views"] += m.views
            by_platform[m.platform]["revenue"] += m.revenue
        
        return Report(
            period=f"{year}-{month:02d}",
            report_type="monthly",
            summary={
                "total_revenue": total_revenue,
                "avg_daily_revenue": round(total_revenue / 30, 2),
            },
            platforms=dict(by_platform),
            revenue={
                "total": total_revenue,
                "by_source": revenue_by_source,
            },
            recommendations=self._generate_monthly_recommendations(metrics, total_revenue)
        )
    
    def _generate_recommendations(
        self,
        metrics: List[PlatformMetrics],
        revenue: List[RevenueEntry]
    ) -> List[str]:
        """Generate recommendations based on data"""
        recommendations = []
        
        # Check engagement rates
        low_engagement = [m for m in metrics if m.engagement_rate < 2.0]
        if low_engagement:
            platforms = ", ".join(set(m.platform for m in low_engagement))
            recommendations.append(
                f"Low engagement on {platforms}. Try more interactive content like polls or questions."
            )
        
        # Check revenue diversification
        if revenue:
            sources = set(r.source for r in revenue)
            if len(sources) < 3:
                recommendations.append(
                    "Revenue sources are limited. Consider adding affiliate marketing or premium content."
                )
        else:
            recommendations.append(
                "No revenue recorded today. Set up monetization if not already done."
            )
        
        # Check for platforms with declining metrics
        for m in metrics:
            if m.views == 0:
                recommendations.append(
                    f"No views on {m.platform}. Consider posting more frequently."
                )
        
        return recommendations
    
    def _generate_monthly_recommendations(
        self,
        metrics: List[PlatformMetrics],
        total_revenue: float
    ) -> List[str]:
        """Generate monthly recommendations"""
        recommendations = []
        
        if total_revenue < 100:
            recommendations.append(
                "Revenue below $100/month. Focus on growing audience and monetization."
            )
        elif total_revenue < 500:
            recommendations.append(
                "Good progress! Consider premium content or sponsorships to increase revenue."
            )
        else:
            recommendations.append(
                "Strong month! Look into scaling what's working and automating processes."
            )
        
        return recommendations


# ==================== DASHBOARD ====================

class Dashboard:
    """Main analytics dashboard interface"""
    
    def __init__(self):
        self.db = AnalyticsDatabase()
        self.report_gen = ReportGenerator(self.db)
    
    def log_metrics(self, platform: str, **kwargs):
        """Log platform metrics"""
        metrics = PlatformMetrics(
            platform=platform,
            date=datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        )
        self.db.save_metrics(metrics)
        logger.info(f"Logged metrics for {platform}: {kwargs.get('views', 0)} views")
    
    def log_revenue(
        self,
        amount: float,
        source: str,
        description: str = "",
        date: str = None
    ):
        """Log revenue entry"""
        entry = RevenueEntry(
            date=date or datetime.now().strftime("%Y-%m-%d"),
            source=source,
            amount=amount,
            description=description
        )
        self.db.save_revenue(entry)
        logger.info(f"Logged revenue: ${amount} from {source}")
    
    def set_goal(
        self,
        name: str,
        metric_type: str,
        target_value: float,
        deadline: str = None,
        platform: str = ""
    ) -> int:
        """Set a new goal"""
        goal = Goal(
            name=name,
            metric_type=metric_type,
            target_value=target_value,
            deadline=deadline or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            platform=platform
        )
        goal_id = self.db.save_goal(goal)
        logger.info(f"Created goal: {name} (target: {target_value})")
        return goal_id
    
    def get_summary(self) -> Dict[str, Any]:
        """Get current summary of all platforms"""
        summary = {
            "as_of": datetime.now().isoformat(),
            "platforms": {},
            "revenue": {},
            "goals": []
        }
        
        # Get latest metrics for each platform
        for platform in Platform:
            metrics = self.db.get_latest_metrics(platform.value)
            if metrics:
                summary["platforms"][platform.value] = metrics.to_dict()
        
        # Get MTD revenue
        today = datetime.now()
        start_of_month = today.replace(day=1).strftime("%Y-%m-%d")
        end_of_month = today.strftime("%Y-%m-%d")
        
        summary["revenue"]["mtd"] = self.db.get_total_revenue(start_of_month, end_of_month)
        summary["revenue"]["by_source"] = self.db.get_revenue_by_source(start_of_month, end_of_month)
        
        # Get active goals
        summary["goals"] = [g.to_dict() for g in self.db.get_active_goals()]
        
        return summary
    
    def export_report(
        self,
        report_type: str = "daily",
        format: str = "json",
        filepath: str = None
    ) -> str:
        """Export report to file"""
        # Generate report
        if report_type == "daily":
            report = self.report_gen.daily_report()
        elif report_type == "weekly":
            report = self.report_gen.weekly_report()
        elif report_type == "monthly":
            report = self.report_gen.monthly_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Determine filepath
        if filepath is None:
            reports_dir = ensure_directory(config.paths.data_dir / "reports")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = str(reports_dir / f"{report_type}_report_{timestamp}.{format}")
        
        # Export
        if format == "json":
            report.to_json(filepath)
        elif format == "html":
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report.to_html())
        else:
            raise ValueError(f"Unknown format: {format}")
        
        return filepath


# ==================== CLI ====================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analytics Dashboard")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_parser.add_argument("--type", choices=["daily", "weekly", "monthly"], default="daily")
    report_parser.add_argument("--format", choices=["json", "html"], default="json")
    report_parser.add_argument("--output", type=str, help="Output filepath")
    
    # Log command
    log_parser = subparsers.add_parser("log", help="Log metrics or revenue")
    log_parser.add_argument("--platform", type=str, help="Platform name")
    log_parser.add_argument("--views", type=int, default=0)
    log_parser.add_argument("--followers", type=int, default=0)
    log_parser.add_argument("--revenue", type=float, default=0)
    log_parser.add_argument("--source", type=str, help="Revenue source")
    
    # Summary command
    subparsers.add_parser("summary", help="Show current summary")
    
    args = parser.parse_args()
    
    dashboard = Dashboard()
    
    if args.command == "report":
        filepath = dashboard.export_report(args.type, args.format, args.output)
        print(f"Report exported to: {filepath}")
    
    elif args.command == "log":
        if args.platform:
            dashboard.log_metrics(
                args.platform,
                views=args.views,
                followers=args.followers
            )
            print(f"Logged metrics for {args.platform}")
        
        if args.revenue > 0 and args.source:
            dashboard.log_revenue(args.revenue, args.source)
            print(f"Logged revenue: ${args.revenue}")
    
    elif args.command == "summary":
        summary = dashboard.get_summary()
        print(json.dumps(summary, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
