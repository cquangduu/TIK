"""
================================================================================
COURSE GENERATOR — Create & Sell Online Courses
================================================================================
Features:
    1. Auto-generate course curriculum from content
    2. Create course modules with lessons
    3. Generate quizzes & assignments
    4. Export to Udemy/Teachable format
    5. Track student progress
================================================================================
Revenue Potential: $500-5000/month (Udemy/Teachable courses)
================================================================================
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# ==================== CONFIGURATION ====================
COURSES_DIR = Path("courses")
COURSES_DIR.mkdir(exist_ok=True)


# ==================== COURSE TEMPLATES ====================

TOPIK_1_CURRICULUM = {
    "title": "TOPIK I Complete - Từ 0 đến Level 2",
    "description": "Khóa học tiếng Hàn toàn diện dành cho người mới bắt đầu, chuẩn bị cho kỳ thi TOPIK I.",
    "level": "Beginner",
    "duration_weeks": 12,
    "modules": [
        {
            "id": 1,
            "title": "Module 1: Bảng chữ cái Hangul",
            "description": "Làm quen với bảng chữ cái tiếng Hàn",
            "duration_days": 7,
            "lessons": [
                {"id": 1, "title": "Giới thiệu Hangul", "type": "video", "duration_min": 15},
                {"id": 2, "title": "Nguyên âm cơ bản", "type": "video", "duration_min": 20},
                {"id": 3, "title": "Phụ âm cơ bản", "type": "video", "duration_min": 20},
                {"id": 4, "title": "Ghép vần", "type": "video", "duration_min": 25},
                {"id": 5, "title": "Luyện đọc", "type": "practice", "duration_min": 30},
                {"id": 6, "title": "Quiz: Hangul", "type": "quiz", "questions": 20},
            ]
        },
        {
            "id": 2,
            "title": "Module 2: Chào hỏi & Giới thiệu",
            "description": "Cách chào hỏi và tự giới thiệu bằng tiếng Hàn",
            "duration_days": 7,
            "lessons": [
                {"id": 1, "title": "Các cách chào hỏi", "type": "video", "duration_min": 20},
                {"id": 2, "title": "Tự giới thiệu bản thân", "type": "video", "duration_min": 25},
                {"id": 3, "title": "Danh xưng và cách xưng hô", "type": "video", "duration_min": 20},
                {"id": 4, "title": "Ngữ pháp: 입니다/예요", "type": "video", "duration_min": 25},
                {"id": 5, "title": "Luyện hội thoại", "type": "practice", "duration_min": 30},
                {"id": 6, "title": "Quiz: Chào hỏi", "type": "quiz", "questions": 15},
            ]
        },
        {
            "id": 3,
            "title": "Module 3: Số đếm",
            "description": "Hệ thống số đếm Hàn Quốc và Sino-Korean",
            "duration_days": 7,
            "lessons": [
                {"id": 1, "title": "Số đếm Hàn thuần (하나, 둘, 셋)", "type": "video", "duration_min": 25},
                {"id": 2, "title": "Số đếm Sino-Korean (일, 이, 삼)", "type": "video", "duration_min": 25},
                {"id": 3, "title": "Đọc ngày tháng", "type": "video", "duration_min": 20},
                {"id": 4, "title": "Đọc giờ", "type": "video", "duration_min": 20},
                {"id": 5, "title": "Đơn vị đếm", "type": "video", "duration_min": 25},
                {"id": 6, "title": "Quiz: Số đếm", "type": "quiz", "questions": 20},
            ]
        },
        # ... thêm modules khác
    ]
}

TOPIK_2_CURRICULUM = {
    "title": "TOPIK II Mastery - Level 3 đến Level 6",
    "description": "Khóa học chuyên sâu dành cho người muốn đạt TOPIK II cấp cao.",
    "level": "Intermediate to Advanced",
    "duration_weeks": 24,
    "modules": [
        {
            "id": 1,
            "title": "Module 1: Ngữ pháp nâng cao",
            "description": "Các cấu trúc ngữ pháp TOPIK II quan trọng",
            "duration_days": 14,
            "lessons": [
                {"id": 1, "title": "-(으)ㄴ/는데", "type": "video", "duration_min": 30},
                {"id": 2, "title": "-(으)면서", "type": "video", "duration_min": 25},
                {"id": 3, "title": "-다가", "type": "video", "duration_min": 25},
                {"id": 4, "title": "-(으)ㄹ 뿐만 아니라", "type": "video", "duration_min": 30},
                {"id": 5, "title": "Practice: Ngữ pháp", "type": "practice", "duration_min": 45},
                {"id": 6, "title": "Quiz: Ngữ pháp Module 1", "type": "quiz", "questions": 30},
            ]
        },
        {
            "id": 2,
            "title": "Module 2: Đọc hiểu chuyên sâu",
            "description": "Chiến lược đọc hiểu cho TOPIK II",
            "duration_days": 14,
            "lessons": [
                {"id": 1, "title": "Phân tích cấu trúc đoạn văn", "type": "video", "duration_min": 35},
                {"id": 2, "title": "Tìm ý chính", "type": "video", "duration_min": 30},
                {"id": 3, "title": "Suy luận thông tin", "type": "video", "duration_min": 30},
                {"id": 4, "title": "Đọc nhanh hiệu quả", "type": "video", "duration_min": 25},
                {"id": 5, "title": "Practice: Đề đọc thử", "type": "practice", "duration_min": 60},
                {"id": 6, "title": "Quiz: Đọc hiểu", "type": "quiz", "questions": 25},
            ]
        },
        {
            "id": 3,
            "title": "Module 3: Viết văn TOPIK 54",
            "description": "Chiến lược viết bài văn 200-300 chữ",
            "duration_days": 14,
            "lessons": [
                {"id": 1, "title": "Cấu trúc bài văn TOPIK", "type": "video", "duration_min": 40},
                {"id": 2, "title": "Viết đoạn mở bài", "type": "video", "duration_min": 30},
                {"id": 3, "title": "Phát triển thân bài", "type": "video", "duration_min": 35},
                {"id": 4, "title": "Kết luận ấn tượng", "type": "video", "duration_min": 25},
                {"id": 5, "title": "Các mẫu câu nâng cao", "type": "video", "duration_min": 35},
                {"id": 6, "title": "Practice: Viết bài văn", "type": "assignment", "duration_min": 90},
            ]
        },
    ]
}


class CourseGenerator:
    """
    Generate courses from content data.
    """
    
    def __init__(self):
        self.output_dir = COURSES_DIR
    
    def generate_course_from_template(self, template: Dict, output_name: str) -> str:
        """Generate course files from template"""
        
        course_dir = self.output_dir / output_name
        course_dir.mkdir(exist_ok=True)
        
        # Create course structure
        course_data = {
            "meta": {
                "title": template["title"],
                "description": template["description"],
                "level": template["level"],
                "duration_weeks": template["duration_weeks"],
                "created_at": datetime.now().isoformat(),
            },
            "modules": template["modules"],
            "statistics": {
                "total_modules": len(template["modules"]),
                "total_lessons": sum(len(m["lessons"]) for m in template["modules"]),
                "total_quizzes": sum(1 for m in template["modules"] for l in m["lessons"] if l["type"] == "quiz"),
            }
        }
        
        # Save course JSON
        course_file = course_dir / "course.json"
        with open(course_file, "w", encoding="utf-8") as f:
            json.dump(course_data, f, ensure_ascii=False, indent=2)
        
        # Create module directories
        for module in template["modules"]:
            module_dir = course_dir / f"module_{module['id']:02d}"
            module_dir.mkdir(exist_ok=True)
            
            # Create module info
            module_info = {
                "id": module["id"],
                "title": module["title"],
                "description": module["description"],
                "lessons": module["lessons"],
            }
            
            with open(module_dir / "module.json", "w", encoding="utf-8") as f:
                json.dump(module_info, f, ensure_ascii=False, indent=2)
        
        logging.info(f"✅ Generated course: {output_name}")
        return str(course_dir)
    
    def generate_from_daily_content(self, content_files: List[str], course_name: str) -> str:
        """Generate course from accumulated daily content"""
        
        course_dir = self.output_dir / course_name
        course_dir.mkdir(exist_ok=True)
        
        # Load all content
        all_vocabulary = []
        all_grammar = []
        all_quizzes = []
        
        for content_file in content_files:
            if os.path.exists(content_file):
                with open(content_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                all_vocabulary.extend(data.get("vocabulary", []))
                all_grammar.extend(data.get("grammar", []))
                
                # Extract quizzes
                if "video_3" in data:
                    all_quizzes.append(data["video_3"])
                if "video_4" in data:
                    all_quizzes.append(data["video_4"])
        
        # Remove duplicates
        seen_vocab = set()
        unique_vocab = []
        for v in all_vocabulary:
            key = v.get("korean", "")
            if key and key not in seen_vocab:
                seen_vocab.add(key)
                unique_vocab.append(v)
        
        # Create modules (group by 20 vocabulary items)
        modules = []
        vocab_per_module = 20
        
        for i in range(0, len(unique_vocab), vocab_per_module):
            module_vocab = unique_vocab[i:i + vocab_per_module]
            module_num = i // vocab_per_module + 1
            
            module = {
                "id": module_num,
                "title": f"Module {module_num}: Từ vựng tháng {module_num}",
                "description": f"Học {len(module_vocab)} từ vựng mới",
                "vocabulary": module_vocab,
                "lessons": [
                    {
                        "id": 1,
                        "title": "Video bài giảng",
                        "type": "video",
                        "duration_min": 20,
                    },
                    {
                        "id": 2,
                        "title": "Flashcards luyện tập",
                        "type": "practice",
                        "duration_min": 15,
                    },
                    {
                        "id": 3,
                        "title": "Quiz kiểm tra",
                        "type": "quiz",
                        "questions": len(module_vocab),
                    },
                ]
            }
            modules.append(module)
        
        # Create course data
        course_data = {
            "meta": {
                "title": course_name.replace("_", " ").title(),
                "description": f"Khóa học từ nội dung TOPIK Daily - {len(unique_vocab)} từ vựng",
                "level": "Mixed",
                "created_at": datetime.now().isoformat(),
            },
            "modules": modules,
            "vocabulary_count": len(unique_vocab),
            "grammar_count": len(all_grammar),
            "quiz_count": len(all_quizzes),
        }
        
        # Save
        course_file = course_dir / "course.json"
        with open(course_file, "w", encoding="utf-8") as f:
            json.dump(course_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"✅ Generated course from {len(content_files)} content files")
        return str(course_dir)
    
    def export_to_udemy(self, course_dir: str) -> Dict:
        """Export course to Udemy-compatible format"""
        
        course_path = Path(course_dir)
        course_file = course_path / "course.json"
        
        if not course_file.exists():
            logging.error(f"❌ Course not found: {course_file}")
            return {}
        
        with open(course_file, "r", encoding="utf-8") as f:
            course = json.load(f)
        
        # Udemy format
        udemy_course = {
            "course_title": course["meta"]["title"],
            "course_subtitle": course["meta"]["description"][:120],
            "course_description": self._generate_udemy_description(course),
            "course_language": "Vietnamese",
            "course_level": course["meta"]["level"],
            "course_category": "Language Learning",
            "course_subcategory": "Korean",
            "sections": [],
        }
        
        for module in course.get("modules", []):
            section = {
                "title": module["title"],
                "lectures": [],
            }
            
            for lesson in module.get("lessons", []):
                lecture = {
                    "title": lesson["title"],
                    "type": "video" if lesson["type"] == "video" else "article",
                    "description": "",
                }
                section["lectures"].append(lecture)
            
            udemy_course["sections"].append(section)
        
        # Save Udemy format
        udemy_file = course_path / "udemy_export.json"
        with open(udemy_file, "w", encoding="utf-8") as f:
            json.dump(udemy_course, f, ensure_ascii=False, indent=2)
        
        logging.info(f"✅ Exported to Udemy format: {udemy_file}")
        return udemy_course
    
    def _generate_udemy_description(self, course: Dict) -> str:
        """Generate Udemy course description"""
        
        return f"""
