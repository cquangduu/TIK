"""
================================================================================
BLOG GENERATOR MODULE — Professional Version
================================================================================
Auto-generate SEO-optimized blog posts from TOPIK data.

Features:
    - Generate Markdown/HTML from final_data.json
    - SEO-optimized structure with meta tags
    - Multi-language support (KO/VI)
    - Automatic sitemap and RSS generation
    - GitHub Pages / Netlify / Vercel deployment ready
================================================================================
"""

from __future__ import annotations

import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from urllib.parse import quote

# Core framework
from core import (
    Config, Logger, Database,
    safe_json_load, safe_json_save,
    ensure_directory, sanitize_filename, truncate_text
)

# Initialize core components
config = Config()
logger = Logger(__name__)
db = Database()


# ==================== DATA CLASSES ====================

@dataclass
class PostInfo:
    """Blog post information"""
    title: str
    slug: str
    date: str
    topic: str
    excerpt: str
    tags: List[str] = field(default_factory=list)
    md_path: str = ""
    html_path: str = ""
    word_count: int = 0
    reading_time: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "slug": self.slug,
            "date": self.date,
            "topic": self.topic,
            "excerpt": self.excerpt,
            "tags": self.tags,
            "md_path": self.md_path,
            "html_path": self.html_path,
            "word_count": self.word_count,
            "reading_time": self.reading_time,
        }


# ==================== TEMPLATES ====================

class Templates:
    """HTML/CSS templates for blog generation"""
    
    BLOG_POST = """---
title: "{title}"
date: "{date}"
topic: "{topic}"
tags: {tags}
description: "{description}"
lang: "vi"
canonical: "{canonical_url}"
---

# {title}

📅 **Ngày**: {date}  
🏷️ **Chủ đề**: {topic}  
⏱️ **Thời gian đọc**: {reading_time} phút

---

## 📰 Tin Tức Hôm Nay

### 🇰🇷 Tiếng Hàn
{news_kr}

### 🇻🇳 Tiếng Việt
{news_vi}

---

## 📝 Đề Thi TOPIK 54

### Yêu cầu đề bài:
{question}

---

## ✍️ Bài Văn Mẫu

{essay}

---

## 📊 Phân Tích Theo Đoạn

{paragraphs_analysis}

---

## 📚 Từ Vựng & Ngữ Pháp Quan Trọng

{vocabulary_section}

---

## 🎯 Quiz Hôm Nay

### Quiz Từ Vựng
{vocab_quiz}

### Quiz Ngữ Pháp
{grammar_quiz}

---

## 🎬 Video Học Tập

- [TikTok Video 1 - Tin Tức]({video_1_url})
- [TikTok Video 2 - Bài Văn Mẫu]({video_2_url})
- [TikTok Video 3 - Quiz Từ Vựng]({video_3_url})
- [TikTok Video 4 - Quiz Ngữ Pháp]({video_4_url})
- [YouTube Deep Dive]({video_5_url})

---

## 🎧 Podcast

Nghe bài học hôm nay trên [Spotify]({spotify_url})

---

*Được tạo tự động bởi 데일리 코리안 System*
"""

    INDEX = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>데일리 코리안 - Học TOPIK Mỗi Ngày</title>
    <meta name="description" content="Học tiếng Hàn và luyện thi TOPIK mỗi ngày với tin tức, bài văn mẫu, từ vựng và quiz.">
    <meta name="keywords" content="TOPIK, Korean, 한국어, tiếng Hàn, học tiếng Hàn">
    <meta property="og:title" content="데일리 코리안 - Học TOPIK Mỗi Ngày">
    <meta property="og:description" content="Học tiếng Hàn và luyện thi TOPIK mỗi ngày">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="vi_VN">
    <link rel="canonical" href="{base_url}">
    <link rel="stylesheet" href="style.css">
    <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="feed.xml">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1>🇰🇷 데일리 코리안</h1>
        <p>Học TOPIK Mỗi Ngày - Tin Tức, Bài Văn, Quiz</p>
    </header>
    
    <nav class="nav-links">
        <a href="#posts">Bài Viết</a>
        <a href="https://youtube.com/@topikdaily">YouTube</a>
        <a href="https://tiktok.com/@topikdaily">TikTok</a>
        <a href="feed.xml">RSS</a>
    </nav>
    
    <main>
        <section id="posts" class="posts">
            {posts_list}
        </section>
        
        <section class="pagination">
            {pagination}
        </section>
    </main>
    
    <footer>
        <p>© {year} 데일리 코리안 | <a href="https://youtube.com/@topikdaily">YouTube</a> | <a href="https://tiktok.com/@topikdaily">TikTok</a></p>
        <p>Made with ❤️ for Korean learners</p>
    </footer>
    
    <script src="script.js" defer></script>
