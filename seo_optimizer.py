"""
================================================================================
SEO OPTIMIZER — Maximize Blog Traffic & Revenue
================================================================================
Features:
    1. Auto-generate SEO meta tags
    2. Keyword research & optimization
    3. Internal linking suggestions
    4. Schema.org structured data
    5. Sitemap & robots.txt generator
    6. Performance analytics
================================================================================
Revenue Impact: 2-5x more organic traffic = more ad revenue
================================================================================
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ==================== CONFIGURATION ====================
BLOG_OUTPUT_DIR = "blog_output"
SITEMAP_FILE = os.path.join(BLOG_OUTPUT_DIR, "sitemap.xml")
ROBOTS_FILE = os.path.join(BLOG_OUTPUT_DIR, "robots.txt")

# Target keywords for TOPIK content
PRIMARY_KEYWORDS = [
    "học tiếng Hàn",
    "TOPIK",
    "từ vựng tiếng Hàn",
    "ngữ pháp tiếng Hàn",
    "luyện thi TOPIK",
    "Korean vocabulary",
    "Korean grammar",
    "TOPIK preparation",
]

LONG_TAIL_KEYWORDS = [
    "học tiếng Hàn cho người mới bắt đầu",
    "từ vựng TOPIK II",
    "ngữ pháp TOPIK 54",
    "cách viết bài văn TOPIK",
    "luyện nghe tiếng Hàn",
    "tin tức Hàn Quốc song ngữ",
]


class SEOOptimizer:
    """
    Tối ưu SEO cho blog TOPIK Daily.
    """
    
    def __init__(self, site_url: str = "https://topikdaily.com"):
        self.site_url = site_url.rstrip("/")
        self.blog_dir = Path(BLOG_OUTPUT_DIR)
    
    def generate_meta_tags(self, data: Dict) -> Dict[str, str]:
        """Generate SEO meta tags for a blog post"""
        
        title = data.get("title", "Bài học TOPIK hôm nay")
        description = data.get("description", "")
        keywords = data.get("keywords", PRIMARY_KEYWORDS[:5])
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        image = data.get("image", f"{self.site_url}/og-image.jpg")
        
        # Generate description if not provided
        if not description:
            news_vi = data.get("news_vi", "")[:150]
            description = f"Bài học TOPIK ngày {date}. {news_vi}..."
        
        # Optimize title for SEO (50-60 chars)
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Meta description (150-160 chars)
        if len(description) > 160:
            description = description[:157] + "..."
        
        return {
            "title": title,
            "description": description,
            "keywords": ", ".join(keywords) if isinstance(keywords, list) else keywords,
            "canonical": f"{self.site_url}/posts/{date}",
            "og_title": title,
            "og_description": description,
            "og_image": image,
            "og_url": f"{self.site_url}/posts/{date}",
            "og_type": "article",
            "twitter_card": "summary_large_image",
            "twitter_title": title,
            "twitter_description": description,
            "twitter_image": image,
            "article_published": date,
            "article_author": "TOPIK Daily",
        }
    
    def generate_schema_article(self, data: Dict) -> Dict:
        """Generate Schema.org Article structured data"""
        
        title = data.get("title", "Bài học TOPIK")
        description = data.get("description", "")
        date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        image = data.get("image", f"{self.site_url}/og-image.jpg")
        
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "image": image,
            "datePublished": date,
            "dateModified": date,
            "author": {
                "@type": "Organization",
                "name": "TOPIK Daily",
                "url": self.site_url
            },
            "publisher": {
                "@type": "Organization",
                "name": "TOPIK Daily",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.site_url}/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.site_url}/posts/{date}"
            }
        }
    
    def generate_schema_course(self) -> Dict:
        """Generate Schema.org Course structured data for the learning content"""
        
        return {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": "TOPIK Daily - Học tiếng Hàn mỗi ngày",
            "description": "Khóa học tiếng Hàn miễn phí với bài học hàng ngày, từ vựng, ngữ pháp và luyện thi TOPIK.",
            "provider": {
                "@type": "Organization",
                "name": "TOPIK Daily",
                "url": self.site_url
            },
            "educationalLevel": "Beginner to Advanced",
            "inLanguage": ["ko", "vi"],
            "isAccessibleForFree": True,
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
            }
        }
    
    def generate_schema_faq(self, faqs: List[Dict]) -> Dict:
        """Generate Schema.org FAQ structured data"""
        
        faq_items = []
        for faq in faqs:
            faq_items.append({
                "@type": "Question",
                "name": faq.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.get("answer", "")
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        }
    
    def generate_sitemap(self, posts: List[Dict]) -> str:
        """Generate sitemap.xml"""
        
        sitemap_entries = []
        
        # Homepage
        sitemap_entries.append(f"""
    <url>
        <loc>{self.site_url}/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>""")
        
        # Posts
        for post in posts:
            date = post.get("date", "")
            sitemap_entries.append(f"""
    <url>
        <loc>{self.site_url}/posts/{date}</loc>
        <lastmod>{date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>""")
        
        # Static pages
        static_pages = ["vocabulary", "grammar", "quiz", "about", "premium"]
        for page in static_pages:
            sitemap_entries.append(f"""
    <url>
        <loc>{self.site_url}/{page}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>""")
        
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(sitemap_entries)}
</urlset>"""
        
        # Save
        with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
            f.write(sitemap)
        
        logging.info(f"✅ Generated sitemap: {SITEMAP_FILE}")
        return sitemap
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt"""
        
        robots = f"""# TOPIK Daily robots.txt
User-agent: *
Allow: /

# Sitemap
Sitemap: {self.site_url}/sitemap.xml

# Disallow admin/private areas
Disallow: /admin/
Disallow: /api/
Disallow: /private/

# Allow all search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Yandex
Allow: /
"""
        
        # Save
        with open(ROBOTS_FILE, "w", encoding="utf-8") as f:
            f.write(robots)
        
        logging.info(f"✅ Generated robots.txt: {ROBOTS_FILE}")
        return robots
    
    def optimize_content(self, content: str, target_keyword: str) -> str:
        """Optimize content for target keyword"""
        
        # Check keyword density (aim for 1-2%)
        word_count = len(content.split())
        keyword_count = content.lower().count(target_keyword.lower())
        density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        # Suggestions
        suggestions = []
        
        if density < 0.5:
            suggestions.append(f"⚠️ Keyword '{target_keyword}' density too low ({density:.1f}%). Add more mentions.")
        elif density > 3:
            suggestions.append(f"⚠️ Keyword '{target_keyword}' density too high ({density:.1f}%). Reduce to avoid spam.")
        else:
            suggestions.append(f"✅ Keyword density OK ({density:.1f}%)")
        
        # Check for heading structure
        if not re.search(r'#\s+', content):
            suggestions.append("⚠️ No H1 heading found. Add main title with #")
        
        if not re.search(r'##\s+', content):
            suggestions.append("⚠️ No H2 headings found. Add subheadings with ##")
        
        # Check for links
        if not re.search(r'\[.*?\]\(.*?\)', content):
            suggestions.append("⚠️ No links found. Add internal/external links.")
        
        # Check content length
        if word_count < 300:
            suggestions.append(f"⚠️ Content too short ({word_count} words). Aim for 1000+ words.")
        elif word_count >= 1000:
            suggestions.append(f"✅ Content length OK ({word_count} words)")
        
        return "\n".join(suggestions)
    
    def suggest_internal_links(self, current_post: Dict, all_posts: List[Dict]) -> List[Dict]:
        """Suggest internal links to other relevant posts"""
        
        current_keywords = set(current_post.get("keywords", []))
        current_topic = current_post.get("topic", "")
        current_date = current_post.get("date", "")
        
        suggestions = []
        
        for post in all_posts:
            if post.get("date") == current_date:
                continue
            
            post_keywords = set(post.get("keywords", []))
            overlap = current_keywords.intersection(post_keywords)
            
            if overlap or post.get("topic") == current_topic:
                suggestions.append({
                    "url": f"{self.site_url}/posts/{post.get('date')}",
                    "title": post.get("title", ""),
                    "relevance": len(overlap),
                    "anchor_text": f"Xem bài học ngày {post.get('date')}"
                })
        
        # Sort by relevance
        suggestions.sort(key=lambda x: x["relevance"], reverse=True)
        
        return suggestions[:5]  # Top 5 suggestions
    
    def generate_html_head(self, meta_tags: Dict, schema_data: Dict = None) -> str:
        """Generate complete HTML head section with SEO"""
        
        html = f"""
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>{meta_tags.get('title', '')}</title>
    <meta name="title" content="{meta_tags.get('title', '')}">
    <meta name="description" content="{meta_tags.get('description', '')}">
    <meta name="keywords" content="{meta_tags.get('keywords', '')}">
    <link rel="canonical" href="{meta_tags.get('canonical', '')}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="{meta_tags.get('og_type', 'article')}">
    <meta property="og:url" content="{meta_tags.get('og_url', '')}">
    <meta property="og:title" content="{meta_tags.get('og_title', '')}">
    <meta property="og:description" content="{meta_tags.get('og_description', '')}">
    <meta property="og:image" content="{meta_tags.get('og_image', '')}">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="{meta_tags.get('twitter_card', 'summary_large_image')}">
    <meta property="twitter:url" content="{meta_tags.get('og_url', '')}">
    <meta property="twitter:title" content="{meta_tags.get('twitter_title', '')}">
    <meta property="twitter:description" content="{meta_tags.get('twitter_description', '')}">
    <meta property="twitter:image" content="{meta_tags.get('twitter_image', '')}">
    
    <!-- Article -->
    <meta property="article:published_time" content="{meta_tags.get('article_published', '')}">
    <meta property="article:author" content="{meta_tags.get('article_author', '')}">
"""
        
        if schema_data:
            html += f"""
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(schema_data, ensure_ascii=False, indent=2)}
    </script>
