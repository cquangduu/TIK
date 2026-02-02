"""
================================================================================
MONETIZATION MODULE — Revenue Generation Features
================================================================================
Features:
    1. Gumroad Integration - Sell digital products (PDFs, Anki decks)
    2. Patreon Integration - Premium content access
    3. Affiliate Link Manager - Korean books/courses
    4. Lead Magnet Generator - Free PDFs to collect emails
    5. Analytics Dashboard - Track revenue & growth
================================================================================
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================

# Gumroad
GUMROAD_ACCESS_TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN", "")
GUMROAD_PRODUCT_ID = os.getenv("GUMROAD_PRODUCT_ID", "")

# Patreon
PATREON_ACCESS_TOKEN = os.getenv("PATREON_ACCESS_TOKEN", "")
PATREON_CAMPAIGN_ID = os.getenv("PATREON_CAMPAIGN_ID", "")

# Affiliate Links
AFFILIATE_LINKS = {
    "topik_book_1": {
        "name": "TOPIK Essential Grammar",
        "url": os.getenv("AFFILIATE_TOPIK_BOOK_1", "https://amzn.to/xxx"),
        "commission": 0.04
    },
    "topik_book_2": {
        "name": "TOPIK Vocabulary 5000",
        "url": os.getenv("AFFILIATE_TOPIK_BOOK_2", "https://amzn.to/yyy"),
        "commission": 0.04
    },
    "korean_course": {
        "name": "Talk To Me In Korean",
        "url": os.getenv("AFFILIATE_TTMIK", "https://talktomeinkorean.com/?ref=xxx"),
        "commission": 0.10
    },
    "anki_pro": {
        "name": "AnkiApp Pro",
        "url": os.getenv("AFFILIATE_ANKI", "https://apps.ankiweb.net/"),
        "commission": 0.0
    }
}


# ==================== GUMROAD INTEGRATION ====================

class GumroadManager:
    """
    Manage digital products on Gumroad
    - Auto-generate and upload PDFs
    - Track sales
    - Create discount codes
    """
    
    def __init__(self):
        self.access_token = GUMROAD_ACCESS_TOKEN
        self.api_base = "https://api.gumroad.com/v2"
    
    def is_available(self) -> bool:
        return bool(self.access_token)
    
    def get_products(self) -> List[Dict]:
        """Get all products"""
        if not self.is_available():
            return []
        
        response = requests.get(
            f"{self.api_base}/products",
            params={"access_token": self.access_token}
        )
        
        if response.status_code == 200:
            return response.json().get("products", [])
        return []
    
    def get_sales(self, after_date: str = None) -> List[Dict]:
        """Get sales data"""
        if not self.is_available():
            return []
        
        params = {"access_token": self.access_token}
        if after_date:
            params["after"] = after_date
        
        response = requests.get(f"{self.api_base}/sales", params=params)
        
        if response.status_code == 200:
            return response.json().get("sales", [])
        return []
    
    def create_offer_code(
        self, 
        product_id: str, 
        name: str, 
        amount_off: int = 0,
        percent_off: int = 0,
        max_uses: int = 100
    ) -> Optional[Dict]:
        """Create discount code"""
        if not self.is_available():
            return None
        
        data = {
            "access_token": self.access_token,
            "name": name,
            "max_purchase_count": max_uses
        }
        
        if percent_off > 0:
            data["percent_off"] = percent_off
        elif amount_off > 0:
            data["amount_off_cents"] = amount_off * 100
        
        response = requests.post(
            f"{self.api_base}/products/{product_id}/offer_codes",
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get("offer_code")
        return None


# ==================== LEAD MAGNET GENERATOR ====================

class LeadMagnetGenerator:
    """
    Generate free PDFs to collect email addresses
    - Weekly vocabulary recap
    - TOPIK study guide
    - Grammar cheat sheet
    """
    
    def __init__(self, output_dir: str = "lead_magnets"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_vocab_pdf(self, data: Dict, week_num: int = 1) -> str:
        """Generate weekly vocabulary PDF"""
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        filename = f"TOPIK_Vocab_Week{week_num}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Extract vocabulary
        phase2 = data.get("phase2", {})
        analysis_list = phase2.get("analysis_list", [])
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont("Helvetica-Bold", 24)
        c.drawString(2*cm, height - 2*cm, f"TOPIK Vocabulary - Week {week_num}")
        
        # Subtitle
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 3*cm, "DAILY KOREAN | 데일리 코리안")
        
        # Vocabulary items
        y = height - 5*cm
        c.setFont("Helvetica", 11)
        
        for i, item in enumerate(analysis_list[:20], 1):
            word = item.get("item", "")
            explanation = item.get("professor_explanation", "")[:100]
            
            if y < 3*cm:
                c.showPage()
                y = height - 2*cm
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y, f"{i}. {word}")
            
            c.setFont("Helvetica", 10)
            # Wrap text
            y -= 0.5*cm
            c.drawString(2.5*cm, y, explanation[:80])
            if len(explanation) > 80:
                y -= 0.4*cm
                c.drawString(2.5*cm, y, explanation[80:])
            
            y -= 1*cm
        
        # Footer with CTA
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, 2*cm, "Get daily lessons: topikdaily.com | YouTube: @topikdaily")
        
        c.save()
        logging.info(f"✅ Lead magnet PDF generated: {filepath}")
        return filepath
    
    def generate_grammar_cheatsheet(self, data: Dict) -> str:
        """Generate grammar cheat sheet PDF"""
        # Similar implementation for grammar
        pass
    
    def generate_study_guide(self) -> str:
        """Generate TOPIK study guide PDF"""
        # Comprehensive study guide
        pass


# ==================== ANKI DECK GENERATOR ====================

class AnkiDeckGenerator:
    """
    Generate Anki flashcard decks from vocabulary
    - Export as .apkg file
    - Sell on Gumroad
    """
    
    def __init__(self, output_dir: str = "anki_decks"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_deck(self, data: Dict, deck_name: str = "TOPIK Daily") -> str:
        """Generate Anki deck from vocabulary data"""
        try:
            import genanki
        except ImportError:
            logging.error("❌ genanki not installed. pip install genanki")
            return ""
        
        # Create model (card template)
        model = genanki.Model(
            1607392319,
            'TOPIK Vocabulary',
            fields=[
                {'name': 'Korean'},
                {'name': 'Meaning'},
                {'name': 'Example'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '<div style="font-size: 36px; text-align: center;">{{Korean}}</div>',
                    'afmt': '''{{FrontSide}}
                    <hr id="answer">
                    <div style="font-size: 20px;">{{Meaning}}</div>
                    <br>
                    <div style="font-size: 14px; color: gray;">{{Example}}</div>''',
                },
            ])
        
        # Create deck
        deck = genanki.Deck(
            2059400110,
            deck_name
        )
        
        # Add notes from vocabulary
        phase2 = data.get("phase2", {})
        analysis_list = phase2.get("analysis_list", [])
        
        for item in analysis_list:
            word = item.get("item", "")
            explanation = item.get("professor_explanation", "")
            
            note = genanki.Note(
                model=model,
                fields=[word, explanation, ""]
            )
            deck.add_note(note)
        
        # Export
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"TOPIK_Daily_{date_str}.apkg"
        filepath = os.path.join(self.output_dir, filename)
        
        genanki.Package(deck).write_to_file(filepath)
        logging.info(f"✅ Anki deck generated: {filepath}")
        
        return filepath


# ==================== AFFILIATE LINK MANAGER ====================

class AffiliateLinkManager:
    """
    Manage and track affiliate links
    - Auto-insert into content
    - Track clicks (via redirect)
    - Calculate earnings
    """
    
    def __init__(self):
        self.links = AFFILIATE_LINKS
    
    def get_link(self, key: str) -> str:
        """Get affiliate link by key"""
        link_data = self.links.get(key, {})
        return link_data.get("url", "")
    
    def get_all_links(self) -> Dict:
        """Get all affiliate links"""
        return self.links
    
    def generate_resource_section(self) -> str:
        """Generate HTML/Markdown section with affiliate links"""
        section = """
