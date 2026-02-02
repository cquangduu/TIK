"""
================================================================================
PREMIUM CONTENT GATEKEEPER — Paywall & Content Protection
================================================================================
Features:
    1. Content access levels (free, member, premium)
    2. Token-based authentication
    3. Payment integration (Stripe, Ko-fi, Buy Me a Coffee)
    4. Usage tracking & limits
    5. Trial period management
================================================================================
Revenue Potential: $200-2000/month (recurring subscriptions)
================================================================================
"""

import os
import json
import hmac
import hashlib
import secrets
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ==================== CONFIGURATION ====================
PREMIUM_DIR = Path("premium_data")
PREMIUM_DIR.mkdir(exist_ok=True)

DB_PATH = PREMIUM_DIR / "premium.db"

# Access levels
ACCESS_LEVELS = {
    "free": 0,
    "member": 1,    # Email subscriber
    "premium": 2,   # Paid monthly
    "vip": 3,       # Paid yearly / lifetime
}

# Content tiers
CONTENT_TIERS = {
    "daily_vocab": "free",
    "daily_grammar": "free",
    "basic_quiz": "free",
    "anki_deck_basic": "member",
    "pdf_worksheet": "member",
    "advanced_quiz": "premium",
    "anki_deck_premium": "premium",
    "video_lessons": "premium",
    "mock_test": "premium",
    "1on1_review": "vip",
    "private_discord": "vip",
}


class PremiumDatabase:
    """SQLite database for premium content management"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT,
                access_level INTEGER DEFAULT 0,
                api_token TEXT UNIQUE,
                stripe_customer_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Subscriptions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                plan TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'active',
                payment_provider TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Content access log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id TEXT,
                content_tier TEXT,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                granted BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Free trial tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                converted BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # API usage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                endpoint TEXT,
                request_count INTEGER DEFAULT 1,
                date TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, endpoint, date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, password: str = None) -> Tuple[int, str]:
        """Create new user and return user_id and API token"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash password if provided
        hashed_password = None
        if password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Generate API token
        api_token = secrets.token_urlsafe(32)
        
        try:
            cursor.execute("""
                INSERT INTO users (email, hashed_password, api_token)
                VALUES (?, ?, ?)
            """, (email, hashed_password, api_token))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return user_id, api_token
        except sqlite3.IntegrityError:
            conn.close()
            return None, None
    
    def get_user_by_token(self, token: str) -> Optional[Dict]:
        """Get user by API token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, access_level FROM users WHERE api_token = ?
        """, (token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {"id": row[0], "email": row[1], "access_level": row[2]}
        return None
    
    def update_access_level(self, user_id: int, level: int):
        """Update user access level"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET access_level = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (level, user_id))
        
        conn.commit()
        conn.close()
    
    def add_subscription(self, user_id: int, plan: str, price: float, 
                         duration_days: int, provider: str = "stripe") -> int:
        """Add subscription"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, price, payment_provider, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, plan, price, provider, expires_at))
        
        sub_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return sub_id
    
    def log_access(self, user_id: int, content_id: str, content_tier: str, granted: bool):
        """Log content access attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO access_log (user_id, content_id, content_tier, granted)
            VALUES (?, ?, ?, ?)
        """, (user_id, content_id, content_tier, granted))
        
        conn.commit()
        conn.close()
    
    def track_api_usage(self, user_id: int, endpoint: str):
        """Track API usage for rate limiting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            INSERT INTO api_usage (user_id, endpoint, date)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, endpoint, date) DO UPDATE SET
                request_count = request_count + 1
        """, (user_id, endpoint, today))
        
        conn.commit()
        conn.close()
    
    def get_api_usage(self, user_id: int, endpoint: str) -> int:
        """Get API usage count for today"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT request_count FROM api_usage
            WHERE user_id = ? AND endpoint = ? AND date = ?
        """, (user_id, endpoint, today))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0