"""
        
        html += """
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
</head>"""
        
        return html


class KeywordResearcher:
    """
    Nghiên cứu keywords cho content optimization.
    """
    
    def __init__(self):
        self.primary_keywords = PRIMARY_KEYWORDS
        self.long_tail = LONG_TAIL_KEYWORDS
    
    def get_keywords_for_topic(self, topic: str) -> List[str]:
        """Get relevant keywords for a topic"""
        
        topic_keywords = {
            "vocabulary": [
                "từ vựng tiếng Hàn",
                "Korean vocabulary",
                "học từ vựng TOPIK",
                "từ vựng TOPIK II",
                "flashcard tiếng Hàn",
            ],
            "grammar": [
                "ngữ pháp tiếng Hàn",
                "Korean grammar",
                "cấu trúc ngữ pháp TOPIK",
                "học ngữ pháp tiếng Hàn",
            ],
            "writing": [
                "viết văn TOPIK",
                "TOPIK writing",
                "bài văn mẫu TOPIK 54",
                "cách viết bài văn tiếng Hàn",
            ],
            "listening": [
                "nghe tiếng Hàn",
                "Korean listening",
                "luyện nghe TOPIK",
            ],
            "news": [
                "tin tức Hàn Quốc",
                "Korea news",
                "tin tức song ngữ Hàn Việt",
            ],
        }
        
        # Find matching topic
        for key, keywords in topic_keywords.items():
            if key in topic.lower():
                return keywords + self.primary_keywords[:3]
        
        return self.primary_keywords
    
    def generate_title_variations(self, base_title: str, keyword: str) -> List[str]:
        """Generate SEO-friendly title variations"""
        
        return [
            f"{keyword} - {base_title}",
            f"{base_title} | {keyword}",
            f"[{datetime.now().year}] {base_title} - {keyword}",
            f"{base_title} ({keyword})",
            f"Học {keyword}: {base_title}",
        ]


# ==================== UTILITY FUNCTIONS ====================

def optimize_blog_post(data_file: str = "topik-video/public/final_data.json") -> Dict:
    """Optimize a blog post for SEO"""
    
    if not os.path.exists(data_file):
        logging.error(f"❌ Data file not found: {data_file}")
        return {}
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    optimizer = SEOOptimizer()
    
    # Generate meta tags
    meta_tags = optimizer.generate_meta_tags(data)
    
    # Generate schema
    schema = optimizer.generate_schema_article(data)
    
    # Generate HTML head
    html_head = optimizer.generate_html_head(meta_tags, schema)
    
    return {
        "meta_tags": meta_tags,
        "schema": schema,
        "html_head": html_head
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    optimizer = SEOOptimizer("https://topikdaily.com")
    
    # Test
    sample_data = {
        "title": "Bài học TOPIK ngày 02/02/2026 - Từ vựng về du lịch",
        "date": "2026-02-02",
        "topic": "vocabulary",
        "news_vi": "Hôm nay chúng ta sẽ học về từ vựng du lịch trong tiếng Hàn."
    }
    
    meta = optimizer.generate_meta_tags(sample_data)
    print("Meta tags:", json.dumps(meta, indent=2, ensure_ascii=False))
    
    schema = optimizer.generate_schema_article(sample_data)
    print("\nSchema:", json.dumps(schema, indent=2, ensure_ascii=False))