## 📚 Recommended Resources

Here are some great resources to help you prepare for TOPIK:

"""
        for key, data in self.links.items():
            name = data.get("name", "")
            url = data.get("url", "")
            if url:
                section += f"- [{name}]({url})\n"
        
        section += "\n*Disclosure: Some links are affiliate links. We may earn a commission at no extra cost to you.*\n"
        
        return section
    
    def insert_into_blog(self, blog_content: str) -> str:
        """Insert affiliate section into blog post"""
        resource_section = self.generate_resource_section()
        
        # Insert before footer or at end
        if "## 🎬 Video" in blog_content:
            return blog_content.replace("## 🎬 Video", f"{resource_section}\n## 🎬 Video")
        else:
            return blog_content + "\n" + resource_section


# ==================== SUBSCRIPTION MANAGER ====================

class SubscriptionManager:
    """
    Manage premium subscriptions
    - Patreon integration
    - Ko-fi integration
    - Custom membership site
    """
    
    def __init__(self):
        self.patreon_token = PATREON_ACCESS_TOKEN
        self.campaign_id = PATREON_CAMPAIGN_ID
    
    def get_patrons(self) -> List[Dict]:
        """Get list of Patreon supporters"""
        if not self.patreon_token:
            return []
        
        headers = {"Authorization": f"Bearer {self.patreon_token}"}
        
        response = requests.get(
            f"https://www.patreon.com/api/oauth2/v2/campaigns/{self.campaign_id}/members",
            headers=headers,
            params={
                "include": "user",
                "fields[member]": "full_name,email,patron_status,pledge_cadence"
            }
        )
        
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    
    def get_premium_emails(self) -> List[str]:
        """Get emails of premium subscribers"""
        patrons = self.get_patrons()
        emails = []
        
        for patron in patrons:
            attrs = patron.get("attributes", {})
            if attrs.get("patron_status") == "active_patron":
                email = attrs.get("email")
                if email:
                    emails.append(email)
        
        return emails


# ==================== PREMIUM CONTENT GENERATOR ====================

class PremiumContentGenerator:
    """
    Generate premium-only content for subscribers
    - Extended vocabulary lists
    - Detailed grammar explanations
    - Practice exercises
    - Answer keys
    """
    
    def __init__(self, output_dir: str = "premium_content"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_extended_vocab(self, data: Dict) -> str:
        """Generate extended vocabulary with more examples"""
        phase2 = data.get("phase2", {})
        analysis_list = phase2.get("analysis_list", [])
        
        content = "# 📚 Premium: Extended Vocabulary Guide\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        
        for i, item in enumerate(analysis_list, 1):
            word = item.get("item", "")
            explanation = item.get("professor_explanation", "")
            
            content += f"## {i}. {word}\n\n"
            content += f"{explanation}\n\n"
            content += "### 추가 예문 (Additional Examples)\n\n"
            content += "1. [Example sentence 1]\n"
            content += "2. [Example sentence 2]\n"
            content += "3. [Example sentence 3]\n\n"
            content += "### 연습 문제 (Practice)\n\n"
            content += "Fill in the blank: ____________\n\n"
            content += "---\n\n"
        
        filepath = os.path.join(
            self.output_dir, 
            f"premium_vocab_{datetime.now().strftime('%Y%m%d')}.md"
        )
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def generate_practice_test(self, data: Dict) -> str:
        """Generate TOPIK practice test"""
        # Generate mock test questions
        pass


# ==================== ANALYTICS DASHBOARD ====================

class AnalyticsDashboard:
    """
    Track revenue and growth metrics
    - YouTube Analytics
    - Gumroad Sales
    - Patreon Revenue
    - Blog Traffic
    """
    
    def __init__(self):
        self.gumroad = GumroadManager()
        self.subscriptions = SubscriptionManager()
    
    def get_daily_report(self) -> Dict:
        """Generate daily revenue report"""
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "gumroad_sales": 0,
            "patreon_members": 0,
            "total_revenue": 0
        }
        
        # Gumroad sales
        if self.gumroad.is_available():
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            sales = self.gumroad.get_sales(after_date=yesterday)
            report["gumroad_sales"] = len(sales)
            report["gumroad_revenue"] = sum(
                float(s.get("price", 0)) for s in sales
            )
        
        # Patreon
        patrons = self.subscriptions.get_patrons()
        active = [p for p in patrons if p.get("attributes", {}).get("patron_status") == "active_patron"]
        report["patreon_members"] = len(active)
        
        return report
    
    def send_daily_report(self, email: str):
        """Send daily revenue report via email"""
        report = self.get_daily_report()
        
        subject = f"📊 TOPIK Daily Revenue Report - {report['date']}"
        body = f"""