class AccessController:
    """Control content access based on user level"""
    
    # Rate limits by access level (requests per day)
    RATE_LIMITS = {
        0: 50,      # free
        1: 200,     # member
        2: 1000,    # premium
        3: 10000,   # vip
    }
    
    def __init__(self):
        self.db = PremiumDatabase()
    
    def check_access(self, user_token: str, content_id: str) -> Tuple[bool, str]:
        """Check if user can access content"""
        
        # Get user
        user = self.db.get_user_by_token(user_token)
        if not user:
            return False, "Invalid token"
        
        # Get content tier
        content_tier = CONTENT_TIERS.get(content_id, "premium")
        required_level = ACCESS_LEVELS.get(content_tier, 2)
        
        # Check access level
        if user["access_level"] >= required_level:
            self.db.log_access(user["id"], content_id, content_tier, True)
            return True, "Access granted"
        else:
            self.db.log_access(user["id"], content_id, content_tier, False)
            return False, f"Requires {content_tier} access"
    
    def check_rate_limit(self, user_token: str, endpoint: str) -> Tuple[bool, int]:
        """Check rate limit, returns (allowed, remaining)"""
        
        user = self.db.get_user_by_token(user_token)
        if not user:
            return False, 0
        
        limit = self.RATE_LIMITS.get(user["access_level"], 50)
        usage = self.db.get_api_usage(user["id"], endpoint)
        
        if usage >= limit:
            return False, 0
        
        self.db.track_api_usage(user["id"], endpoint)
        return True, limit - usage - 1


class SubscriptionManager:
    """Manage subscriptions and payments"""
    
    PLANS = {
        "member_monthly": {
            "name": "Member Monthly",
            "price": 0,  # Free
            "level": 1,
            "duration_days": 365 * 10,  # Essentially permanent
        },
        "premium_monthly": {
            "name": "Premium Monthly",
            "price": 4.99,
            "level": 2,
            "duration_days": 30,
        },
        "premium_yearly": {
            "name": "Premium Yearly",
            "price": 39.99,
            "level": 2,
            "duration_days": 365,
        },
        "vip_lifetime": {
            "name": "VIP Lifetime",
            "price": 99.99,
            "level": 3,
            "duration_days": 365 * 99,
        },
    }
    
    def __init__(self):
        self.db = PremiumDatabase()
    
    def subscribe(self, user_id: int, plan_id: str, provider: str = "stripe") -> bool:
        """Add subscription for user"""
        
        if plan_id not in self.PLANS:
            return False
        
        plan = self.PLANS[plan_id]
        
        # Add subscription
        self.db.add_subscription(
            user_id=user_id,
            plan=plan_id,
            price=plan["price"],
            duration_days=plan["duration_days"],
            provider=provider
        )
        
        # Update access level
        self.db.update_access_level(user_id, plan["level"])
        
        return True
    
    def get_pricing_page(self) -> str:
        """Generate pricing page HTML"""
        
        return """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>TOPIK Daily Premium</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; color: white; margin-bottom: 40px; font-size: 2.5rem; }
        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .plan { background: white; border-radius: 20px; padding: 30px; text-align: center; transition: transform 0.3s; }
        .plan:hover { transform: translateY(-10px); }
        .plan.popular { border: 3px solid #667eea; position: relative; }
        .plan.popular::before { content: 'POPULAR'; position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: #667eea; color: white; padding: 4px 20px; border-radius: 20px; font-size: 0.8rem; }
        .plan-name { font-size: 1.5rem; font-weight: bold; margin-bottom: 10px; }
        .plan-price { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .plan-price span { font-size: 1rem; color: #666; }
        .plan-features { list-style: none; margin: 20px 0; text-align: left; }
        .plan-features li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .plan-features li::before { content: '✓'; color: #667eea; margin-right: 10px; }
        .btn { display: block; width: 100%; padding: 15px; background: #667eea; color: white; border: none; border-radius: 10px; font-size: 1.1rem; cursor: pointer; }
        .btn:hover { background: #764ba2; }
        .btn.free { background: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🇰🇷 TOPIK Daily Premium</h1>
        
        <div class="pricing-grid">
            <!-- Free -->
            <div class="plan">
                <div class="plan-name">Free</div>
                <div class="plan-price">$0 <span>/mãi mãi</span></div>
                <ul class="plan-features">
                    <li>Daily vocabulary</li>
                    <li>Daily grammar</li>
                    <li>Basic quizzes</li>
                    <li>Blog access</li>
                </ul>
                <button class="btn free">Bắt đầu miễn phí</button>
            </div>
            
            <!-- Member -->
            <div class="plan">
                <div class="plan-name">Member</div>
                <div class="plan-price">$0 <span>/email signup</span></div>
                <ul class="plan-features">
                    <li>Everything in Free</li>
                    <li>Basic Anki decks</li>
                    <li>PDF worksheets</li>
                    <li>Newsletter tips</li>
                </ul>
                <button class="btn free">Đăng ký email</button>
            </div>
            
            <!-- Premium -->
            <div class="plan popular">
                <div class="plan-name">Premium</div>
                <div class="plan-price">$4.99 <span>/tháng</span></div>
                <ul class="plan-features">
                    <li>Everything in Member</li>
                    <li>Premium Anki decks</li>
                    <li>Video lessons</li>
                    <li>Mock TOPIK tests</li>
                    <li>Advanced quizzes</li>
                </ul>
                <button class="btn">Upgrade Premium</button>
            </div>
            
            <!-- VIP -->
            <div class="plan">
                <div class="plan-name">VIP Lifetime</div>
                <div class="plan-price">$99.99 <span>/một lần</span></div>
                <ul class="plan-features">
                    <li>Everything in Premium</li>
                    <li>1-on-1 writing review</li>
                    <li>Private Discord access</li>
                    <li>Priority support</li>
                    <li>Lifetime updates</li>
                </ul>
                <button class="btn">Get VIP Access</button>
            </div>
        </div>
    </div>
</body>
</html>
"""


