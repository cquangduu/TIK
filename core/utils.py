"""
================================================================================
DAILY KOREAN — Utility Functions
================================================================================
Common utilities used across all modules.
================================================================================
"""

import os
import re
import json
import time
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, TypeVar
from functools import wraps

T = TypeVar('T')


# ─── File Operations ─────────────────────────────────────────────────────────

def safe_json_load(filepath: str | Path, default: Any = None) -> Any:
    """Safely load JSON file with error handling"""
    try:
        path = Path(filepath)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Error loading {filepath}: {e}")
    return default if default is not None else {}


def safe_json_save(data: Any, filepath: str | Path, indent: int = 2) -> bool:
    """Safely save data to JSON file"""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except IOError as e:
        print(f"❌ Error saving {filepath}: {e}")
        return False


def validate_file_exists(filepath: str | Path, raise_error: bool = False) -> bool:
    """Check if file exists"""
    exists = Path(filepath).exists()
    if not exists and raise_error:
        raise FileNotFoundError(f"File not found: {filepath}")
    return exists


def ensure_directory(path: str | Path) -> Path:
    """Ensure directory exists, create if not"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    Safe for Windows, macOS, and Linux.
    """
    # Normalize unicode characters
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Truncate if too long
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename or "untitled"


def get_file_hash(filepath: str | Path, algorithm: str = "md5") -> str:
    """Calculate file hash for deduplication"""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


# ─── Text Processing ─────────────────────────────────────────────────────────

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace"""
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_sentences(text: str, lang: str = "ko") -> List[str]:
    """Split text into sentences"""
    if lang == "ko":
        # Korean sentence endings
        pattern = r'(?<=[.?!。！？])\s+'
    else:
        pattern = r'(?<=[.?!])\s+'
    
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def count_words(text: str, lang: str = "ko") -> int:
    """Count words in text"""
    if lang == "ko":
        # Korean: count by syllables/characters (excluding spaces)
        return len(re.findall(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]+', text))
    else:
        return len(text.split())


def estimate_reading_time(text: str, wpm: int = 200) -> float:
    """Estimate reading time in minutes"""
    word_count = count_words(text)
    return word_count / wpm


# ─── Time & Date ─────────────────────────────────────────────────────────────

def format_duration(seconds: float) -> str:
    """Format duration as HH:MM:SS or MM:SS"""
    if seconds < 0:
        return "00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_number(num: int | float, precision: int = 1) -> str:
    """Format large numbers with K, M, B suffixes"""
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.{precision}f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.{precision}f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.{precision}f}K"
    return str(int(num))


def get_date_range(days: int = 7) -> List[str]:
    """Get list of dates for the past N days"""
    today = datetime.now()
    return [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(days)
    ]


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string to datetime object"""
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


# ─── Retry & Error Handling ──────────────────────────────────────────────────

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap
        exponential: Use exponential backoff (2^n)
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if exponential:
                            delay = min(base_delay * (2 ** attempt), max_delay)
                        else:
                            delay = base_delay
                        
                        print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                        time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0.0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        now = time.time()
        elapsed = now - self.last_call
        
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_call = time.time()
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Use as decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self.wait()
            return func(*args, **kwargs)
        return wrapper


# ─── Validation ──────────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
    return bool(re.match(pattern, url))


def validate_korean_text(text: str) -> bool:
    """Check if text contains Korean characters"""
    return bool(re.search(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]', text))


# ─── Korean Language Helpers ─────────────────────────────────────────────────

def get_korean_particle(word: str, particle_with_final: str, particle_without_final: str) -> str:
    """
    Get correct Korean particle based on 받침 (final consonant).
    
    Example:
        get_korean_particle("학교", "를", "을") -> "를"
        get_korean_particle("집", "을", "를") -> "을"
    """
    if not word:
        return particle_with_final
    
    last_char = word[-1]
    
    # Check if it's a Korean syllable
    if '\uAC00' <= last_char <= '\uD7AF':
        # Calculate if it has final consonant (받침)
        code = ord(last_char) - 0xAC00
        has_final = (code % 28) != 0
        return particle_without_final if has_final else particle_with_final
    
    return particle_with_final


def romanize_korean(text: str) -> str:
    """
    Simple romanization of Korean text (basic conversion).
    For production, use a proper library like korean-romanizer.
    """
    # This is a simplified version - use a proper library for accuracy
    romanization_map = {
        'ㄱ': 'g', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄹ': 'r', 'ㅁ': 'm',
        'ㅂ': 'b', 'ㅅ': 's', 'ㅇ': '', 'ㅈ': 'j', 'ㅊ': 'ch',
        'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h',
        'ㅏ': 'a', 'ㅓ': 'eo', 'ㅗ': 'o', 'ㅜ': 'u', 'ㅡ': 'eu',
        'ㅣ': 'i', 'ㅐ': 'ae', 'ㅔ': 'e', 'ㅚ': 'oe', 'ㅟ': 'wi',
    }
    
    result = []
    for char in text:
        if char in romanization_map:
            result.append(romanization_map[char])
        elif '\uAC00' <= char <= '\uD7AF':
            # For full syllables, just keep original for now
            result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)


# ─── Progress Tracking ───────────────────────────────────────────────────────

class ProgressTracker:
    """Simple progress tracker for long-running tasks"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        self._print_progress()
    
    def _print_progress(self):
        """Print progress bar"""
        percent = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        # Estimate remaining time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = format_duration(eta)
        else:
            eta_str = "--:--"
        
        bar_length = 30
        filled = int(bar_length * self.current / self.total) if self.total > 0 else 0
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\r{self.description}: [{bar}] {percent:.1f}% ({self.current}/{self.total}) ETA: {eta_str}", end='')
        
        if self.current >= self.total:
            print()  # New line when done
    
    def complete(self):
        """Mark as complete"""
        self.current = self.total
        self._print_progress()
        elapsed = time.time() - self.start_time
        print(f"✅ Completed in {format_duration(elapsed)}")
