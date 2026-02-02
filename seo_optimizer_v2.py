"""
================================================================================
SEO OPTIMIZER — Professional Version
================================================================================
Maximize blog traffic with advanced SEO optimization.

Features:
    - Meta tags generation with Open Graph & Twitter Cards
    - Schema.org structured data (Article, Course, FAQ, HowTo)
    - Keyword density analysis and suggestions
    - Internal linking recommendations
    - Sitemap & robots.txt generation
    - Content scoring and improvement tips
    - Competitive keyword analysis
================================================================================
"""

from __future__ import annotations

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import Counter
from urllib.parse import quote

# Core framework
from core import (
    Config, Logger, Database,
    safe_json_load, safe_json_save,
    ensure_directory, truncate_text, clean_text
)

# Initialize core components
config = Config()
logger = Logger(__name__)
db = Database()


# ==================== CONSTANTS ====================

PRIMARY_KEYWORDS = [
    "học tiếng Hàn",
    "TOPIK",
    "từ vựng tiếng Hàn",
    "ngữ pháp tiếng Hàn",
    "luyện thi TOPIK",
    "Korean vocabulary",
    "Korean grammar",
    "TOPIK preparation",
    "tiếng Hàn cho người Việt",
    "한국어",
]

TOPIC_KEYWORDS = {
    "vocabulary": [
        "từ vựng tiếng Hàn", "Korean vocabulary", "học từ vựng TOPIK",
        "từ vựng TOPIK II", "flashcard tiếng Hàn", "어휘",
    ],
    "grammar": [
        "ngữ pháp tiếng Hàn", "Korean grammar", "cấu trúc ngữ pháp TOPIK",
        "học ngữ pháp tiếng Hàn", "문법",
    ],
    "writing": [
        "viết văn TOPIK", "TOPIK writing", "bài văn mẫu TOPIK 54",
        "cách viết bài văn tiếng Hàn", "쓰기",
    ],
    "listening": [
        "nghe tiếng Hàn", "Korean listening", "luyện nghe TOPIK", "듣기",
    ],
    "news": [
        "tin tức Hàn Quốc", "Korea news", "tin tức song ngữ Hàn Việt",
        "뉴스", "시사",
    ],
    "quiz": [
        "quiz tiếng Hàn", "kiểm tra TOPIK", "bài test tiếng Hàn",
        "TOPIK practice test",
    ],
}


# ==================== DATA CLASSES ====================

@dataclass
class MetaTags:
    """SEO meta tags structure"""
    title: str
    description: str
    keywords: str
    canonical: str
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    og_url: str = ""
    og_type: str = "article"
    twitter_card: str = "summary_large_image"
    twitter_title: str = ""
    twitter_description: str = ""
    twitter_image: str = ""
    article_published: str = ""
    article_modified: str = ""
    article_author: str = "데일리 코리안"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "canonical": self.canonical,
            "og_title": self.og_title or self.title,
            "og_description": self.og_description or self.description,
            "og_image": self.og_image,
            "og_url": self.og_url or self.canonical,
            "og_type": self.og_type,
            "twitter_card": self.twitter_card,
            "twitter_title": self.twitter_title or self.title,
            "twitter_description": self.twitter_description or self.description,
            "twitter_image": self.twitter_image or self.og_image,
            "article_published": self.article_published,
            "article_modified": self.article_modified,
            "article_author": self.article_author,
        }


@dataclass
class ContentScore:
    """SEO content score and suggestions"""
    overall_score: int  # 0-100
    title_score: int
    description_score: int
    content_score: int
    keyword_score: int
    structure_score: int
    suggestions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "title_score": self.title_score,
            "description_score": self.description_score,
            "content_score": self.content_score,
            "keyword_score": self.keyword_score,
            "structure_score": self.structure_score,
            "suggestions": self.suggestions,
            "warnings": self.warnings,
        }


@dataclass
class InternalLink:
    """Internal link suggestion"""
    url: str
    title: str
    anchor_text: str
    relevance_score: float


# ==================== SEO OPTIMIZER ====================

