"""
================================================================================
AFFILIATE MANAGER — Manage Affiliate Links & Commissions
================================================================================
Features:
    1. Track affiliate links (Amazon, Coupang, Gmarket)
    2. Auto-insert affiliate links in content
    3. Track clicks & conversions
    4. Generate affiliate reports
    5. Recommend products to promote
================================================================================
Revenue Potential: $100-1000/month (affiliate commissions)
================================================================================
"""

import os
import json
import re
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ==================== CONFIGURATION ====================
AFFILIATE_DIR = Path("affiliate_data")
AFFILIATE_DIR.mkdir(exist_ok=True)

DB_PATH = AFFILIATE_DIR / "affiliate.db"


# ==================== PRODUCT DATABASE ====================

KOREAN_LEARNING_PRODUCTS = {
    "books": [
        {
            "name": "TOPIK Essential Grammar",
            "korean_name": "TOPIK 필수 문법",
            "category": "grammar",
            "level": "beginner",
            "amazon_asin": "B09XXXXXX1",
            "coupang_id": "12345678",
            "price_usd": 25.99,
            "commission_rate": 0.04,
        },
        {
            "name": "Korean Vocabulary 2000",
            "korean_name": "한국어 어휘 2000",
            "category": "vocabulary",
            "level": "intermediate",
            "amazon_asin": "B09XXXXXX2",
            "coupang_id": "12345679",
            "price_usd": 19.99,
            "commission_rate": 0.04,
        },
        {
            "name": "TOPIK Writing Guide",
            "korean_name": "TOPIK 쓰기 가이드",
            "category": "writing",
            "level": "advanced",
            "amazon_asin": "B09XXXXXX3",
            "coupang_id": "12345680",
            "price_usd": 22.99,
            "commission_rate": 0.04,
        },
    ],
    "electronics": [
        {
            "name": "Samsung Galaxy Buds",
            "category": "audio",
            "amazon_asin": "B0BXXXXXX4",
            "coupang_id": "23456789",
            "price_usd": 149.99,
            "commission_rate": 0.03,
            "keywords": ["listening", "podcast", "audio"],
        },
        {
            "name": "Kindle Paperwhite",
            "category": "ereader",
            "amazon_asin": "B0BXXXXXX5",
            "coupang_id": "23456790",
            "price_usd": 139.99,
            "commission_rate": 0.03,
            "keywords": ["reading", "ebook", "study"],
        },
    ],
    "subscriptions": [
        {
            "name": "Italki Korean Lessons",
            "category": "tutoring",
            "affiliate_url": "https://italki.com/affshare?ref=XXXXX",
            "price_usd": 15.00,  # per lesson
            "commission_rate": 0.10,
            "keywords": ["speaking", "tutor", "practice"],
        },
        {
            "name": "LingQ Premium",
            "category": "app",
            "affiliate_url": "https://lingq.com/ref/XXXXX",
            "price_usd": 12.99,  # per month
            "commission_rate": 0.15,
            "keywords": ["reading", "listening", "vocabulary"],
        },
    ],
}