🇰🇷 **{course['meta']['title']}**

{course['meta']['description']}

---

## 📚 Bạn sẽ học được gì?

✅ Nắm vững từ vựng TOPIK cần thiết
✅ Hiểu và sử dụng ngữ pháp nâng cao
✅ Luyện kỹ năng đọc, nghe, viết
✅ Chuẩn bị tốt cho kỳ thi TOPIK

---

## 🎯 Khóa học này dành cho ai?

- Người học tiếng Hàn từ cơ bản đến nâng cao
- Người chuẩn bị thi TOPIK
- Người muốn cải thiện tiếng Hàn hàng ngày

---

## 📋 Nội dung khóa học

- **{len(course.get('modules', []))}** modules
- **{course.get('vocabulary_count', 0)}** từ vựng
- **{course.get('quiz_count', 0)}** bài quiz

---

## 👨‍🏫 Về giảng viên

TOPIK Daily là nền tảng học tiếng Hàn miễn phí với nội dung cập nhật hàng ngày.

---

화이팅! 💪
"""


class QuizGenerator:
    """Generate quizzes for courses"""
    
    def generate_vocab_quiz(self, vocabulary: List[Dict], num_questions: int = 20) -> Dict:
        """Generate vocabulary quiz"""
        import random
        
        if len(vocabulary) < 4:
            return {}
        
        questions = []
        vocab_sample = random.sample(vocabulary, min(num_questions, len(vocabulary)))
        
        for vocab in vocab_sample:
            # Generate wrong options
            other_vocab = [v for v in vocabulary if v != vocab]
            wrong_options = random.sample(other_vocab, min(3, len(other_vocab)))
            
            question = {
                "type": "multiple_choice",
                "question": f"'{vocab.get('korean', '')}' có nghĩa là gì?",
                "options": [
                    vocab.get("meaning", ""),
                    *[v.get("meaning", "") for v in wrong_options]
                ],
                "correct_answer": 0,  # First option is correct
                "explanation": vocab.get("example_vi", ""),
            }
            
            # Shuffle options
            options = question["options"]
            correct = options[0]
            random.shuffle(options)
            question["correct_answer"] = options.index(correct)
            question["options"] = options
            
            questions.append(question)
        
        return {
            "title": "Quiz Từ Vựng",
            "type": "vocabulary",
            "questions": questions,
            "passing_score": 70,
        }
    
    def generate_grammar_quiz(self, grammar: List[Dict], num_questions: int = 15) -> Dict:
        """Generate grammar quiz"""
        import random
        
        if not grammar:
            return {}
        
        questions = []
        grammar_sample = random.sample(grammar, min(num_questions, len(grammar)))
        
        for g in grammar_sample:
            question = {
                "type": "fill_blank",
                "question": f"Điền ngữ pháp phù hợp: {g.get('example1_ko', '').replace(g.get('pattern', ''), '___')}",
                "correct_answer": g.get("pattern", ""),
                "hint": g.get("meaning", ""),
            }
            questions.append(question)
        
        return {
            "title": "Quiz Ngữ Pháp",
            "type": "grammar",
            "questions": questions,
            "passing_score": 60,
        }


# ==================== UTILITY FUNCTIONS ====================

def create_topik1_course() -> str:
    """Create TOPIK I course"""
    generator = CourseGenerator()
    return generator.generate_course_from_template(TOPIK_1_CURRICULUM, "topik_1_complete")


def create_topik2_course() -> str:
    """Create TOPIK II course"""
    generator = CourseGenerator()
    return generator.generate_course_from_template(TOPIK_2_CURRICULUM, "topik_2_mastery")


# ==================== MAIN ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test
    print("Creating TOPIK I course...")
    path1 = create_topik1_course()
    print(f"Created: {path1}")
    
    print("\nCreating TOPIK II course...")
    path2 = create_topik2_course()
    print(f"Created: {path2}")
    
    # Export to Udemy
    generator = CourseGenerator()
    generator.export_to_udemy(path1)
