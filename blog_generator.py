"""
================================================================================
BLOG GENERATOR MODULE — Auto Generate Blog Posts from TOPIK Data
================================================================================
Features:
    - Generate Markdown/HTML blog posts from final_data.json
    - SEO-optimized structure
    - Multi-language support (KO/VI)
    - Auto-deploy to GitHub Pages / Netlify / Vercel
================================================================================
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
import shutil

# ==================== CONFIGURATION ====================
BLOG_OUTPUT_DIR = "blog_output"
BLOG_POSTS_DIR = os.path.join(BLOG_OUTPUT_DIR, "posts")
BLOG_ASSETS_DIR = os.path.join(BLOG_OUTPUT_DIR, "assets")

# ==================== TEMPLATES ====================

BLOG_POST_TEMPLATE = """---
title: "{title}"
date: "{date}"
topic: "{topic}"
tags: {tags}
description: "{description}"
lang: "vi"
---

# {title}

📅 **Ngày**: {date}  
🏷️ **Chủ đề**: {topic}

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

*Được tạo tự động bởi TOPIK Daily System*
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAILY KOREAN - Học TOPIK Mỗi Ngày</title>
    <meta name="description" content="Học tiếng Hàn và luyện thi TOPIK mỗi ngày với tin tức, bài văn mẫu, từ vựng và quiz.">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>🇰🇷 DAILY KOREAN</h1>
        <p>Học TOPIK Mỗi Ngày - Tin Tức, Bài Văn, Quiz</p>
    </header>
    
    <main>
        <section class="posts">
            {posts_list}
        </section>
    </main>
    
    <footer>
        <p>© 2026 DAILY KOREAN | <a href="https://youtube.com/@topikdaily">YouTube</a> | <a href="https://tiktok.com/@topikdaily">TikTok</a></p>
    </footer>
</body>
</html>
"""

POST_CARD_TEMPLATE = """
        <article class="post-card">
            <h2><a href="posts/{slug}.html">{title}</a></h2>
            <p class="date">📅 {date}</p>
            <p class="topic">🏷️ {topic}</p>
            <p class="excerpt">{excerpt}</p>
            <a href="posts/{slug}.html" class="read-more">Đọc tiếp →</a>
        </article>