class AffiliateDatabase:
    """SQLite database for affiliate tracking"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS affiliate_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                affiliate_url TEXT NOT NULL,
                short_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # Clicks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER,
                source TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (link_id) REFERENCES affiliate_links(id)
            )
        """)
        
        # Conversions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id INTEGER,
                order_amount REAL,
                commission_amount REAL,
                converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (link_id) REFERENCES affiliate_links(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_link(self, product_name: str, platform: str, affiliate_url: str, short_url: str = None) -> int:
        """Add new affiliate link"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO affiliate_links (product_name, platform, affiliate_url, short_url)
            VALUES (?, ?, ?, ?)
        """, (product_name, platform, affiliate_url, short_url))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return link_id
    
    def track_click(self, link_id: int, source: str = "unknown"):
        """Track link click"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clicks (link_id, source)
            VALUES (?, ?)
        """, (link_id, source))
        
        conn.commit()
        conn.close()
    
    def add_conversion(self, link_id: int, order_amount: float, commission_amount: float):
        """Add conversion record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversions (link_id, order_amount, commission_amount)
            VALUES (?, ?, ?)
        """, (link_id, order_amount, commission_amount))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, days: int = 30) -> Dict:
        """Get affiliate stats for period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total clicks
        cursor.execute("""
            SELECT COUNT(*) FROM clicks WHERE clicked_at >= ?
        """, (start_date,))
        total_clicks = cursor.fetchone()[0]
        
        # Total conversions
        cursor.execute("""
            SELECT COUNT(*), SUM(commission_amount), SUM(order_amount)
            FROM conversions WHERE converted_at >= ?
        """, (start_date,))
        row = cursor.fetchone()
        total_conversions = row[0] or 0
        total_commission = row[1] or 0
        total_sales = row[2] or 0
        
        # Top products
        cursor.execute("""
            SELECT al.product_name, COUNT(c.id) as clicks
            FROM affiliate_links al
            LEFT JOIN clicks c ON al.id = c.link_id AND c.clicked_at >= ?
            GROUP BY al.id
            ORDER BY clicks DESC
            LIMIT 5
        """, (start_date,))
        top_products = cursor.fetchall()
        
        conn.close()
        
        return {
            "period_days": days,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
            "total_commission": total_commission,
            "total_sales": total_sales,
            "top_products": [{"name": p[0], "clicks": p[1]} for p in top_products],
        }


class AffiliateManager:
    """Manage affiliate links and insertions"""
    
    def __init__(self, affiliate_tag: str = "topikdaily-21"):
        self.affiliate_tag = affiliate_tag
        self.db = AffiliateDatabase()
        
        # Platform URL templates
        self.url_templates = {
            "amazon": "https://www.amazon.com/dp/{asin}?tag={tag}",
            "amazon_jp": "https://www.amazon.co.jp/dp/{asin}?tag={tag}",
            "coupang": "https://www.coupang.com/vp/products/{id}?itemsCount=1&searchId=XXXX&vendorItemId={id}&sourceType=srp&clickEventId=XXXX&campaignId=XXXXX",
        }
    
    def generate_amazon_link(self, asin: str, marketplace: str = "com") -> str:
        """Generate Amazon affiliate link"""
        if marketplace == "jp":
            return f"https://www.amazon.co.jp/dp/{asin}?tag={self.affiliate_tag}"
        return f"https://www.amazon.com/dp/{asin}?tag={self.affiliate_tag}"
    
    def generate_coupang_link(self, product_id: str) -> str:
        """Generate Coupang affiliate link (placeholder)"""
        # Coupang requires Coupang Partners registration
        return f"https://link.coupang.com/re/XXXXX?lId={product_id}"
    
    def find_products_for_content(self, content: str, level: str = "all") -> List[Dict]:
        """Find relevant products for content"""
        
        content_lower = content.lower()
        recommended = []
        
        # Check keywords
        for category, products in KOREAN_LEARNING_PRODUCTS.items():
            for product in products:
                score = 0
                
                # Check keywords
                keywords = product.get("keywords", [])
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        score += 1
                
                # Check category match
                if product.get("category", "").lower() in content_lower:
                    score += 2
                
                # Check level match
                if level != "all" and product.get("level", "") == level:
                    score += 1
                
                if score > 0:
                    recommended.append({
                        **product,
                        "relevance_score": score,
                    })
        
        # Sort by relevance
        recommended.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return recommended[:3]  # Top 3
    
    def insert_affiliate_links(self, content: str, max_links: int = 3) -> str:
        """Insert affiliate links into content"""
        
        # Find product mentions
        products = self.find_products_for_content(content)
        
        if not products:
            return content
        
        # Create affiliate section
        affiliate_section = "\n\n---\n\n## 📚 Tài liệu đề xuất\n\n"
        
        for product in products[:max_links]:
            name = product.get("name", "")
            korean_name = product.get("korean_name", name)
            price = product.get("price_usd", 0)
            
            # Generate link
            if product.get("amazon_asin"):
                url = self.generate_amazon_link(product["amazon_asin"])
            elif product.get("affiliate_url"):
                url = product["affiliate_url"]
            else:
                continue
            
            affiliate_section += f"- [{korean_name}]({url}) - ${price:.2f}\n"
        
        affiliate_section += "\n*Links này là affiliate links. Chúng tôi có thể nhận hoa hồng khi bạn mua qua link.*\n"
        
        return content + affiliate_section
    
    def generate_product_review(self, product: Dict) -> str:
        """Generate product review content"""
        
        return f"""
## 📖 Review: {product.get('name', '')}

### Tổng quan
{product.get('korean_name', '')} là một tài liệu tuyệt vời cho người học tiếng Hàn.

### Ưu điểm
- ✅ Nội dung dễ hiểu
- ✅ Phù hợp với level {product.get('level', 'beginner')}
- ✅ Có nhiều ví dụ thực tế

### Nhược điểm
- ⚠️ Cần kết hợp với tài liệu khác

### Giá
💰 ${product.get('price_usd', 0):.2f}

### Link mua
[Mua ngay trên Amazon]({self.generate_amazon_link(product.get('amazon_asin', ''))})

---
*Đây là affiliate link. Chúng tôi nhận hoa hồng khi bạn mua qua link này.*
"""


class AffiliateReporter:
    """Generate affiliate reports"""
    
    def __init__(self):
        self.db = AffiliateDatabase()
    
    def generate_monthly_report(self) -> str:
        """Generate monthly affiliate report"""
        
        stats = self.db.get_stats(days=30)
        
        report = f"""
# 📊 Báo cáo Affiliate - Tháng này

**Thời gian:** 30 ngày gần nhất
**Ngày tạo:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📈 Tổng quan

| Metric | Giá trị |
|--------|---------|
| Tổng clicks | {stats['total_clicks']:,} |
| Tổng conversions | {stats['total_conversions']:,} |
| Conversion rate | {stats['conversion_rate']:.1f}% |
| Tổng doanh số | ${stats['total_sales']:,.2f} |
| **Tổng commission** | **${stats['total_commission']:,.2f}** |

---

## 🏆 Top sản phẩm

"""
        for i, product in enumerate(stats.get("top_products", []), 1):
            report += f"{i}. {product['name']} - {product['clicks']} clicks\n"
        
        report += """

---

## 💡 Đề xuất

1. Thêm nhiều affiliate links vào blog posts
2. Tạo review video cho top sản phẩm
3. Tối ưu placement của links

---

화이팅! 💪
"""
        return report


# ==================== UTILITY FUNCTIONS ====================

def setup_affiliate_links():
    """Setup initial affiliate links"""
    manager = AffiliateManager()
    db = AffiliateDatabase()
    
    for category, products in KOREAN_LEARNING_PRODUCTS.items():
        for product in products:
            if product.get("amazon_asin"):
                url = manager.generate_amazon_link(product["amazon_asin"])
                db.add_link(product["name"], "amazon", url)
                print(f"Added: {product['name']}")


def get_affiliate_stats():
    """Get affiliate statistics"""
    db = AffiliateDatabase()
    return db.get_stats()


# ==================== MAIN ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Affiliate Manager")
    parser.add_argument("--setup", action="store_true", help="Setup initial links")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_affiliate_links()
    elif args.stats:
        stats = get_affiliate_stats()
        print(json.dumps(stats, indent=2))
    elif args.report:
        reporter = AffiliateReporter()
        print(reporter.generate_monthly_report())
    else:
        parser.print_help()