class PaymentIntegration:
    """Payment gateway integration"""
    
    def __init__(self):
        self.stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    
    def create_checkout_session(self, plan_id: str, user_email: str) -> Optional[str]:
        """Create Stripe checkout session"""
        
        if not self.stripe_key:
            logging.warning("Stripe key not configured")
            return None
        
        try:
            import stripe
            stripe.api_key = self.stripe_key
            
            plan = SubscriptionManager.PLANS.get(plan_id)
            if not plan:
                return None
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': plan['name'],
                        },
                        'unit_amount': int(plan['price'] * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment' if 'lifetime' in plan_id else 'subscription',
                success_url='https://topikdaily.com/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='https://topikdaily.com/cancel',
                customer_email=user_email,
            )
            
            return session.url
            
        except ImportError:
            logging.error("Stripe library not installed")
            return None
        except Exception as e:
            logging.error(f"Stripe error: {e}")
            return None
    
    def verify_webhook(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify Stripe webhook signature"""
        
        try:
            import stripe
            stripe.Webhook.construct_event(payload, signature, secret)
            return True
        except Exception:
            return False


# ==================== API MIDDLEWARE ====================

def require_auth(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        token = kwargs.get('token') or (args[0] if args else None)
        
        if not token:
            return {"error": "Authentication required", "code": 401}
        
        db = PremiumDatabase()
        user = db.get_user_by_token(token)
        
        if not user:
            return {"error": "Invalid token", "code": 401}
        
        kwargs['user'] = user
        return func(*args, **kwargs)
    
    return wrapper


def require_level(min_level: int):
    """Decorator to require minimum access level"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = kwargs.get('user', {})
            
            if user.get('access_level', 0) < min_level:
                level_name = [k for k, v in ACCESS_LEVELS.items() if v == min_level]
                return {"error": f"Requires {level_name[0] if level_name else 'higher'} access", "code": 403}
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ==================== UTILITY FUNCTIONS ====================

def create_user(email: str, password: str = None) -> Dict:
    """Create new user"""
    db = PremiumDatabase()
    user_id, token = db.create_user(email, password)
    
    if user_id:
        return {"user_id": user_id, "api_token": token}
    return {"error": "Email already exists"}


def check_content_access(token: str, content_id: str) -> Dict:
    """Check if user can access content"""
    controller = AccessController()
    allowed, message = controller.check_access(token, content_id)
    
    return {"allowed": allowed, "message": message}


# ==================== MAIN ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Premium Content Gatekeeper")
    parser.add_argument("--create-user", metavar="EMAIL", help="Create new user")
    parser.add_argument("--check-access", nargs=2, metavar=("TOKEN", "CONTENT"), help="Check access")
    parser.add_argument("--pricing", action="store_true", help="Generate pricing page")
    
    args = parser.parse_args()
    
    if args.create_user:
        result = create_user(args.create_user)
        print(json.dumps(result, indent=2))
    elif args.check_access:
        result = check_content_access(args.check_access[0], args.check_access[1])
        print(json.dumps(result, indent=2))
    elif args.pricing:
        manager = SubscriptionManager()
        html = manager.get_pricing_page()
        
        output_file = PREMIUM_DIR / "pricing.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {output_file}")
    else:
        parser.print_help()