"""

CSS_TEMPLATE = """
:root {
    --primary: #1a73e8;
    --secondary: #5f6368;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text: #202124;
    --accent: #ea4335;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

header {
    background: linear-gradient(135deg, var(--primary), #4285f4);
    color: white;
    padding: 3rem 1rem;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
}

.posts {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.post-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.post-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.post-card h2 {
    margin-bottom: 0.5rem;
}

.post-card h2 a {
    color: var(--text);
    text-decoration: none;
}

.post-card h2 a:hover {
    color: var(--primary);
}

.date, .topic {
    color: var(--secondary);
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.excerpt {
    margin: 1rem 0;
    color: var(--secondary);
}

.read-more {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
}

footer {
    text-align: center;
    padding: 2rem;
    color: var(--secondary);
}

footer a {
    color: var(--primary);
    text-decoration: none;
}

/* Post page styles */
article.post {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

article.post h1 {
    color: var(--primary);
    margin-bottom: 1rem;
}

article.post h2 {
    color: var(--text);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--bg);
}

article.post h3 {
    color: var(--secondary);
    margin: 1.5rem 0 0.5rem;
}

article.post pre {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
}

article.post blockquote {
    border-left: 4px solid var(--primary);
    padding-left: 1rem;
    margin: 1rem 0;
    color: var(--secondary);
}

.quiz-section {
    background: #e8f5e9;
    padding: 1.5rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.vocab-item {
    background: #fff3e0;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.korean-text {
    font-size: 1.2em;
    color: var(--primary);
}

@media (max-width: 768px) {
    header h1 {
        font-size: 1.8rem;
    }
    
    .posts {
        grid-template-columns: 1fr;
    }
}
"""


class BlogGenerator:
    """Generate blog posts from TOPIK final_data.json"""
    
    def __init__(self, output_dir: str = BLOG_OUTPUT_DIR):
        self.output_dir = output_dir
        self.posts_dir = os.path.join(output_dir, "posts")
        self.assets_dir = os.path.join(output_dir, "assets")
        self.posts_data = []
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.posts_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)
        logging.info(f"📁 Blog directories created: {self.output_dir}")
        
    def generate_slug(self, title: str, date: str) -> str:
        """Generate URL-friendly slug"""
        # Remove special characters, keep Korean/Vietnamese
        slug = re.sub(r'[^\w\s가-힣àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ-]', '', title.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = slug[:50]  # Limit length
        return f"{date}-{slug}"
    
    def format_vocabulary(self, analysis_list: List[Dict]) -> str:
        """Format vocabulary section"""
        if not analysis_list:
            return "*Không có từ vựng hôm nay*"
        
        sections = []
        for i, item in enumerate(analysis_list[:15], 1):  # Limit to 15 items
            word = item.get("item", "")
            explanation = item.get("professor_explanation", "")
            sections.append(f"""
<div class="vocab-item">
<strong class="korean-text">{i}. {word}</strong>

{explanation}
</div>
""")
        return "\n".join(sections)
    
    def format_paragraphs(self, paragraphs: List[Dict]) -> str:
        """Format essay paragraphs analysis"""
        if not paragraphs:
            return "*Không có phân tích*"
        
        sections = []
        for para in paragraphs:
            label = para.get("label", "")
            ko = para.get("ko", "")
            vi = para.get("vi", "")
            analysis_ko = para.get("analysis_ko", "")
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
    
    def format_quiz(self, quiz_data: Dict, quiz_type: str = "vocab") -> str:
        """Format quiz section"""
        if not quiz_data:
            return "*Không có quiz*"
        
        target = quiz_data.get("target_word", quiz_data.get("target_grammar", ""))
        question_ko = quiz_data.get("question_ko", "")
        question_vi = quiz_data.get("question_vi", "")
        options_ko = quiz_data.get("options_ko", [])
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
    
    def generate_post(self, data: Dict, date: str = None) -> Dict:
        """Generate a single blog post from final_data.json"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Extract data
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        phase3 = data.get("phase3", {})
        phase4 = data.get("phase4", {})
        
        # Get topic
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        # Get news
        news_kr = phase1.get("news_summary_easy_kr", "")
        news_vi = phase1.get("news_summary_easy_vi", news_kr)  # Fallback
        
        # Get question
        question = phase1.get("question_full_text", "")
        
        # Get essay
        essay = phase2.get("essay", "")
        
        # Get analysis
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
        
        # Format sections
        vocabulary_section = self.format_vocabulary(analysis_list)
        paragraphs_analysis = self.format_paragraphs(paragraphs)
        vocab_quiz_html = self.format_quiz(vocab_quiz, "vocab")
        grammar_quiz_html = self.format_quiz(grammar_quiz, "grammar")
        
        # Generate markdown
        content = BLOG_POST_TEMPLATE.format(
            title=title,
            date=date,
            topic=topic,
            tags=json.dumps(["TOPIK", "Korean", "Learning", "Quiz"], ensure_ascii=False),
            description=f"Học TOPIK với chủ đề: {topic}",
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
        
        # Save markdown
        md_path = os.path.join(self.posts_dir, f"{slug}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Convert to HTML
        html_content = self.markdown_to_html(content, title)
        html_path = os.path.join(self.posts_dir, f"{slug}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        post_info = {
            "title": title,
            "slug": slug,
            "date": date,
            "topic": topic,
            "excerpt": news_vi[:150] + "..." if len(news_vi) > 150 else news_vi,
            "md_path": md_path,
            "html_path": html_path
        }
        
        self.posts_data.append(post_info)
        logging.info(f"✅ Blog post generated: {slug}")
        
        return post_info
    
    def markdown_to_html(self, markdown_content: str, title: str) -> str:
        """Convert markdown to HTML (simple conversion)"""
        # Remove frontmatter
        content = re.sub(r'^---[\s\S]*?---\n', '', markdown_content)
        
        # Convert headers
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # Convert bold
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        
        # Convert italic
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        
        # Convert code
        content = re.sub(r'`(.+?)`', r'<code>\1</code>', content)
        
        # Convert blockquotes
        content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
        
        # Convert lists
        content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
        
        # Convert links
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
        
        # Convert paragraphs
        content = re.sub(r'\n\n', '</p><p>', content)
        
        # Convert line breaks
        content = re.sub(r'\n', '<br>', content)
        
        # Wrap in HTML
        html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../style.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1><a href="../index.html" style="color:white;text-decoration:none;">🇰🇷 TOPIK Daily</a></h1>
    </header>
    
    <article class="post">
        <p>{content}</p>
    </article>
    
    <footer>
        <p><a href="../index.html">← Quay lại trang chủ</a></p>
        <p>© 2026 TOPIK Daily</p>
    </footer>
</body>
</html>
"""
        return html
    
    def generate_index(self):
        """Generate index.html with all posts"""
        posts_html = ""
        for post in sorted(self.posts_data, key=lambda x: x["date"], reverse=True):
            posts_html += POST_CARD_TEMPLATE.format(
                slug=post["slug"],
                title=post["title"],
                date=post["date"],
                topic=post["topic"],
                excerpt=post["excerpt"]
            )
        
        index_html = INDEX_TEMPLATE.format(posts_list=posts_html)
        
        index_path = os.path.join(self.output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        
        # Generate CSS
        css_path = os.path.join(self.output_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(CSS_TEMPLATE)
        
        logging.info(f"✅ Blog index generated: {index_path}")
        
    def generate_from_json(self, json_path: str) -> Dict:
        """Generate blog post from final_data.json file"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.setup_directories()
        post_info = self.generate_post(data)
        self.generate_index()
        
        return post_info


def generate_blog_from_data(json_path: str, output_dir: str = BLOG_OUTPUT_DIR) -> Dict:
    """
    Main function to generate blog from final_data.json
    
    Args:
        json_path: Path to final_data.json
        output_dir: Output directory for blog
        
    Returns:
        Dict with post info
    """
    generator = BlogGenerator(output_dir)
    return generator.generate_from_json(json_path)


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Generate blog from TOPIK data")
    parser.add_argument("--json", default="topik-video/public/final_data.json", help="Path to final_data.json")
    parser.add_argument("--output", default="blog_output", help="Output directory")
    
    args = parser.parse_args()
    
    if os.path.exists(args.json):
        result = generate_blog_from_data(args.json, args.output)
        print(f"✅ Blog generated: {result}")
    else:
        print(f"❌ File not found: {args.json}")
