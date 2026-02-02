

import sys
import os
from pathlib import Path

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Colors for terminal (simple version for Windows compatibility)
class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    CYAN = ''
    RESET = ''
    BOLD = ''

# Try to enable colors on Windows
try:
    import os
    os.system('')  # Enable ANSI on Windows
    class Colors:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
except:
    pass

def ok(msg): print(f"  [OK] {msg}")
def fail(msg): print(f"  [FAIL] {msg}")
def warn(msg): print(f"  [WARN] {msg}")
def info(msg): print(f"  [INFO] {msg}")
def header(msg): print(f"\n{'='*60}\n{msg}\n{'='*60}")

# ==================== TEST FUNCTIONS ====================

def test_core_imports():
    """Test các thư viện core"""
    header("TEST CORE IMPORTS")
    results = {}
    
    core_libs = [
        ("requests", "HTTP Client"),
        ("bs4", "BeautifulSoup - Web Scraping"),
        ("pydub", "Audio Processing"),
        ("dotenv", "Environment Variables"),
        ("PIL", "Pillow - Image Processing"),
    ]
    
    for lib, desc in core_libs:
        try:
            __import__(lib)
            ok(f"{desc}")
            results[lib] = True
        except ImportError:
            fail(f"{desc} - pip install {lib}")
            results[lib] = False
    
    return results


def test_google_apis():
    """Test Google APIs"""
    header("TEST GOOGLE APIs")
    results = {}
    
    google_libs = [
        ("google.auth", "Google Auth"),
        ("google.oauth2.credentials", "Google OAuth2"),
        ("googleapiclient.discovery", "Google API Client"),
    ]
    
    for lib, desc in google_libs:
        try:
            __import__(lib)
            ok(f"{desc}")
            results[lib] = True
        except ImportError:
            fail(f"{desc}")
            results[lib] = False
    
    return results


def test_tts_engines():
    """Test TTS engines"""
    header("TEST TTS ENGINES")
    results = {}
    
    # Azure TTS
    try:
        import azure.cognitiveservices.speech as speechsdk
        ok("Azure TTS")
        results['azure'] = True
    except ImportError:
        warn("Azure TTS không được cài đặt")
        results['azure'] = False
    
    # Edge TTS
    try:
        import edge_tts
        ok("Edge TTS (fallback)")
        results['edge'] = True
    except ImportError:
        warn("Edge TTS không được cài đặt")
        results['edge'] = False
    
    return results


def test_document_libs():
    """Test Document generation libraries"""
    header("TEST DOCUMENT LIBRARIES")
    results = {}
    
    doc_libs = [
        ("docx", "python-docx - Word Documents"),
        ("reportlab", "ReportLab - PDF Generation"),
        ("genanki", "Genanki - Anki Flashcards"),
    ]
    
    for lib, desc in doc_libs:
        try:
            __import__(lib)
            ok(f"{desc}")
            results[lib] = True
        except ImportError:
            fail(f"{desc}")
            results[lib] = False
    
    return results


def test_project_modules():
    """Test các module của project"""
    header("TEST PROJECT MODULES")
    results = {}
    
    modules = [
        ("main", "Main Pipeline"),
        ("run", "Unified Runner"),
        ("blog_generator", "Blog Generator"),
        ("youtube_uploader", "YouTube Uploader"),
        ("telegram_bot", "Telegram Bot"),
        ("anki_generator", "Anki Generator"),
        ("podcast_generator", "Podcast Generator"),
        ("social_publisher", "Social Publisher"),
        ("seo_optimizer", "SEO Optimizer"),
        ("monetization", "Monetization"),
        ("premium_gatekeeper", "Premium Gatekeeper"),
        ("email_marketing", "Email Marketing"),
        ("api_server", "API Server"),
        ("analytics_dashboard", "Analytics Dashboard"),
    ]
    
    for module, desc in modules:
        try:
            __import__(module)
            ok(f"{desc}")
            results[module] = True
        except ImportError as e:
            fail(f"{desc}: {e}")
            results[module] = False
        except Exception as e:
            warn(f"{desc}: {type(e).__name__}")
            results[module] = "warn"
    
    return results


def test_env_variables():
    """Test environment variables"""
    header("TEST ENVIRONMENT VARIABLES")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    env_vars = [
        ("GEMINI_API_KEY", "Gemini AI API"),
        ("AZURE_SPEECH_KEY", "Azure TTS"),
        ("AZURE_SPEECH_REGION", "Azure Region"),
        ("TELEGRAM_BOT_TOKEN", "Telegram Bot"),
        ("GOOGLE_DRIVE_FOLDER_ID", "Google Drive"),
    ]
    
    results = {}
    for var, desc in env_vars:
        value = os.environ.get(var)
        if value:
            # Ẩn phần lớn key
            masked = value[:4] + "..." + value[-4:] if len(value) > 10 else "***"
            ok(f"{desc}: {masked}")
            results[var] = True
        else:
            warn(f"{desc}: Chưa cấu hình")
            results[var] = False
    
    return results