</body>
</html>
"""

    POST_CARD = """
        <article class="post-card" data-date="{date}">
            <div class="post-meta">
                <span class="date">📅 {date}</span>
                <span class="reading-time">⏱️ {reading_time} phút</span>
            </div>
            <h2><a href="posts/{slug}.html">{title}</a></h2>
            <p class="topic">🏷️ {topic}</p>
            <p class="excerpt">{excerpt}</p>
            <div class="tags">
                {tags_html}
            </div>
            <a href="posts/{slug}.html" class="read-more">Đọc tiếp →</a>
        </article>
"""

    CSS = """:root {
    --primary: #1a73e8;
    --primary-dark: #1557b0;
    --secondary: #5f6368;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text: #202124;
    --accent: #ea4335;
    --success: #34a853;
    --warning: #fbbc04;
    --border: #dadce0;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
    --shadow-hover: 0 4px 16px rgba(0,0,0,0.15);
    --radius: 12px;
    --transition: 0.2s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 16px;
}

header {
    background: linear-gradient(135deg, var(--primary), #4285f4);
    color: white;
    padding: 4rem 1rem;
    text-align: center;
}

header h1 {
    font-size: 2.8rem;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

.nav-links {
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 1rem;
    background: var(--card-bg);
    box-shadow: var(--shadow);
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-links a {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
    transition: color var(--transition);
}

.nav-links a:hover {
    color: var(--primary-dark);
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.posts {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 2rem;
}

.post-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    transition: transform var(--transition), box-shadow var(--transition);
    display: flex;
    flex-direction: column;
}

.post-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
}

.post-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.85rem;
    color: var(--secondary);
}

.post-card h2 {
    margin-bottom: 0.5rem;
    font-size: 1.3rem;
}

.post-card h2 a {
    color: var(--text);
    text-decoration: none;
    transition: color var(--transition);
}

.post-card h2 a:hover {
    color: var(--primary);
}

.topic {
    color: var(--secondary);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.excerpt {
    margin: 1rem 0;
    color: var(--secondary);
    flex-grow: 1;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.tag {
    background: var(--bg);
    color: var(--primary);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    text-decoration: none;
    transition: background var(--transition);
}

.tag:hover {
    background: var(--primary);
    color: white;
}

.read-more {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
    transition: color var(--transition);
}

.read-more:hover {
    color: var(--primary-dark);
}

.pagination {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 3rem 0;
}

.pagination a {
    padding: 0.5rem 1rem;
    background: var(--card-bg);
    border-radius: var(--radius);
    text-decoration: none;
    color: var(--primary);
    box-shadow: var(--shadow);
}

footer {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--secondary);
    background: var(--card-bg);
    margin-top: 3rem;
}

footer a {
    color: var(--primary);
    text-decoration: none;
}

/* Post page styles */
article.post {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2.5rem;
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

article.post h1 {
    color: var(--primary);
    margin-bottom: 1.5rem;
    font-size: 2rem;
    line-height: 1.3;
}

article.post h2 {
    color: var(--text);
    margin: 2.5rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--bg);
    font-size: 1.4rem;
}

article.post h3 {
    color: var(--secondary);
    margin: 1.5rem 0 0.75rem;
    font-size: 1.15rem;
}

article.post pre {
    background: #263238;
    color: #aed581;
    padding: 1.5rem;
    border-radius: var(--radius);
    overflow-x: auto;
    font-size: 0.9rem;
}

article.post code {
    background: var(--bg);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9em;
}

article.post blockquote {
    border-left: 4px solid var(--primary);
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    background: var(--bg);
    border-radius: 0 var(--radius) var(--radius) 0;
}

.quiz-section {
    background: #e8f5e9;
    padding: 1.5rem;
    border-radius: var(--radius);
    margin: 1.5rem 0;
    border-left: 4px solid var(--success);
}

.vocab-item {
    background: #fff3e0;
    padding: 1.25rem;
    border-radius: var(--radius);
    margin: 0.75rem 0;
    border-left: 4px solid var(--warning);
}

.korean-text {
    font-size: 1.2em;
    color: var(--primary);
}

details {
    margin: 1rem 0;
}

details summary {
    cursor: pointer;
    color: var(--primary);
    font-weight: 500;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }
    
    header p {
        font-size: 1rem;
    }
    
    .posts {
        grid-template-columns: 1fr;
    }
    
    .nav-links {
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    article.post {
        padding: 1.5rem;
        margin: 1rem;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #121212;
        --card-bg: #1e1e1e;
        --text: #e0e0e0;
        --secondary: #9e9e9e;
        --border: #333;
    }
    
    header {
        background: linear-gradient(135deg, #1557b0, #2a6bc4);
    }
}
"""

    RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>데일리 코리안 - TOPIK Daily</title>
    <link>{base_url}</link>
    <description>Học tiếng Hàn và luyện thi TOPIK mỗi ngày</description>
    <language>vi</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>
    {items}
</channel>
</rss>
"""

    RSS_ITEM = """
    <item>
        <title>{title}</title>
        <link>{base_url}/posts/{slug}.html</link>
        <description><![CDATA[{excerpt}]]></description>
        <pubDate>{pub_date}</pubDate>
        <guid>{base_url}/posts/{slug}.html</guid>
    </item>
"""

    SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}</loc>
        <lastmod>{date}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    {urls}
</urlset>
"""


# ==================== BLOG GENERATOR ====================

class BlogGenerator:
    """
    Professional blog generator from TOPIK data.
    
    Features:
        - Markdown and HTML generation
        - SEO optimization (meta tags, sitemap, RSS)
        - Responsive design with dark mode
        - Multi-language support
    """
    
    def __init__(
        self,
        output_dir: str = None,
        base_url: str = "https://topikdaily.github.io"
    ):
        """
        Initialize blog generator.
        
        Args:
            output_dir: Output directory for generated files
            base_url: Base URL for canonical links and RSS
        """
        self.output_dir = Path(output_dir or config.paths.blog_dir)
        self.posts_dir = self.output_dir / "posts"
        self.assets_dir = self.output_dir / "assets"
        self.base_url = base_url.rstrip("/")
        
        self.posts: List[PostInfo] = []
        self.templates = Templates()
        
        logger.info(f"BlogGenerator initialized: {self.output_dir}")
    
    def setup_directories(self):
        """Create necessary directories"""
        ensure_directory(self.output_dir)
        ensure_directory(self.posts_dir)
        ensure_directory(self.assets_dir)
        logger.debug(f"Blog directories created: {self.output_dir}")
    
    def generate_slug(self, title: str, date: str) -> str:
        """
        Generate URL-friendly slug from title.
        
        Args:
            title: Post title
            date: Date string (YYYY-MM-DD)
            
        Returns:
            URL-safe slug
        """
        # Remove special characters, keep Korean/Vietnamese
        slug = re.sub(
            r'[^\w\s가-힣àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ-]',
            '',
            title.lower()
        )
        slug = re.sub(r'\s+', '-', slug.strip())
        slug = slug[:50]  # Limit length
        
        return f"{date}-{slug}"
    
    def _calculate_reading_time(self, text: str) -> int:
        """Calculate estimated reading time in minutes"""
        words = len(text.split())
        return max(1, words // 200)
    
    def _format_vocabulary(self, analysis_list: List[Dict]) -> str:
        """Format vocabulary section as HTML"""
        if not analysis_list:
            return "*Không có từ vựng hôm nay*"
        
        sections = []
        for i, item in enumerate(analysis_list[:15], 1):
            word = item.get("item", "")
            explanation = item.get("professor_explanation", "")
            
            sections.append(f"""
<div class="vocab-item">
<strong class="korean-text">{i}. {word}</strong>

{explanation}
</div>
""")
        return "\n".join(sections)
    
    def _format_paragraphs(self, paragraphs: List[Dict]) -> str:
        """Format essay paragraphs analysis"""
        if not paragraphs:
            return "*Không có phân tích*"
        
        sections = []
        for para in paragraphs:
            label = para.get("label", "")
            ko = para.get("ko", "")
            vi = para.get("vi", "")
            analysis_vi = para.get("analysis_vi", "")
            
            sections.append(f"""
### {label}

**🇰🇷 Tiếng Hàn:**
> {ko}

**🇻🇳 Tiếng Việt:**
> {vi}

**📊 Phân tích:**
{analysis_vi}
""")
        return "\n".join(sections)
    
    def _format_quiz(self, quiz_data: Dict) -> str:
        """Format quiz section as HTML"""
        if not quiz_data:
            return "*Không có quiz*"
        
        target = quiz_data.get("target_word", quiz_data.get("target_grammar", ""))
        question_vi = quiz_data.get("question_vi", "")
        options_vi = quiz_data.get("options_vi", [])
        correct = quiz_data.get("correct_answer", "")
        explanation_vi = quiz_data.get("explanation_vi", "")
        
        options_text = "\n".join([f"- {opt}" for opt in options_vi])
        
        return f"""
<div class="quiz-section">

**Từ khóa:** `{target}`

**Câu hỏi:** {question_vi}

{options_text}

<details>
<summary>👁️ Xem đáp án</summary>

**Đáp án đúng: {correct}**

{explanation_vi}

</details>
</div>
"""
    
    def _markdown_to_html(self, markdown_content: str, title: str, post: PostInfo) -> str:
        """Convert markdown to HTML with full page structure"""
        # Remove frontmatter
        content = re.sub(r'^---[\s\S]*?---\n', '', markdown_content)
        
        # Convert headers
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Convert formatting
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
        content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
        content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
        
        # Convert paragraphs and line breaks
        content = re.sub(r'\n\n', '</p><p>', content)
        content = re.sub(r'\n', '<br>', content)
        
        # Build tags HTML
        tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in post.tags])
        
        return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 데일리 코리안</title>
    <meta name="description" content="{truncate_text(post.excerpt, 160)}">
    <meta name="keywords" content="{', '.join(post.tags)}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{truncate_text(post.excerpt, 160)}">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="vi_VN">
    <link rel="canonical" href="{self.base_url}/posts/{post.slug}.html">
    <link rel="stylesheet" href="../style.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1><a href="../index.html" style="color:white;text-decoration:none;">🇰🇷 데일리 코리안</a></h1>
    </header>
    
    <article class="post">
        <div class="post-meta">
            <span class="date">📅 {post.date}</span>
            <span class="reading-time">⏱️ {post.reading_time} phút đọc</span>
        </div>
        
        <p>{content}</p>
        
        <div class="tags" style="margin-top: 2rem;">
            {tags_html}
        </div>
    </article>
    
    <footer>
        <p><a href="../index.html">← Quay lại trang chủ</a></p>
        <p>© {datetime.now().year} 데일리 코리안</p>
    </footer>
</body>
</html>
"""
    
    def generate_post(self, data: Dict, date: str = None) -> PostInfo:
        """
        Generate a single blog post from final_data.json.
        
        Args:
            data: Parsed JSON data from final_data.json
            date: Optional date override (YYYY-MM-DD)
            
        Returns:
            PostInfo object with generated post details
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract data sections
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        phase3 = data.get("phase3", {})
        phase4 = data.get("phase4", {})
        
        # Get content
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        news_kr = phase1.get("news_summary_easy_kr", "")
        news_vi = phase1.get("news_summary_easy_vi", news_kr)
        question = phase1.get("question_full_text", "")
        essay = phase2.get("essay", "")
        analysis_list = phase2.get("analysis_list", [])
        
        # Get Deep Dive data
        deep_dive = phase4.get("video_5_deep_dive", phase3.get("video_5_deep_dive", {}))
        paragraphs = deep_dive.get("essay", {}).get("paragraphs", [])
        
        # Get quizzes
        vocab_quiz = phase3.get("video_3_vocab_quiz", phase4.get("video_3_vocab_quiz", {}))
        grammar_quiz = phase3.get("video_4_grammar_quiz", phase4.get("video_4_grammar_quiz", {}))
        
        # Generate content
        title = f"TOPIK Daily - {topic}"
        slug = self.generate_slug(topic, date)
        
        # Calculate metrics
        full_content = f"{news_kr} {news_vi} {essay}"
        word_count = len(full_content.split())
        reading_time = self._calculate_reading_time(full_content)
        
        # Format sections
        vocabulary_section = self._format_vocabulary(analysis_list)
        paragraphs_analysis = self._format_paragraphs(paragraphs)
        vocab_quiz_html = self._format_quiz(vocab_quiz)
        grammar_quiz_html = self._format_quiz(grammar_quiz)
        
        # Generate markdown
        content = self.templates.BLOG_POST.format(
            title=title,
            date=date,
            topic=topic,
            tags=json.dumps(["TOPIK", "Korean", "Learning", "Quiz", topic], ensure_ascii=False),
            description=truncate_text(news_vi, 150),
            canonical_url=f"{self.base_url}/posts/{slug}.html",
            reading_time=reading_time,
            news_kr=news_kr,
            news_vi=news_vi,
            question=question,
            essay=essay,
            paragraphs_analysis=paragraphs_analysis,
            vocabulary_section=vocabulary_section,
            vocab_quiz=vocab_quiz_html,
            grammar_quiz=grammar_quiz_html,
            video_1_url="#",
            video_2_url="#",
            video_3_url="#",
            video_4_url="#",
            video_5_url="#",
            spotify_url="#"
        )
        
        # Create post info
        post = PostInfo(
            title=title,
            slug=slug,
            date=date,
            topic=topic,
            excerpt=truncate_text(news_vi, 150),
            tags=["TOPIK", "Korean", "Learning", topic],
            word_count=word_count,
            reading_time=reading_time
        )
        
        # Save markdown
        md_path = self.posts_dir / f"{slug}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        post.md_path = str(md_path)
        
        # Convert to HTML and save
        html_content = self._markdown_to_html(content, title, post)
        html_path = self.posts_dir / f"{slug}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        post.html_path = str(html_path)
        
        self.posts.append(post)
        logger.info(f"Blog post generated: {slug}")
        
        # Log to database
        db.insert_content(
            content_type="blog_post",
            title=title,
            file_path=str(html_path),
            platform="blog"
        )
        
        return post
    
    def generate_index(self):
        """Generate index.html with all posts"""
        posts_html = ""
        for post in sorted(self.posts, key=lambda x: x.date, reverse=True):
            tags_html = " ".join([
                f'<span class="tag">{tag}</span>' 
                for tag in post.tags[:4]
            ])
            
            posts_html += self.templates.POST_CARD.format(
                slug=post.slug,
                title=post.title,
                date=post.date,
                topic=post.topic,
                excerpt=post.excerpt,
                reading_time=post.reading_time,
                tags_html=tags_html
            )
        
        index_html = self.templates.INDEX.format(
            base_url=self.base_url,
            posts_list=posts_html,
            pagination="",  # TODO: Implement pagination
            year=datetime.now().year
        )
        
        # Save index.html
        index_path = self.output_dir / "index.html"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        
        # Save CSS
        css_path = self.output_dir / "style.css"
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(self.templates.CSS)
        
        logger.info(f"Blog index generated: {index_path}")
    
    def generate_rss(self):
        """Generate RSS feed"""
        items = ""
        for post in sorted(self.posts, key=lambda x: x.date, reverse=True)[:20]:
            items += self.templates.RSS_ITEM.format(
                title=post.title,
                base_url=self.base_url,
                slug=post.slug,
                excerpt=post.excerpt,
                pub_date=datetime.strptime(post.date, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 GMT")
            )
        
        rss_content = self.templates.RSS.format(
            base_url=self.base_url,
            build_date=datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            items=items
        )
        
        rss_path = self.output_dir / "feed.xml"
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        logger.info(f"RSS feed generated: {rss_path}")
    
    def generate_sitemap(self):
        """Generate sitemap.xml"""
        urls = ""
        for post in self.posts:
            urls += f"""
    <url>
        <loc>{self.base_url}/posts/{post.slug}.html</loc>
        <lastmod>{post.date}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>"""
        
        sitemap_content = self.templates.SITEMAP.format(
            base_url=self.base_url,
            date=datetime.now().strftime("%Y-%m-%d"),
            urls=urls
        )
        
        sitemap_path = self.output_dir / "sitemap.xml"
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        
        logger.info(f"Sitemap generated: {sitemap_path}")
    
    def generate_from_json(self, json_path: str) -> PostInfo:
        """
        Generate complete blog from final_data.json file.
        
        Args:
            json_path: Path to final_data.json
            
        Returns:
            PostInfo for the generated post
        """
        data = safe_json_load(json_path, {})
        if not data:
            raise FileNotFoundError(f"Failed to load: {json_path}")
        
        self.setup_directories()
        post = self.generate_post(data)
        self.generate_index()
        self.generate_rss()
        self.generate_sitemap()
        
        logger.info(f"Blog generation complete: {self.output_dir}")
        
        return post


# ==================== PUBLIC API ====================

def generate_blog_from_data(
    json_path: str,
    output_dir: str = None,
    base_url: str = "https://topikdaily.github.io"
) -> PostInfo:
    """
    Main function to generate blog from final_data.json.
    
    Args:
        json_path: Path to final_data.json
        output_dir: Output directory for blog
        base_url: Base URL for SEO
        
    Returns:
        PostInfo with generated post details
    """
    generator = BlogGenerator(output_dir, base_url)
    return generator.generate_from_json(json_path)


# ==================== CLI ====================

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate blog from TOPIK data")
    parser.add_argument(
        "--json",
        default="topik-video/public/final_data.json",
        help="Path to final_data.json"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output directory"
    )
    parser.add_argument(
        "--base-url",
        default="https://topikdaily.github.io",
        help="Base URL for SEO"
    )
    
    args = parser.parse_args()
    
    if Path(args.json).exists():
        result = generate_blog_from_data(args.json, args.output, args.base_url)
        print(f"Blog generated: {result.html_path}")
    else:
        logger.error(f"File not found: {args.json}")


if __name__ == "__main__":
    main()
