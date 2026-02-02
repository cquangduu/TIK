"""
================================================================================
PODCAST GENERATOR MODULE — Generate Podcast Audio for Spotify/Apple Podcasts
================================================================================
Features:
    - Combine audio segments into full podcast episode
    - Generate podcast metadata (title, description, chapters)
    - Create RSS feed for podcast distribution
    - Support for Spotify via Anchor.fm or direct RSS
================================================================================
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydub import AudioSegment
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ==================== CONFIGURATION ====================
PODCAST_OUTPUT_DIR = "podcast_output"
PODCAST_NAME = "DAILY KOREAN - Luyện Thi TOPIK Mỗi Ngày"
PODCAST_AUTHOR = "DAILY KOREAN"
PODCAST_EMAIL = "dailykoreanluyenviettopik@gmail.com"
PODCAST_WEBSITE = "https://dailykorean.me"
PODCAST_COVER_URL = "https://dailykorean.me/cover.jpg"
PODCAST_CATEGORY = "Education"
PODCAST_SUBCATEGORY = "Language Learning"
PODCAST_LANGUAGE = "vi"

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 2
BITRATE = "128k"

# Intro/Outro audio (optional)
INTRO_AUDIO = None  # Path to intro jingle
OUTRO_AUDIO = None  # Path to outro jingle


class PodcastGenerator:
    """Generate podcast episodes from TOPIK audio segments"""
    
    def __init__(self, output_dir: str = PODCAST_OUTPUT_DIR):
        self.output_dir = output_dir
        self.episodes_dir = os.path.join(output_dir, "episodes")
        self.episodes = []
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.episodes_dir, exist_ok=True)
        logging.info(f"📁 Podcast directories created: {self.output_dir}")
    
    def load_audio_segment(self, path: str) -> Optional[AudioSegment]:
        """Load audio file as AudioSegment"""
        if not path or not os.path.exists(path):
            logging.warning(f"⚠️ Audio file not found: {path}")
            return None
        
        try:
            return AudioSegment.from_mp3(path)
        except Exception as e:
            logging.error(f"❌ Error loading audio: {path} - {e}")
            return None
    
    def add_silence(self, duration_ms: int = 1000) -> AudioSegment:
        """Create silence segment"""
        return AudioSegment.silent(duration=duration_ms)
    
    def generate_episode(
        self,
        data: Dict,
        assets_dir: str,
        date: str = None,
        episode_number: int = 1
    ) -> Optional[Dict]:
        """
        Generate a podcast episode from TOPIK data
        
        Args:
            data: final_data.json content
            assets_dir: Path to audio assets
            date: Episode date
            episode_number: Episode number
            
        Returns:
            Episode info dict
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        self.setup_directories()
        
        # Extract metadata
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase3 = data.get("phase3", {})
        phase4 = data.get("phase4", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        
        # Collect audio segments
        audio_segments = []
        chapters = []
        current_time = 0
        
        # Add intro (optional)
        if INTRO_AUDIO and os.path.exists(INTRO_AUDIO):
            intro = self.load_audio_segment(INTRO_AUDIO)
            if intro:
                audio_segments.append(intro)
                chapters.append({"time": 0, "title": "Intro"})
                current_time += len(intro)
        
        # --- Section 1: News ---
        chapters.append({"time": current_time / 1000, "title": "📰 Tin Tức Hàn Quốc"})
        
        video1_data = phase3.get("video_1_news_healing", {})
        if video1_data:
            combined_audio = video1_data.get("combined_audio", "")
            if combined_audio:
                audio_path = os.path.join(assets_dir, combined_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    audio_segments.append(self.add_silence(2000))  # 2s pause
                    current_time += 2000
        
        # --- Section 2: Essay ---
        chapters.append({"time": current_time / 1000, "title": "✍️ Bài Văn Mẫu TOPIK 54"})
        
        video2_data = phase3.get("video_2_writing_coach", {})
        if video2_data:
            combined_audio = video2_data.get("combined_audio", "")
            if combined_audio:
                audio_path = os.path.join(assets_dir, combined_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    audio_segments.append(self.add_silence(2000))
                    current_time += 2000
        
        # --- Section 3: Vocabulary Quiz ---
        chapters.append({"time": current_time / 1000, "title": "📚 Quiz Từ Vựng"})
        
        video3_data = phase3.get("video_3_vocab_quiz", phase4.get("video_3_vocab_quiz", {}))
        if video3_data:
            audio_timing = video3_data.get("audio_timing", {})
            
            # Question
            question_audio = audio_timing.get("question", {}).get("path", "")
            if question_audio:
                audio_path = os.path.join(assets_dir, question_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    # Add thinking time
                    audio_segments.append(self.add_silence(5000))  # 5s thinking
                    current_time += 5000
            
            # Answer
            answer_audio = audio_timing.get("answer", {}).get("path", "")
            if answer_audio:
                audio_path = os.path.join(assets_dir, answer_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    audio_segments.append(self.add_silence(2000))
                    current_time += 2000
        
        # --- Section 4: Grammar Quiz ---
        chapters.append({"time": current_time / 1000, "title": "📖 Quiz Ngữ Pháp"})
        
        video4_data = phase3.get("video_4_grammar_quiz", phase4.get("video_4_grammar_quiz", {}))
        if video4_data:
            audio_timing = video4_data.get("audio_timing", {})
            
            # Question
            question_audio = audio_timing.get("question", {}).get("path", "")
            if question_audio:
                audio_path = os.path.join(assets_dir, question_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    audio_segments.append(self.add_silence(5000))
                    current_time += 5000
            
            # Answer
            answer_audio = audio_timing.get("answer", {}).get("path", "")
            if answer_audio:
                audio_path = os.path.join(assets_dir, answer_audio.lstrip("/"))
                segment = self.load_audio_segment(audio_path)
                if segment:
                    audio_segments.append(segment)
                    current_time += len(segment)
                    audio_segments.append(self.add_silence(2000))
                    current_time += 2000
        
        # --- Section 5: Deep Dive (Optional) ---
        deep_dive = phase4.get("video_5_deep_dive", {})
        if deep_dive:
            chapters.append({"time": current_time / 1000, "title": "🎓 Deep Dive - Phân Tích Chi Tiết"})
            
            # Try to get deep dive audio segments
            audio_info = deep_dive.get("audio", {})
            segments_list = audio_info.get("segments", [])
            
            for seg in segments_list:
                seg_path = seg.get("path", "")
                if seg_path:
                    audio_path = os.path.join(assets_dir, seg_path.lstrip("/"))
                    segment = self.load_audio_segment(audio_path)
                    if segment:
                        audio_segments.append(segment)
                        current_time += len(segment)
                        audio_segments.append(self.add_silence(500))  # Short pause
                        current_time += 500
        
        # Add outro (optional)
        if OUTRO_AUDIO and os.path.exists(OUTRO_AUDIO):
            chapters.append({"time": current_time / 1000, "title": "Outro"})
            outro = self.load_audio_segment(OUTRO_AUDIO)
            if outro:
                audio_segments.append(outro)
                current_time += len(outro)
        
        # Combine all segments
        if not audio_segments:
            logging.error("❌ No audio segments found!")
            return None
        
        combined = audio_segments[0]
        for segment in audio_segments[1:]:
            combined += segment
        
        # Export
        episode_filename = f"ep{episode_number:03d}_{date}.mp3"
        episode_path = os.path.join(self.episodes_dir, episode_filename)
        
        combined.export(
            episode_path,
            format="mp3",
            bitrate=BITRATE,
            parameters=["-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS)]
        )
        
        # Calculate duration
        duration_sec = len(combined) / 1000
        duration_str = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"
        
        episode_info = {
            "number": episode_number,
            "title": f"Ep.{episode_number}: {topic}",
            "date": date,
            "topic": topic,
            "path": episode_path,
            "filename": episode_filename,
            "duration_sec": duration_sec,
            "duration_str": duration_str,
            "chapters": chapters,
            "description": self.generate_description(data, chapters)
        }
        
        self.episodes.append(episode_info)
        logging.info(f"✅ Podcast episode generated: {episode_filename} ({duration_str})")
        
        return episode_info
    
    def generate_description(self, data: Dict, chapters: List[Dict]) -> str:
        """Generate episode description with timestamps"""
        meta = data.get("meta", {})
        phase1 = data.get("phase1", {})
        phase2 = data.get("phase2", {})
        
        topic = meta.get("topic_title_vi", "TOPIK Daily")
        news = phase1.get("news_summary_easy_kr", "")[:200]
        
        # Format chapters as timestamps
        timestamps = "\n".join([
            f"{int(ch['time'] // 60):02d}:{int(ch['time'] % 60):02d} - {ch['title']}"
            for ch in chapters
        ])
        
        description = f"""🇰🇷 {topic}

Trong tập hôm nay:
- Tin tức Hàn Quốc đơn giản hóa
- Bài văn mẫu TOPIK 54
- Quiz từ vựng và ngữ pháp
- Phân tích chi tiết

📑 Chapters:
{timestamps}

🔗 Xem thêm:
- Blog: {PODCAST_WEBSITE}
- TikTok: @dailykorean
- YouTube: @dailykorean

#TOPIK #LearnKorean #Podcast #Korean
"""
        return description
    
    def generate_rss_feed(self, base_url: str = PODCAST_WEBSITE) -> str:
        """Generate RSS feed for podcast distribution"""
        
        # Create RSS structure
        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        
        channel = ET.SubElement(rss, "channel")
        
        # Channel info
        ET.SubElement(channel, "title").text = PODCAST_NAME
        ET.SubElement(channel, "link").text = PODCAST_WEBSITE
        ET.SubElement(channel, "language").text = PODCAST_LANGUAGE
        ET.SubElement(channel, "description").text = f"Học tiếng Hàn và luyện thi TOPIK mỗi ngày với tin tức, bài văn mẫu, từ vựng và quiz."
        
        # iTunes specific
        ET.SubElement(channel, "itunes:author").text = PODCAST_AUTHOR
        ET.SubElement(channel, "itunes:summary").text = "Podcast học tiếng Hàn hàng ngày, phù hợp cho người chuẩn bị thi TOPIK."
        
        itunes_owner = ET.SubElement(channel, "itunes:owner")
        ET.SubElement(itunes_owner, "itunes:name").text = PODCAST_AUTHOR
        ET.SubElement(itunes_owner, "itunes:email").text = PODCAST_EMAIL
        
        itunes_image = ET.SubElement(channel, "itunes:image")
        itunes_image.set("href", PODCAST_COVER_URL)
        
        itunes_category = ET.SubElement(channel, "itunes:category")
        itunes_category.set("text", PODCAST_CATEGORY)
        itunes_subcat = ET.SubElement(itunes_category, "itunes:category")
        itunes_subcat.set("text", PODCAST_SUBCATEGORY)
        
        ET.SubElement(channel, "itunes:explicit").text = "false"
        
        # Add episodes
        for episode in sorted(self.episodes, key=lambda x: x["date"], reverse=True):
            item = ET.SubElement(channel, "item")
            
            ET.SubElement(item, "title").text = episode["title"]
            ET.SubElement(item, "description").text = episode["description"]
            ET.SubElement(item, "pubDate").text = datetime.strptime(
                episode["date"], "%Y-%m-%d"
            ).strftime("%a, %d %b %Y 00:00:00 +0000")
            
            # Audio enclosure
            enclosure = ET.SubElement(item, "enclosure")
            enclosure.set("url", f"{base_url}/episodes/{episode['filename']}")
            enclosure.set("type", "audio/mpeg")
            enclosure.set("length", str(int(episode["duration_sec"] * SAMPLE_RATE * CHANNELS * 2)))
            
            ET.SubElement(item, "itunes:duration").text = episode["duration_str"]
            ET.SubElement(item, "itunes:episode").text = str(episode["number"])
            ET.SubElement(item, "itunes:summary").text = episode["description"][:250]
            
            # GUID
            guid = ET.SubElement(item, "guid")
            guid.set("isPermaLink", "false")
            guid.text = f"topikdaily-ep{episode['number']}-{episode['date']}"
        
        # Pretty print
        xml_str = ET.tostring(rss, encoding="unicode")
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        pretty_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])
        
        # Save RSS
        rss_path = os.path.join(self.output_dir, "feed.xml")
        with open(rss_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(pretty_xml.replace('<?xml version="1.0" ?>', ''))
        
        logging.info(f"✅ RSS feed generated: {rss_path}")
        return rss_path
    
    def generate_from_json(
        self,
        json_path: str,
        assets_dir: str,
        episode_number: int = 1
    ) -> Optional[Dict]:
        """Generate podcast episode from final_data.json"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        episode = self.generate_episode(data, assets_dir, episode_number=episode_number)
        
        if episode:
            self.generate_rss_feed()
        
        return episode


def generate_podcast_from_data(
    json_path: str,
    assets_dir: str,
    output_dir: str = PODCAST_OUTPUT_DIR,
    episode_number: int = 1
) -> Optional[Dict]:
    """
    Main function to generate podcast from final_data.json
    
    Args:
        json_path: Path to final_data.json
        assets_dir: Path to audio assets directory
        output_dir: Output directory for podcast
        episode_number: Episode number
        
    Returns:
        Episode info dict
    """
    generator = PodcastGenerator(output_dir)
    return generator.generate_from_json(json_path, assets_dir, episode_number)


# ==================== CLI ====================
if __name__ == "__main__":
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    
    parser = argparse.ArgumentParser(description="Generate podcast from TOPIK data")
    parser.add_argument("--json", default="topik-video/public/final_data.json", help="Path to final_data.json")
    parser.add_argument("--assets", default="topik-video/public/assets", help="Path to audio assets")
    parser.add_argument("--output", default="podcast_output", help="Output directory")
    parser.add_argument("--episode", type=int, default=1, help="Episode number")
    
    args = parser.parse_args()
    
    if os.path.exists(args.json):
        result = generate_podcast_from_data(args.json, args.assets, args.output, args.episode)
        if result:
            print(f"✅ Podcast generated: {result}")
        else:
            print("❌ Failed to generate podcast")
    else:
        print(f"❌ File not found: {args.json}")
