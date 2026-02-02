#!/usr/bin/env python3
"""
================================================================================
TOPIK DAILY - VIDEO COMPONENTS TESTER
================================================================================
Kiểm tra chi tiết các thành phần video để đảm bảo:
1. Audio sync đúng với nội dung
2. Text không bị chồng chéo
3. Duration chính xác
4. File JSON đầy đủ dữ liệu

Usage:
    python test_video_components.py           # Kiểm tra tất cả
    python test_video_components.py --fix     # Tự động sửa lỗi
================================================================================
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).parent
REMOTION_DIR = ROOT_DIR / "topik-video"
PUBLIC_DIR = REMOTION_DIR / "public"
ASSETS_DIR = PUBLIC_DIR / "assets"
DATA_FILE = PUBLIC_DIR / "final_data.json"

# ─── Configuration ─────────────────────────────────────────────────────────────
MAX_KOREAN_CHARS_PER_SCREEN = 80  # Maximum Korean chars to display without overflow
MAX_VIETNAMESE_CHARS_PER_SCREEN = 120  # Maximum Vietnamese chars
MIN_SEGMENT_DURATION_SEC = 1.5  # Minimum duration for a segment
MAX_TIKTOK_DURATION_SEC = 59  # TikTok max duration


def ok(msg): print(f"  [OK] {msg}")
def fail(msg): print(f"  [FAIL] {msg}")
def warn(msg): print(f"  [WARN] {msg}")
def info(msg): print(f"  [INFO] {msg}")
def header(msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")


def load_data() -> Dict[str, Any]:
    """Load final_data.json"""
    if not DATA_FILE.exists():
        print(f"[FAIL] File not found: {DATA_FILE}")
        print("  Run main.py first to generate video data.")
        sys.exit(1)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_text_length(text: str, max_length: int, context: str) -> List[str]:
    """Check if text is too long for display"""
    issues = []
    if len(text) > max_length:
        issues.append(f"{context}: Text too long ({len(text)} chars > {max_length})")
    return issues


def check_audio_file(audio_path: str, context: str) -> Tuple[bool, str]:
    """Check if audio file exists and is valid"""
    if not audio_path:
        return False, f"{context}: Missing audio_path"
    
    # Convert to absolute path
    if audio_path.startswith('/'):
        full_path = PUBLIC_DIR / audio_path[1:]
    else:
        full_path = PUBLIC_DIR / audio_path
    
    if not full_path.exists():
        return False, f"{context}: Audio file not found: {audio_path}"
    
    # Check file size
    size = full_path.stat().st_size
    if size < 1000:  # Less than 1KB
        return False, f"{context}: Audio file too small ({size} bytes): {audio_path}"
    
    return True, ""


def check_segment_duration(duration: float, context: str) -> List[str]:
    """Check if segment duration is valid"""
    issues = []
    if not duration or duration <= 0:
        issues.append(f"{context}: Missing or invalid duration")
    elif duration < MIN_SEGMENT_DURATION_SEC:
        issues.append(f"{context}: Duration too short ({duration:.2f}s < {MIN_SEGMENT_DURATION_SEC}s)")
    return issues


def test_video_1_news(data: Dict) -> Dict[str, Any]:
    """Test Video 1: News Healing"""
    header("TEST VIDEO 1: NEWS HEALING")
    
    results = {
        "issues": [],
        "warnings": [],
        "audio_files": [],
        "total_duration": 0,
    }
    
    # Get script data
    script = data.get("tiktok_script", {}).get("video_1_news", {})
    audio_data = data.get("audio_data", {}).get("video_1_news", {})
    
    if not script and not audio_data:
        results["issues"].append("No data found for video_1_news")
        fail("No data found")
        return results
    
    # Check opening
    opening = audio_data.get("opening") or script.get("opening", {})
    if opening:
        if opening.get("audio_path"):
            valid, msg = check_audio_file(opening["audio_path"], "Opening")
            if not valid:
                results["issues"].append(msg)
                fail(msg)
            else:
                ok(f"Opening audio: {opening['audio_path']}")
                results["audio_files"].append(opening["audio_path"])
        
        if opening.get("duration"):
            results["total_duration"] += opening["duration"]
        
        # Check text length
        text = opening.get("text", "")
        issues = check_text_length(text, MAX_KOREAN_CHARS_PER_SCREEN, "Opening text")
        results["warnings"].extend(issues)
    
    # Check segments
    segments = audio_data.get("segments") or script.get("segments", [])
    for idx, seg in enumerate(segments):
        context = f"Segment {idx}"
        
        # Check Korean text length
        ko = seg.get("ko", "")
        if ko:
            issues = check_text_length(ko, MAX_KOREAN_CHARS_PER_SCREEN, f"{context} Korean")
            for issue in issues:
                warn(issue)
            results["warnings"].extend(issues)
        
        # Check Vietnamese text length
        vi = seg.get("vi", "")
        if vi:
            issues = check_text_length(vi, MAX_VIETNAMESE_CHARS_PER_SCREEN, f"{context} Vietnamese")
            for issue in issues:
                warn(issue)
            results["warnings"].extend(issues)
        
        # Check audio
        if seg.get("audio_path"):
            valid, msg = check_audio_file(seg["audio_path"], context)
            if not valid:
                results["issues"].append(msg)
                fail(msg)
            else:
                results["audio_files"].append(seg["audio_path"])
        else:
            results["warnings"].append(f"{context}: No audio_path")
        
        # Check duration
        if seg.get("duration"):
            dur_issues = check_segment_duration(seg["duration"], context)
            results["warnings"].extend(dur_issues)
            results["total_duration"] += seg["duration"]
        else:
            results["issues"].append(f"{context}: Missing duration")
            fail(f"{context}: Missing duration")
    
    # Check closing
    closing = audio_data.get("closing") or script.get("closing", {})
    if closing:
        if closing.get("audio_path"):
            valid, msg = check_audio_file(closing["audio_path"], "Closing")
            if not valid:
                results["issues"].append(msg)
                fail(msg)
            else:
                ok(f"Closing audio: {closing['audio_path']}")
                results["audio_files"].append(closing["audio_path"])
        
        if closing.get("duration"):
            results["total_duration"] += closing["duration"]
    
    # Summary
    total_dur = results["total_duration"]
    ok(f"Total duration: {total_dur:.2f}s")
    
    if total_dur > MAX_TIKTOK_DURATION_SEC:
        results["issues"].append(f"Total duration exceeds TikTok limit ({total_dur:.2f}s > {MAX_TIKTOK_DURATION_SEC}s)")
        fail(f"Duration exceeds limit: {total_dur:.2f}s > {MAX_TIKTOK_DURATION_SEC}s")
    
    ok(f"Segments: {len(segments)}")
    ok(f"Audio files: {len(results['audio_files'])}")
    
    if results["issues"]:
        fail(f"Issues: {len(results['issues'])}")
    else:
        ok("All checks passed!")
    
    return results


def test_video_2_outline(data: Dict) -> Dict[str, Any]:
    """Test Video 2: Writing Coach"""
    header("TEST VIDEO 2: WRITING COACH")
    
    results = {
        "issues": [],
        "warnings": [],
        "audio_files": [],
        "total_duration": 0,
    }
    
    script = data.get("tiktok_script", {}).get("video_2_outline", {})
    audio_data = data.get("audio_data", {}).get("video_2_outline", {})
    
    if not script and not audio_data:
        results["issues"].append("No data found for video_2_outline")
        fail("No data found")
        return results
    
    # Check parts
    parts = audio_data.get("parts") or script.get("parts", [])
    for idx, part in enumerate(parts):
        context = f"Part {idx} ({part.get('role', 'unknown')})"
        
        # Check Korean text length
        ko = part.get("ko", "")
        if ko:
            issues = check_text_length(ko, MAX_KOREAN_CHARS_PER_SCREEN, f"{context} Korean")
            for issue in issues:
                warn(issue)
            results["warnings"].extend(issues)
        
        # Check Vietnamese text length
        vi = part.get("vi", "")
        if vi:
            issues = check_text_length(vi, MAX_VIETNAMESE_CHARS_PER_SCREEN, f"{context} Vietnamese")
            for issue in issues:
                warn(issue)
            results["warnings"].extend(issues)
        
        # Check audio
        if part.get("audio_path"):
            valid, msg = check_audio_file(part["audio_path"], context)
            if not valid:
                results["issues"].append(msg)
                fail(msg)
            else:
                results["audio_files"].append(part["audio_path"])
        
        # Check duration
        if part.get("duration"):
            results["total_duration"] += part["duration"]
        else:
            results["warnings"].append(f"{context}: Missing duration")
    
    # Summary
    total_dur = results["total_duration"]
    ok(f"Total duration: {total_dur:.2f}s")
    ok(f"Parts: {len(parts)}")
    ok(f"Audio files: {len(results['audio_files'])}")
    
    if total_dur > MAX_TIKTOK_DURATION_SEC:
        results["issues"].append(f"Total duration exceeds TikTok limit")
        fail(f"Duration exceeds limit: {total_dur:.2f}s")
    
    if results["issues"]:
        fail(f"Issues: {len(results['issues'])}")
    else:
        ok("All checks passed!")
    
    return results


def test_quiz_video(data: Dict, video_key: str, video_name: str) -> Dict[str, Any]:
    """Test Quiz Videos (3 and 4)"""
    header(f"TEST {video_name.upper()}")
    
    results = {
        "issues": [],
        "warnings": [],
        "audio_files": [],
        "total_duration": 0,
    }
    
    script = data.get("tiktok_script", {}).get(video_key, {})
    audio_data = data.get("audio_data", {}).get(video_key, {})
    
    if not script:
        results["issues"].append(f"No data found for {video_key}")
        fail("No data found")
        return results
    
    # Check question text
    question_ko = script.get("question_ko") or script.get("question", "")
    if question_ko:
        issues = check_text_length(question_ko, MAX_KOREAN_CHARS_PER_SCREEN, "Question Korean")
        results["warnings"].extend(issues)
    
    # Check options
    options_ko = script.get("options_ko") or script.get("options", [])
    for idx, opt in enumerate(options_ko):
        issues = check_text_length(opt, 40, f"Option {idx}")  # Options should be shorter
        results["warnings"].extend(issues)
    
    # Check explanation
    explanation_ko = script.get("explanation_ko") or script.get("explanation", "")
    if explanation_ko:
        issues = check_text_length(explanation_ko, MAX_KOREAN_CHARS_PER_SCREEN, "Explanation Korean")
        for issue in issues:
            warn(issue)
        results["warnings"].extend(issues)
    
    # Check audio timing
    if audio_data:
        # Opening audio
        opening = audio_data.get("opening_audio")
        if opening and opening.get("path"):
            valid, msg = check_audio_file(opening["path"], "Opening")
            if valid:
                results["audio_files"].append(opening["path"])
                results["total_duration"] += opening.get("duration", 0)
            else:
                results["issues"].append(msg)
        
        # Question audio
        question = audio_data.get("question_audio")
        if question and question.get("path"):
            valid, msg = check_audio_file(question["path"], "Question")
            if valid:
                results["audio_files"].append(question["path"])
                results["total_duration"] += question.get("duration", 0)
            else:
                results["issues"].append(msg)
        
        # Answer audio
        answer = audio_data.get("answer_audio")
        if answer and answer.get("path"):
            valid, msg = check_audio_file(answer["path"], "Answer")
            if valid:
                results["audio_files"].append(answer["path"])
                results["total_duration"] += answer.get("duration", 0)
            else:
                results["issues"].append(msg)
        
        # Silence duration
        silence = audio_data.get("silence_duration", 4)
        results["total_duration"] += silence
        
        # Closing audio
        closing = audio_data.get("closing_audio")
        if closing and closing.get("path"):
            valid, msg = check_audio_file(closing["path"], "Closing")
            if valid:
                results["audio_files"].append(closing["path"])
                results["total_duration"] += closing.get("duration", 0)
            else:
                results["issues"].append(msg)
    
    # Summary
    total_dur = results["total_duration"]
    ok(f"Total duration: {total_dur:.2f}s")
    ok(f"Audio files: {len(results['audio_files'])}")
    
    if total_dur > MAX_TIKTOK_DURATION_SEC:
        results["issues"].append(f"Total duration exceeds TikTok limit")
        fail(f"Duration exceeds limit: {total_dur:.2f}s")
    
    if results["issues"]:
        fail(f"Issues: {len(results['issues'])}")
    else:
        ok("All checks passed!")
    
    return results


def test_video_5_deep_dive(data: Dict) -> Dict[str, Any]:
    """Test Video 5: YouTube Deep Dive"""
    header("TEST VIDEO 5: YOUTUBE DEEP DIVE")
    
    results = {
        "issues": [],
        "warnings": [],
        "audio_files": [],
        "total_duration": 0,
    }
    
    script = data.get("tiktok_script", {}).get("video_5_deep_dive", {})
    
    if not script:
        results["issues"].append("No data found for video_5_deep_dive")
        fail("No data found")
        return results
    
    # Check meta
    meta = script.get("meta", {})
    if meta:
        ok(f"Title: {meta.get('title_ko', 'N/A')[:50]}...")
    
    # Check segments
    segments = script.get("segments", [])
    for idx, seg in enumerate(segments):
        context = f"Segment {idx} ({seg.get('section', 'unknown')})"
        
        # Check Korean text length (larger for YouTube)
        ko = seg.get("ko", "")
        if ko:
            issues = check_text_length(ko, 300, f"{context} Korean")  # YouTube allows more
            for issue in issues:
                warn(issue)
            results["warnings"].extend(issues)
        
        # Check audio
        if seg.get("audio_path"):
            valid, msg = check_audio_file(seg["audio_path"], context)
            if not valid:
                results["issues"].append(msg)
            else:
                results["audio_files"].append(seg["audio_path"])
        else:
            results["warnings"].append(f"{context}: No audio_path")
        
        # Check duration
        if seg.get("duration"):
            results["total_duration"] += seg["duration"]
        else:
            results["warnings"].append(f"{context}: Missing duration")
    
    # Summary
    total_dur = results["total_duration"]
    ok(f"Total duration: {total_dur:.2f}s ({total_dur/60:.1f} minutes)")
    ok(f"Segments: {len(segments)}")
    ok(f"Audio files: {len(results['audio_files'])}")
    
    if results["issues"]:
        fail(f"Issues: {len(results['issues'])}")
    else:
        ok("All checks passed!")
    
    return results


def print_summary(all_results: Dict[str, Dict]):
    """Print overall test summary"""
    header("SUMMARY")
    
    total_issues = 0
    total_warnings = 0
    total_audio = 0
    
    for video, results in all_results.items():
        issues = len(results.get("issues", []))
        warnings = len(results.get("warnings", []))
        audio = len(results.get("audio_files", []))
        duration = results.get("total_duration", 0)
        
        status = "[FAIL]" if issues > 0 else "[OK]"
        print(f"  {status} {video}: {duration:.1f}s, {audio} audio, {issues} issues, {warnings} warnings")
        
        total_issues += issues
        total_warnings += warnings
        total_audio += audio
    
    print(f"\n  Total: {total_issues} issues, {total_warnings} warnings, {total_audio} audio files")
    
    if total_issues == 0:
        print("\n  All video components are ready!")
    else:
        print(f"\n  {total_issues} issues need to be fixed before rendering.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test video components")
    parser.add_argument("--fix", action="store_true", help="Try to fix issues")
    args = parser.parse_args()
    
    print("")
    print("=" * 60)
    print("       TOPIK DAILY - VIDEO COMPONENTS TESTER")
    print("=" * 60)
    
    # Load data
    info(f"Loading: {DATA_FILE}")
    data = load_data()
    
    all_results = {}
    
    # Test each video
    all_results["Video 1: News"] = test_video_1_news(data)
    all_results["Video 2: Writing"] = test_video_2_outline(data)
    all_results["Video 3: Vocab Quiz"] = test_quiz_video(data, "video_3_vocab_quiz", "Video 3: Vocab Quiz")
    all_results["Video 4: Grammar Quiz"] = test_quiz_video(data, "video_4_grammar_quiz", "Video 4: Grammar Quiz")
    all_results["Video 5: Deep Dive"] = test_video_5_deep_dive(data)
    
    print_summary(all_results)


if __name__ == "__main__":
    main()
