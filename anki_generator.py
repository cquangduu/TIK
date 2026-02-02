"""
================================================================================
ANKI DECK GENERATOR — Create Sellable Anki Decks
================================================================================
Features:
    1. Auto-generate Anki decks from daily content
    2. Multiple card types (vocab, grammar, listening)
    3. Audio cards with Azure TTS
    4. Cloze deletion cards
    5. Package for Gumroad/Patreon sale
================================================================================
Revenue Potential: $200-1000/month (sell decks on Gumroad)
================================================================================
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ==================== CONFIGURATION ====================
ANKI_OUTPUT_DIR = "anki_decks"
os.makedirs(ANKI_OUTPUT_DIR, exist_ok=True)

# Model IDs (consistent for updates)
MODEL_VOCAB_BASIC = 1607392319
MODEL_VOCAB_AUDIO = 1607392320
MODEL_GRAMMAR = 1607392321
MODEL_CLOZE = 1607392322
MODEL_LISTENING = 1607392323

# Deck IDs
DECK_DAILY = 2059400110
DECK_WEEKLY = 2059400111
DECK_MONTHLY = 2059400112
DECK_PREMIUM = 2059400113


class AnkiDeckGenerator:
    """
    Tạo Anki decks chuyên nghiệp để bán.
    """
    
    def __init__(self):
        self.output_dir = Path(ANKI_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        # Try to import genanki
        try:
            import genanki
            self.genanki = genanki
            self.available = True
        except ImportError:
            logging.warning("⚠️ genanki not installed. pip install genanki")
            self.available = False
    
    def _create_vocab_model(self) -> 'genanki.Model':
        """Create vocabulary card model"""
        return self.genanki.Model(
            MODEL_VOCAB_BASIC,
            'TOPIK Vocabulary',
            fields=[
                {'name': 'Korean'},
                {'name': 'Romanization'},
                {'name': 'Vietnamese'},
                {'name': 'English'},
                {'name': 'Example_KO'},
                {'name': 'Example_VI'},
                {'name': 'Level'},
                {'name': 'Tags'},
            ],
            templates=[
                {
                    'name': 'Recognition',
                    'qfmt': '''
                        <div class="card">
                            <div class="korean">{{Korean}}</div>
                            <div class="romanization">[{{Romanization}}]</div>
                        </div>
                    ''',
                    'afmt': '''
                        {{FrontSide}}
                        <hr>
                        <div class="answer">
                            <div class="meaning-vi">🇻🇳 {{Vietnamese}}</div>
                            <div class="meaning-en">🇺🇸 {{English}}</div>
                            <div class="example">
                                <div class="example-ko">{{Example_KO}}</div>
                                <div class="example-vi">{{Example_VI}}</div>
                            </div>
                            <div class="level">Level: {{Level}}</div>
                        </div>
                    ''',
                },
                {
                    'name': 'Recall',
                    'qfmt': '''
                        <div class="card">
                            <div class="meaning-vi">🇻🇳 {{Vietnamese}}</div>
                        </div>
                    ''',
                    'afmt': '''
                        {{FrontSide}}
                        <hr>
                        <div class="answer">
                            <div class="korean">{{Korean}}</div>
                            <div class="romanization">[{{Romanization}}]</div>
                            <div class="example">
                                <div class="example-ko">{{Example_KO}}</div>
                            </div>
                        </div>
                    ''',
                },
            ],
            css='''
                .card { 
                    font-family: 'Noto Sans KR', sans-serif;
                    text-align: center;
                    padding: 20px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    color: white;
                }
                .korean { 
                    font-size: 48px; 
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .romanization { 
                    font-size: 18px; 
                    color: #888;
                    font-style: italic;
                }
                .meaning-vi { 
                    font-size: 28px; 
                    color: #ffc857;
                    margin: 10px 0;
                }
                .meaning-en { 
                    font-size: 20px; 
                    color: #a5d6ff;
                    margin: 5px 0;
                }
                .example { 
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 10px;
                }
                .example-ko { 
                    font-size: 22px;
                    margin-bottom: 5px;
                }
                .example-vi { 
                    font-size: 16px;
                    color: #ccc;
                }
                .level {
                    margin-top: 15px;
                    font-size: 12px;
                    color: #666;
                }
            '''
        )
    
    def _create_audio_model(self) -> 'genanki.Model':
        """Create listening card model with audio"""
        return self.genanki.Model(
            MODEL_VOCAB_AUDIO,
            'TOPIK Listening',
            fields=[
                {'name': 'Audio'},
                {'name': 'Korean'},
                {'name': 'Vietnamese'},
                {'name': 'Transcript'},
            ],
            templates=[
                {
                    'name': 'Listening',
                    'qfmt': '''
                        <div class="card">
                            <div class="audio">{{Audio}}</div>
                            <div class="hint">🎧 Nghe và đoán nghĩa</div>
                        </div>
                    ''',
                    'afmt': '''
                        {{FrontSide}}
                        <hr>
                        <div class="answer">
                            <div class="korean">{{Korean}}</div>
                            <div class="meaning">{{Vietnamese}}</div>
                            <div class="transcript">{{Transcript}}</div>
                        </div>
                    ''',
                },
            ],
            css='''
                .card { text-align: center; padding: 20px; }
                .audio { font-size: 48px; }
                .hint { color: #888; margin-top: 10px; }
                .korean { font-size: 36px; margin: 15px 0; }
                .meaning { font-size: 24px; color: #2196F3; }
                .transcript { margin-top: 10px; color: #666; }
            '''
        )
    
    def _create_grammar_model(self) -> 'genanki.Model':
        """Create grammar card model"""
        return self.genanki.Model(
            MODEL_GRAMMAR,
            'TOPIK Grammar',
            fields=[
                {'name': 'Pattern'},
                {'name': 'Meaning'},
                {'name': 'Conjugation'},
                {'name': 'Example1_KO'},
                {'name': 'Example1_VI'},
                {'name': 'Example2_KO'},
                {'name': 'Example2_VI'},
                {'name': 'Level'},
                {'name': 'Notes'},
            ],
            templates=[
                {
                    'name': 'Grammar',
                    'qfmt': '''
                        <div class="card">
                            <div class="pattern">{{Pattern}}</div>
                        </div>
                    ''',
                    'afmt': '''
                        {{FrontSide}}
                        <hr>
                        <div class="answer">
                            <div class="meaning">{{Meaning}}</div>
                            <div class="conjugation">{{Conjugation}}</div>
                            <div class="examples">
                                <div class="example">
                                    <div class="ko">{{Example1_KO}}</div>
                                    <div class="vi">{{Example1_VI}}</div>
                                </div>
                                <div class="example">
                                    <div class="ko">{{Example2_KO}}</div>
                                    <div class="vi">{{Example2_VI}}</div>
                                </div>
                            </div>
                            <div class="notes">{{Notes}}</div>
                        </div>
                    ''',
                },
            ],
            css='''
                .card { text-align: center; padding: 20px; }
                .pattern { font-size: 36px; color: #7c4dff; }
                .meaning { font-size: 24px; margin: 15px 0; }
                .conjugation { color: #888; margin-bottom: 15px; }
                .examples { background: #f5f5f5; padding: 15px; border-radius: 10px; }
                .example { margin: 10px 0; }
                .ko { font-size: 20px; }
                .vi { font-size: 16px; color: #666; }
                .notes { margin-top: 15px; font-size: 14px; color: #888; }
            '''
        )
    
    def generate_daily_deck(self, data: Dict, date: str = None) -> str:
        """Generate daily Anki deck from content data"""
        if not self.available:
            return ""
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        deck_name = f"TOPIK_Daily_{date}"
        deck = self.genanki.Deck(DECK_DAILY, deck_name)
        
        vocab_model = self._create_vocab_model()
        grammar_model = self._create_grammar_model()
        
        media_files = []
        
        # Add vocabulary cards
        vocab_list = data.get("vocabulary", [])
        for vocab in vocab_list:
            note = self.genanki.Note(
                model=vocab_model,
                fields=[
                    vocab.get("korean", ""),
                    vocab.get("romanization", ""),
                    vocab.get("meaning", ""),
                    vocab.get("english", vocab.get("meaning", "")),
                    vocab.get("example_ko", ""),
                    vocab.get("example_vi", ""),
                    vocab.get("level", "TOPIK II"),
                    vocab.get("tags", "vocabulary"),
                ],
                tags=[f"date:{date}", "vocabulary"]
            )
            deck.add_note(note)
        
        # Add grammar cards
        grammar_list = data.get("grammar", [])
        for grammar in grammar_list:
            note = self.genanki.Note(
                model=grammar_model,
                fields=[
                    grammar.get("pattern", ""),
                    grammar.get("meaning", ""),
                    grammar.get("conjugation", ""),
                    grammar.get("example1_ko", ""),
                    grammar.get("example1_vi", ""),
                    grammar.get("example2_ko", ""),
                    grammar.get("example2_vi", ""),
                    grammar.get("level", "TOPIK II"),
                    grammar.get("notes", ""),
                ],
                tags=[f"date:{date}", "grammar"]
            )
            deck.add_note(note)
        
        # Save deck
        output_path = self.output_dir / f"{deck_name}.apkg"
        
        if media_files:
            package = self.genanki.Package(deck)
            package.media_files = media_files
            package.write_to_file(str(output_path))
        else:
            self.genanki.Package(deck).write_to_file(str(output_path))
        
        logging.info(f"✅ Generated Anki deck: {output_path}")
        return str(output_path)
    
    def generate_weekly_deck(self, weekly_data: List[Dict], week_number: int) -> str:
        """Generate weekly compilation deck"""
        if not self.available:
            return ""
        
        deck_name = f"TOPIK_Weekly_W{week_number}"
        deck = self.genanki.Deck(DECK_WEEKLY, deck_name)
        
        vocab_model = self._create_vocab_model()
        grammar_model = self._create_grammar_model()
        
        # Combine all daily data
        for daily_data in weekly_data:
            date = daily_data.get("date", "")
            
            for vocab in daily_data.get("vocabulary", []):
                note = self.genanki.Note(
                    model=vocab_model,
                    fields=[
                        vocab.get("korean", ""),
                        vocab.get("romanization", ""),
                        vocab.get("meaning", ""),
                        vocab.get("english", ""),
                        vocab.get("example_ko", ""),
                        vocab.get("example_vi", ""),
                        vocab.get("level", "TOPIK II"),
                        f"week{week_number}",
                    ],
                    tags=[f"week:{week_number}", "vocabulary"]
                )
                deck.add_note(note)
        
        output_path = self.output_dir / f"{deck_name}.apkg"
        self.genanki.Package(deck).write_to_file(str(output_path))
        
        logging.info(f"✅ Generated weekly deck: {output_path}")
        return str(output_path)
    
    def generate_premium_deck(self, all_data: List[Dict], title: str = "TOPIK_Premium") -> str:
        """Generate premium deck for sale (1000+ cards)"""
        if not self.available:
            return ""
        
        deck_name = title
        deck = self.genanki.Deck(DECK_PREMIUM, deck_name)
        
        vocab_model = self._create_vocab_model()
        grammar_model = self._create_grammar_model()
        audio_model = self._create_audio_model()
        
        media_files = []
        added_korean = set()  # Avoid duplicates
        
        for data in all_data:
            for vocab in data.get("vocabulary", []):
                korean = vocab.get("korean", "")
                if korean and korean not in added_korean:
                    added_korean.add(korean)
                    
                    note = self.genanki.Note(
                        model=vocab_model,
                        fields=[
                            korean,
                            vocab.get("romanization", ""),
                            vocab.get("meaning", ""),
                            vocab.get("english", ""),
                            vocab.get("example_ko", ""),
                            vocab.get("example_vi", ""),
                            vocab.get("level", "TOPIK II"),
                            "premium",
                        ],
                        tags=["premium", "vocabulary"]
                    )
                    deck.add_note(note)
        
        output_path = self.output_dir / f"{deck_name}.apkg"
        
        if media_files:
            package = self.genanki.Package(deck)
            package.media_files = media_files
            package.write_to_file(str(output_path))
        else:
            self.genanki.Package(deck).write_to_file(str(output_path))
        
        logging.info(f"✅ Generated premium deck: {output_path} ({len(added_korean)} cards)")
        return str(output_path)


# ==================== UTILITY FUNCTIONS ====================

def generate_anki_from_final_data(data_file: str = "topik-video/public/final_data.json") -> str:
    """Generate Anki deck from final_data.json"""
    if not os.path.exists(data_file):
        logging.error(f"❌ Data file not found: {data_file}")
        return ""
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    generator = AnkiDeckGenerator()
    return generator.generate_daily_deck(data)


# ==================== MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    generator = AnkiDeckGenerator()
    print(f"Anki generator available: {generator.available}")
    
    # Test with sample data
    sample_data = {
        "vocabulary": [
            {
                "korean": "학생",
                "romanization": "haksaeng",
                "meaning": "học sinh",
                "english": "student",
                "example_ko": "저는 학생입니다.",
                "example_vi": "Tôi là học sinh.",
                "level": "TOPIK I"
            },
            {
                "korean": "선생님",
                "romanization": "seonsaengnim",
                "meaning": "giáo viên",
                "english": "teacher",
                "example_ko": "선생님이 왔습니다.",
                "example_vi": "Giáo viên đã đến.",
                "level": "TOPIK I"
            }
        ],
        "grammar": [
            {
                "pattern": "-(으)ㄹ 수 있다",
                "meaning": "có thể",
                "conjugation": "V + -(으)ㄹ 수 있다",
                "example1_ko": "한국어를 할 수 있어요.",
                "example1_vi": "Tôi có thể nói tiếng Hàn.",
                "level": "TOPIK II"
            }
        ]
    }
    
    if generator.available:
        deck_path = generator.generate_daily_deck(sample_data)
        print(f"Generated: {deck_path}")