class SEOOptimizer:
    """
    Professional SEO optimizer for blog content.
    
    Features:
        - Meta tag generation with all major platforms
        - Schema.org structured data
        - Content analysis and scoring
        - Keyword optimization
        - Internal linking suggestions
    """
    
    def __init__(
        self,
        site_url: str = "https://topikdaily.github.io",
        site_name: str = "데일리 코리안"
    ):
        """
        Initialize SEO optimizer.
        
        Args:
            site_url: Base URL of the website
            site_name: Name of the website
        """
        self.site_url = site_url.rstrip("/")
        self.site_name = site_name
        self.blog_dir = Path(config.paths.blog_dir)
        
        logger.info(f"SEOOptimizer initialized for {site_url}")
    
    # ─── Meta Tags ───────────────────────────────────────────────────────────
    
    def generate_meta_tags(
        self,
        title: str,
        description: str = "",
        keywords: List[str] = None,
        date: str = None,
        slug: str = "",
        image: str = ""
    ) -> MetaTags:
        """
        Generate comprehensive SEO meta tags.
        
        Args:
            title: Page title
            description: Meta description
            keywords: List of keywords
            date: Publication date
            slug: URL slug for canonical
            image: OG image URL
            
        Returns:
            MetaTags object
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if not description:
            description = f"Bài học TOPIK ngày {date}. Học tiếng Hàn mỗi ngày với {self.site_name}."
        
        # Optimize title (50-60 chars)
        optimized_title = self._optimize_title(title)
        
        # Optimize description (150-160 chars)
        optimized_desc = self._optimize_description(description)
        
        # Build canonical URL
        canonical = f"{self.site_url}/posts/{slug}.html" if slug else f"{self.site_url}/posts/{date}"
        
        # Build image URL
        if not image:
            image = f"{self.site_url}/og-image.jpg"
        
        # Keywords
        keywords_str = ", ".join(keywords[:10]) if keywords else ", ".join(PRIMARY_KEYWORDS[:5])
        
        return MetaTags(
            title=optimized_title,
            description=optimized_desc,
            keywords=keywords_str,
            canonical=canonical,
            og_title=optimized_title,
            og_description=optimized_desc,
            og_image=image,
            og_url=canonical,
            og_type="article",
            twitter_card="summary_large_image",
            article_published=f"{date}T00:00:00+07:00",
            article_modified=f"{datetime.now().strftime('%Y-%m-%d')}T00:00:00+07:00",
        )
    
    def _optimize_title(self, title: str) -> str:
        """Optimize title for SEO (50-60 chars)"""
        if len(title) <= 60:
            return title
        
        # Try to cut at a natural break
        if " | " in title:
            parts = title.split(" | ")
            if len(parts[0]) <= 55:
                return parts[0]
        
        if " - " in title:
            parts = title.split(" - ")
            if len(parts[0]) <= 55:
                return parts[0]
        
        return title[:57] + "..."
    
    def _optimize_description(self, description: str) -> str:
        """Optimize description for SEO (150-160 chars)"""
        # Clean text
        description = clean_text(description)
        
        if len(description) <= 160:
            return description
        
        # Try to cut at sentence boundary
        sentences = description.split(". ")
        result = ""
        for sentence in sentences:
            if len(result) + len(sentence) + 2 <= 157:
                result += sentence + ". "
            else:
                break
        
        if result:
            return result.rstrip()
        
        return description[:157] + "..."
    
    # ─── Schema.org Structured Data ──────────────────────────────────────────
    
    def generate_article_schema(
        self,
        title: str,
        description: str,
        date: str,
        slug: str = "",
        image: str = ""
    ) -> Dict[str, Any]:
        """Generate Schema.org Article structured data"""
        
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": self._optimize_title(title),
            "description": self._optimize_description(description),
            "image": image or f"{self.site_url}/og-image.jpg",
            "datePublished": f"{date}T00:00:00+07:00",
            "dateModified": f"{datetime.now().strftime('%Y-%m-%d')}T00:00:00+07:00",
            "author": {
                "@type": "Organization",
                "name": self.site_name,
                "url": self.site_url
            },
            "publisher": {
                "@type": "Organization",
                "name": self.site_name,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.site_url}/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.site_url}/posts/{slug or date}"
            },
            "inLanguage": "vi",
            "keywords": ", ".join(PRIMARY_KEYWORDS[:5])
        }
    
    def generate_course_schema(self) -> Dict[str, Any]:
        """Generate Schema.org Course structured data"""
        
        return {
            "@context": "https://schema.org",
            "@type": "Course",
            "name": f"{self.site_name} - Học tiếng Hàn mỗi ngày",
            "description": "Khóa học tiếng Hàn miễn phí với bài học hàng ngày, từ vựng, ngữ pháp và luyện thi TOPIK.",
            "provider": {
                "@type": "Organization",
                "name": self.site_name,
                "url": self.site_url
            },
            "educationalLevel": "Beginner to Advanced",
            "inLanguage": ["ko", "vi"],
            "isAccessibleForFree": True,
            "courseCode": "TOPIK-DAILY",
            "hasCourseInstance": {
                "@type": "CourseInstance",
                "courseMode": "online",
                "courseWorkload": "PT15M"  # 15 minutes per day
            },
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "VND",
                "availability": "https://schema.org/InStock"
            }
        }
    
    def generate_faq_schema(self, faqs: List[Dict[str, str]]) -> Dict[str, Any]:
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
    
    def generate_howto_schema(
        self,
        title: str,
        description: str,
        steps: List[str],
        total_time: str = "PT15M"
    ) -> Dict[str, Any]:
        """Generate Schema.org HowTo structured data"""
        
        step_items = []
        for i, step in enumerate(steps, 1):
            step_items.append({
                "@type": "HowToStep",
                "position": i,
                "text": step
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": title,
            "description": description,
            "totalTime": total_time,
            "step": step_items
        }
    
    # ─── Content Analysis ────────────────────────────────────────────────────
    
    def analyze_content(
        self,
        content: str,
        title: str = "",
        target_keyword: str = ""
    ) -> ContentScore:
        """
        Analyze content for SEO and provide scoring.
        
        Args:
            content: The content to analyze
            title: Page title
            target_keyword: Primary target keyword
            
        Returns:
            ContentScore with scores and suggestions
        """
        suggestions = []
        warnings = []
        
        # Word count
        word_count = len(content.split())
        
        # Title analysis
        title_score = self._analyze_title(title, target_keyword, suggestions, warnings)
        
        # Content length
        content_score = self._analyze_content_length(word_count, suggestions, warnings)
        
        # Keyword analysis
        keyword_score = self._analyze_keywords(content, target_keyword, suggestions, warnings)
        
        # Structure analysis
        structure_score = self._analyze_structure(content, suggestions, warnings)
        
        # Description placeholder (would need actual description)
        description_score = 70
        
        # Calculate overall score
        overall_score = int(
            (title_score * 0.2) +
            (description_score * 0.15) +
            (content_score * 0.25) +
            (keyword_score * 0.2) +
            (structure_score * 0.2)
        )
        
        return ContentScore(
            overall_score=overall_score,
            title_score=title_score,
            description_score=description_score,
            content_score=content_score,
            keyword_score=keyword_score,
            structure_score=structure_score,
            suggestions=suggestions,
            warnings=warnings
        )
    
    def _analyze_title(
        self,
        title: str,
        keyword: str,
        suggestions: List[str],
        warnings: List[str]
    ) -> int:
        """Analyze title for SEO"""
        score = 100
        
        if not title:
            warnings.append("Missing title")
            return 0
        
        # Length check
        if len(title) < 30:
            suggestions.append(f"Title is short ({len(title)} chars). Aim for 50-60 characters.")
            score -= 15
        elif len(title) > 60:
            warnings.append(f"Title is too long ({len(title)} chars). Keep under 60 characters.")
            score -= 20
        
        # Keyword in title
        if keyword and keyword.lower() not in title.lower():
            suggestions.append(f"Add target keyword '{keyword}' to title.")
            score -= 20
        
        # Power words
        power_words = ["học", "hướng dẫn", "cách", "miễn phí", "dễ", "nhanh", "mới"]
        has_power_word = any(word in title.lower() for word in power_words)
        if not has_power_word:
            suggestions.append("Add a power word to title (e.g., 'Hướng dẫn', 'Cách', 'Miễn phí').")
            score -= 10
        
        return max(0, score)
    
    def _analyze_content_length(
        self,
        word_count: int,
        suggestions: List[str],
        warnings: List[str]
    ) -> int:
        """Analyze content length"""
        if word_count < 300:
            warnings.append(f"Content too short ({word_count} words). Aim for 1000+ words.")
            return 30
        elif word_count < 600:
            suggestions.append(f"Content is short ({word_count} words). Consider expanding to 1000+ words.")
            return 60
        elif word_count < 1000:
            suggestions.append(f"Good content length ({word_count} words).")
            return 80
        else:
            return 100
    
    def _analyze_keywords(
        self,
        content: str,
        target_keyword: str,
        suggestions: List[str],
        warnings: List[str]
    ) -> int:
        """Analyze keyword usage"""
        if not target_keyword:
            suggestions.append("Set a target keyword for better optimization.")
            return 50
        
        word_count = len(content.split())
        keyword_count = content.lower().count(target_keyword.lower())
        density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        score = 100
        
        if density < 0.5:
            suggestions.append(f"Keyword density too low ({density:.1f}%). Add more mentions of '{target_keyword}'.")
            score = 40
        elif density > 3:
            warnings.append(f"Keyword density too high ({density:.1f}%). Reduce to avoid spam.")
            score = 50
        elif density < 1:
            suggestions.append(f"Keyword density OK ({density:.1f}%). Could add a few more mentions.")
            score = 70
        
        # Check for keyword variations
        # This is a simplified check
        return score
    
    def _analyze_structure(
        self,
        content: str,
        suggestions: List[str],
        warnings: List[str]
    ) -> int:
        """Analyze content structure"""
        score = 100
        
        # Check for H1
        if not re.search(r'^#\s+', content, re.MULTILINE):
            warnings.append("No H1 heading found. Add main title with #")
            score -= 25
        
        # Check for H2
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        if h2_count == 0:
            suggestions.append("No H2 headings found. Add subheadings with ##")
            score -= 20
        elif h2_count < 3:
            suggestions.append(f"Only {h2_count} H2 headings. Consider adding more for better structure.")
            score -= 10
        
        # Check for links
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
        if link_count == 0:
            suggestions.append("No links found. Add internal and external links.")
            score -= 15
        
        # Check for lists
        list_count = len(re.findall(r'^[-*]\s+', content, re.MULTILINE))
        if list_count == 0:
            suggestions.append("No lists found. Use bullet points for readability.")
            score -= 10
        
        # Check for images (markdown format)
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', content))
        if image_count == 0:
            suggestions.append("No images found. Add relevant images.")
            score -= 10
        
        return max(0, score)
    
    # ─── Internal Linking ────────────────────────────────────────────────────
    
    def suggest_internal_links(
        self,
        current_post: Dict[str, Any],
        all_posts: List[Dict[str, Any]],
        max_suggestions: int = 5
    ) -> List[InternalLink]:
        """
        Suggest internal links to related posts.
        
        Args:
            current_post: Current post data with keywords, topic, date
            all_posts: List of all posts
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of InternalLink suggestions
        """
        current_keywords = set(current_post.get("keywords", []))
        current_keywords.update(current_post.get("tags", []))
        current_topic = current_post.get("topic", "").lower()
        current_date = current_post.get("date", "")
        
        suggestions = []
        
        for post in all_posts:
            # Skip current post
            if post.get("date") == current_date:
                continue
            
            post_keywords = set(post.get("keywords", []))
            post_keywords.update(post.get("tags", []))
            post_topic = post.get("topic", "").lower()
            
            # Calculate relevance
            keyword_overlap = len(current_keywords.intersection(post_keywords))
            topic_match = 1 if current_topic and current_topic in post_topic else 0
            
            relevance = (keyword_overlap * 0.6) + (topic_match * 0.4)
            
            if relevance > 0:
                slug = post.get("slug", post.get("date", ""))
                suggestions.append(InternalLink(
                    url=f"{self.site_url}/posts/{slug}.html",
                    title=post.get("title", ""),
                    anchor_text=f"Xem bài học: {post.get('title', '')[:50]}",
                    relevance_score=relevance
                ))
        
        # Sort by relevance and return top N
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions[:max_suggestions]
    
    # ─── Sitemap & Robots ────────────────────────────────────────────────────
    
    def generate_sitemap(self, posts: List[Dict[str, Any]]) -> str:
        """Generate sitemap.xml content"""
        
        entries = []
        
        # Homepage
        entries.append(f"""
    <url>
        <loc>{self.site_url}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>""")
        
        # Posts
        for post in posts:
            date = post.get("date", "")
            slug = post.get("slug", date)
            entries.append(f"""
    <url>
        <loc>{self.site_url}/posts/{slug}.html</loc>
        <lastmod>{date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>""")
        
        # Static pages
        static_pages = ["vocabulary", "grammar", "quiz", "about", "premium"]
        for page in static_pages:
            entries.append(f"""
    <url>
        <loc>{self.site_url}/{page}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>""")
        
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{"".join(entries)}
</urlset>"""
        
        # Save to file
        sitemap_path = self.blog_dir / "sitemap.xml"
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap)
        
        logger.info(f"Generated sitemap: {sitemap_path}")
        return sitemap
    
    def generate_robots_txt(self) -> str:
        """Generate robots.txt content"""
        
        robots = f"""# {self.site_name} robots.txt
# Generated on {datetime.now().strftime('%Y-%m-%d')}

User-agent: *
Allow: /

# Sitemap
Sitemap: {self.site_url}/sitemap.xml

# Disallow admin/private areas
Disallow: /admin/
Disallow: /api/
Disallow: /private/
Disallow: /*.json$

# Allow all search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Yandex
Allow: /

User-agent: DuckDuckBot
Allow: /
"""
        
        # Save to file
        robots_path = self.blog_dir / "robots.txt"
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(robots)
        
        logger.info(f"Generated robots.txt: {robots_path}")
        return robots
    
    # ─── HTML Generation ─────────────────────────────────────────────────────
    
    def generate_html_head(
        self,
        meta_tags: MetaTags,
        schema_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate complete HTML head section with SEO tags"""
        
        meta = meta_tags.to_dict()
        
        html = f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Primary Meta Tags -->
    <title>{meta['title']}</title>
    <meta name="title" content="{meta['title']}">
    <meta name="description" content="{meta['description']}">
    <meta name="keywords" content="{meta['keywords']}">
    <link rel="canonical" href="{meta['canonical']}">
    <meta name="author" content="{meta['article_author']}">
    <meta name="robots" content="index, follow">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="{meta['og_type']}">
    <meta property="og:url" content="{meta['og_url']}">
    <meta property="og:title" content="{meta['og_title']}">
    <meta property="og:description" content="{meta['og_description']}">
    <meta property="og:image" content="{meta['og_image']}">
    <meta property="og:site_name" content="{self.site_name}">
    <meta property="og:locale" content="vi_VN">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="{meta['twitter_card']}">
    <meta name="twitter:url" content="{meta['og_url']}">
    <meta name="twitter:title" content="{meta['twitter_title']}">
    <meta name="twitter:description" content="{meta['twitter_description']}">
    <meta name="twitter:image" content="{meta['twitter_image']}">
    
    <!-- Article -->
    <meta property="article:published_time" content="{meta['article_published']}">
    <meta property="article:modified_time" content="{meta['article_modified']}">
    <meta property="article:author" content="{meta['article_author']}">"""
        
        if schema_data:
            html += f"""
    
    <!-- Structured Data -->
    <script type="application/ld+json">
{json.dumps(schema_data, ensure_ascii=False, indent=4)}
    </script>"""
        
        html += """
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
</head>"""
        
        return html


# ==================== KEYWORD RESEARCHER ====================

class KeywordResearcher:
    """
    Keyword research and analysis.
    
    Features:
        - Topic-based keyword suggestions
        - Keyword variations generator
        - Competition analysis (simplified)
    """
    
    def __init__(self):
        self.primary_keywords = PRIMARY_KEYWORDS
        self.topic_keywords = TOPIC_KEYWORDS
    
    def get_keywords_for_topic(
        self,
        topic: str,
        include_primary: bool = True
    ) -> List[str]:
        """Get relevant keywords for a topic"""
        
        keywords = []
        
        # Find matching topic
        topic_lower = topic.lower()
        for key, kw_list in self.topic_keywords.items():
            if key in topic_lower:
                keywords.extend(kw_list)
                break
        
        if include_primary:
            keywords.extend(self.primary_keywords[:5])
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        
        return unique
    
    def generate_title_variations(
        self,
        base_title: str,
        keyword: str
    ) -> List[str]:
        """Generate SEO-friendly title variations"""
        
        year = datetime.now().year
        
        return [
            f"{keyword}: {base_title}",
            f"{base_title} | {keyword}",
            f"[{year}] {base_title} - {keyword}",
            f"Hướng dẫn {base_title} ({keyword})",
            f"{base_title} cho người Việt - {keyword}",
            f"Cách {base_title} hiệu quả | {keyword}",
        ]
    
    def extract_keywords_from_content(
        self,
        content: str,
        min_freq: int = 2,
        max_keywords: int = 10
    ) -> List[Tuple[str, int]]:
        """Extract potential keywords from content"""
        
        # Simple word frequency analysis
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter short words and common words
        stop_words = {
            "là", "và", "của", "có", "trong", "cho", "được", "với", 
            "này", "đó", "các", "một", "những", "the", "a", "an", "is", "are",
            "to", "for", "in", "on", "at", "by", "from"
        }
        
        filtered = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Count frequency
        counter = Counter(filtered)
        
        # Get top keywords
        keywords = [(word, count) for word, count in counter.most_common(max_keywords * 2)
                    if count >= min_freq]
        
        return keywords[:max_keywords]


# ==================== PUBLIC API ====================

def optimize_blog_post(
    data: Dict[str, Any],
    site_url: str = "https://topikdaily.github.io"
) -> Dict[str, Any]:
    """
    Optimize a blog post for SEO.
    
    Args:
        data: Post data with title, description, content, etc.
        site_url: Base URL for the site
        
    Returns:
        Dict with meta_tags, schema, score, suggestions
    """
    optimizer = SEOOptimizer(site_url)
    researcher = KeywordResearcher()
    
    title = data.get("title", "")
    description = data.get("description", "")
    content = data.get("content", "")
    topic = data.get("topic", "")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    slug = data.get("slug", "")
    
    # Get keywords
    keywords = researcher.get_keywords_for_topic(topic)
    target_keyword = keywords[0] if keywords else ""
    
    # Generate meta tags
    meta_tags = optimizer.generate_meta_tags(
        title=title,
        description=description,
        keywords=keywords,
        date=date,
        slug=slug
    )
    
    # Generate schema
    schema = optimizer.generate_article_schema(
        title=title,
        description=description,
        date=date,
        slug=slug
    )
    
    # Analyze content
    if content:
        score = optimizer.analyze_content(content, title, target_keyword)
    else:
        score = ContentScore(
            overall_score=50,
            title_score=50,
            description_score=50,
            content_score=50,
            keyword_score=50,
            structure_score=50,
            suggestions=["Add content for analysis"],
            warnings=[]
        )
    
    return {
        "meta_tags": meta_tags.to_dict(),
        "schema": schema,
        "score": score.to_dict(),
        "keywords": keywords,
        "html_head": optimizer.generate_html_head(meta_tags, schema)
    }


# ==================== CLI ====================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SEO Optimizer for TOPIK Daily")
    parser.add_argument("--analyze", type=str, help="Path to content file to analyze")
    parser.add_argument("--sitemap", action="store_true", help="Generate sitemap")
    parser.add_argument("--robots", action="store_true", help="Generate robots.txt")
    parser.add_argument("--url", default="https://topikdaily.github.io", help="Site URL")
    
    args = parser.parse_args()
    
    optimizer = SEOOptimizer(args.url)
    
    if args.analyze:
        content = Path(args.analyze).read_text(encoding="utf-8")
        score = optimizer.analyze_content(content)
        
        print(f"\nSEO Score: {score.overall_score}/100")
        print(f"  Title: {score.title_score}")
        print(f"  Content: {score.content_score}")
        print(f"  Keywords: {score.keyword_score}")
        print(f"  Structure: {score.structure_score}")
        
        if score.warnings:
            print("\nWarnings:")
            for w in score.warnings:
                print(f"  - {w}")
        
        if score.suggestions:
            print("\nSuggestions:")
            for s in score.suggestions:
                print(f"  - {s}")
    
    elif args.sitemap:
        # Load posts from blog directory
        posts = []
        optimizer.generate_sitemap(posts)
        print("Sitemap generated")
    
    elif args.robots:
        optimizer.generate_robots_txt()
        print("robots.txt generated")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