Daily Revenue Report
====================

Date: {report['date']}

💰 Gumroad Sales: {report.get('gumroad_sales', 0)}
   Revenue: ${report.get('gumroad_revenue', 0):.2f}

🎯 Patreon Members: {report.get('patreon_members', 0)}

📈 Total Estimated Monthly Revenue: $XXX

---
Generated by TOPIK Daily Analytics
"""
        # Send email (use EmailPublisher from social_publisher)
        logging.info(f"📊 Daily report: {report}")
        return report


# ==================== MAIN MONETIZATION MANAGER ====================

class MonetizationManager:
    """Unified manager for all monetization features"""
    
    def __init__(self):
        self.gumroad = GumroadManager()
        self.lead_magnets = LeadMagnetGenerator()
        self.anki = AnkiDeckGenerator()
        self.affiliates = AffiliateLinkManager()
        self.subscriptions = SubscriptionManager()
        self.premium = PremiumContentGenerator()
        self.analytics = AnalyticsDashboard()
    
    def process_daily(self, data: Dict) -> Dict:
        """Run daily monetization tasks"""
        results = {
            "anki_deck": None,
            "lead_magnet": None,
            "premium_content": None,
            "analytics": None
        }
        
        # Generate Anki deck (for Gumroad)
        try:
            results["anki_deck"] = self.anki.generate_deck(data)
        except Exception as e:
            logging.error(f"Anki error: {e}")
        
        # Generate lead magnet
        try:
            week_num = datetime.now().isocalendar()[1]
            results["lead_magnet"] = self.lead_magnets.generate_vocab_pdf(data, week_num)
        except Exception as e:
            logging.error(f"Lead magnet error: {e}")
        
        # Generate premium content
        try:
            results["premium_content"] = self.premium.generate_extended_vocab(data)
        except Exception as e:
            logging.error(f"Premium content error: {e}")
        
        # Get analytics
        try:
            results["analytics"] = self.analytics.get_daily_report()
        except Exception as e:
            logging.error(f"Analytics error: {e}")
        
        return results


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Monetization tools")
    parser.add_argument("--json", default="topik-video/public/final_data.json")
    parser.add_argument("--action", choices=["anki", "pdf", "premium", "report", "all"], default="all")
    
    args = parser.parse_args()
    
    if os.path.exists(args.json):
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        manager = MonetizationManager()
        
        if args.action == "all":
            results = manager.process_daily(data)
            print(f"Results: {results}")
        elif args.action == "anki":
            result = manager.anki.generate_deck(data)
            print(f"Anki deck: {result}")
        elif args.action == "pdf":
            result = manager.lead_magnets.generate_vocab_pdf(data)
            print(f"PDF: {result}")
        elif args.action == "report":
            result = manager.analytics.get_daily_report()
            print(f"Report: {result}")
    else:
        print(f"❌ File not found: {args.json}")