def test_api_connections():
    """Test API connections (requires API keys)"""
    header("TEST API CONNECTIONS")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    results = {}
    
    # Test Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            import requests
            resp = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}",
                timeout=10
            )
            if resp.status_code == 200:
                ok("Gemini API: Connected")
                results['gemini'] = True
            else:
                fail(f"Gemini API: Status {resp.status_code}")
                results['gemini'] = False
        except Exception as e:
            fail(f"Gemini API: {e}")
            results['gemini'] = False
    else:
        warn("Gemini API: Key not configured")
        results['gemini'] = None
    
    # Test Azure TTS
    azure_key = os.environ.get("AZURE_SPEECH_KEY")
    azure_region = os.environ.get("AZURE_SPEECH_REGION", "eastasia")
    if azure_key:
        try:
            import requests
            resp = requests.post(
                f"https://{azure_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
                headers={"Ocp-Apim-Subscription-Key": azure_key},
                timeout=10
            )
            if resp.status_code == 200:
                ok("Azure TTS: Connected")
                results['azure_tts'] = True
            else:
                fail(f"Azure TTS: Status {resp.status_code}")
                results['azure_tts'] = False
        except Exception as e:
            fail(f"Azure TTS: {e}")
            results['azure_tts'] = False
    else:
        warn("Azure TTS: Key not configured")
        results['azure_tts'] = None
    
    return results


def test_file_structure():
    """Test file/folder structure"""
    header("TEST FILE STRUCTURE")
    
    root = Path(__file__).parent
    
    required = [
        ("temp_processing", "folder"),
        ("logs", "folder"),
        ("topik-video", "folder"),
        ("blog_output", "folder"),
        (".env", "file"),
        ("requirements.txt", "file"),
    ]
    
    results = {}
    for name, ftype in required:
        path = root / name
        if ftype == "folder":
            if path.is_dir():
                ok(f"{name}/")
                results[name] = True
            else:
                warn(f"{name}/ - Creating...")
                path.mkdir(exist_ok=True)
                results[name] = "created"
        else:
            if path.is_file():
                ok(f"{name}")
                results[name] = True
            else:
                fail(f"{name} - Missing")
                results[name] = False
    
    return results


def test_remotion():
    """Test Remotion setup"""
    header("TEST REMOTION (Video Rendering)")
    
    root = Path(__file__).parent
    remotion_dir = root / "topik-video"
    
    if not remotion_dir.exists():
        fail("topik-video folder not found")
        return {"remotion": False}
    
    # Check package.json
    if (remotion_dir / "package.json").exists():
        ok("package.json exists")
    else:
        fail("package.json missing")
        return {"remotion": False}
    
    # Check node_modules
    if (remotion_dir / "node_modules").exists():
        ok("node_modules installed")
    else:
        warn("node_modules not installed - run: cd topik-video && npm install")
    
    # Check final_data.json
    if (remotion_dir / "public" / "final_data.json").exists():
        ok("final_data.json exists")
    else:
        warn("final_data.json not found - run main.py first")
    
    return {"remotion": True}


def print_summary(all_results):
    """Print test summary"""
    header("SUMMARY")
    
    total = 0
    passed = 0
    warned = 0
    failed = 0
    
    for category, results in all_results.items():
        if isinstance(results, dict):
            for key, value in results.items():
                total += 1
                if value == True:
                    passed += 1
                elif value == "warn" or value == "created":
                    warned += 1
                else:
                    failed += 1
    
    print(f"\n  [OK] Passed: {passed}")
    print(f"  [WARN] Warnings: {warned}")
    print(f"  [FAIL] Failed: {failed}")
    print(f"  Total: {total}")
    
    if failed == 0:
        print(f"\n  All tests passed! System ready.")
    elif failed < 5:
        print(f"\n  Some issues found. Check above.")
    else:
        print(f"\n  Multiple issues found. Fix before running.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test TOPIK Daily modules")
    parser.add_argument("--quick", action="store_true", help="Only test imports")
    parser.add_argument("--api", action="store_true", help="Test API connections")
    parser.add_argument("--env", action="store_true", help="Test environment only")
    args = parser.parse_args()
    
    print("")
    print("=" * 60)
    print("          TOPIK DAILY - MODULE TESTER")
    print("=" * 60)
    print("")
    
    all_results = {}
    
    if args.env:
        all_results["env"] = test_env_variables()
        print_summary(all_results)
        return
    
    # Always test these
    all_results["core"] = test_core_imports()
    all_results["google"] = test_google_apis()
    all_results["tts"] = test_tts_engines()
    all_results["docs"] = test_document_libs()
    
    if not args.quick:
        all_results["modules"] = test_project_modules()
        all_results["files"] = test_file_structure()
        all_results["remotion"] = test_remotion()
    
    all_results["env"] = test_env_variables()
    
    if args.api:
        all_results["api"] = test_api_connections()
    
    print_summary(all_results)


if __name__ == "__main__":
    main()
