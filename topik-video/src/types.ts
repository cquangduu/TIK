// ─── Bilingual Segment (Korean Audio + Vietnamese Subtitle) ──────────────────
export interface BilingualSegment {
  ko: string;
  vi: string;
  audio_path?: string;   // Per-segment audio file
  duration?: number;     // Duration in seconds from Azure TTS
}

// ─── Audio Segment Timing (from Azure TTS) ───────────────────────────────────
export interface AudioSegmentTiming {
  path: string;
  duration: number;  // Duration in seconds
}

// ─── Audio Phase (Opening, Content, Closing) ─────────────────────────────────
export interface AudioPhase {
  audio_path: string;
  duration: number;
  text?: string;
}

// ─── Quiz Audio Timing (Opening + Question + Silence + Answer + Closing) ─────
export interface QuizAudioTiming {
  opening?: AudioSegmentTiming;
  question?: AudioSegmentTiming;
  answer?: AudioSegmentTiming;
  closing?: AudioSegmentTiming;
  silence_duration?: number;  // Thinking time in seconds (default 4s)
  total_duration?: number;
}

// ─── Video 1: News Healing ───────────────────────────────────────────────────
export interface Video1News {
  opening_ment?: string;            // NEW: Korean greeting
  audio_text?: string;              // Full Korean text for TTS (new format)
  closing_ment?: string;            // NEW: Korean closing
  opening?: AudioPhase;             // NEW: Opening audio timing
  segments?: BilingualSegment[];    // Subtitle pairs (ko/vi) with timing
  closing?: AudioPhase;             // NEW: Closing audio timing
  total_duration?: number;          // Total duration from all segments
  ssml_compressed?: boolean;        // NEW: Whether SSML rate was increased
  // Legacy fallback
  script_ko?: string;
  script_vi?: string;
}

// ─── Video 2: Writing Coach Part ─────────────────────────────────────────────
export interface WritingPart {
  role: "intro" | "body_1" | "body_2" | "body_3";
  label_vi?: string;               // e.g., "Mở Bài", "Thân Bài 1"
  ko: string;                      // Korean main point
  vi: string;                      // Vietnamese explanation
  audio_path?: string;             // NEW: Per-part audio
  duration?: number;               // NEW: Per-part duration
}

export interface Video2Outline {
  opening_ment?: string;           // NEW: Korean greeting
  audio_text?: string;             // Full Korean text for TTS (new format)
  closing_ment?: string;           // NEW: Korean closing
  opening?: AudioPhase;            // NEW: Opening audio timing
  parts?: WritingPart[];           // Structured parts with ko/vi
  closing?: AudioPhase;            // NEW: Closing audio timing
  total_duration?: number;         // NEW: Total duration
  ssml_compressed?: boolean;       // NEW: Whether SSML rate was increased
  // Legacy fallback
  intro?: string;
  body_1?: string;
  body_2?: string;
  body_3?: string;
}

// ─── Quiz data (shared shape for vocab & grammar) ──────────────────────────
export interface QuizData {
  target_word?: string;            // video_3 only
  target_grammar?: string;         // video_4 only
  opening_ment?: string;           // NEW: Korean greeting
  closing_ment?: string;           // NEW: Korean closing
  // New format: separated Korean/Vietnamese
  question_ko?: string;            // Korean question for TTS
  question_vi?: string;            // Vietnamese translation (subtitle)
  options_ko?: string[];           // Korean options for TTS
  options_vi?: string[];           // Vietnamese options (subtitle)
  explanation_ko?: string;         // Korean explanation for TTS
  explanation_vi?: string;         // Vietnamese explanation (subtitle)
  // NEW: Audio timing from Azure TTS (segment-based)
  audio_timing?: QuizAudioTiming;
  // NEW: SSML signal for long text (triggers faster typewriter)
  ssml_fast_mode?: boolean;
  ssml_compressed?: boolean;       // NEW: Whether SSML rate was increased
  // Legacy fallback
  question?: string;
  options?: string[];              // always 4 elements: ["A. …", "B. …", "C. …", "D. …"]
  correct_answer: string;          // single letter: "A" | "B" | "C" | "D"
  explanation?: string;
}

// ─── Video 5: Deep Dive (YouTube Long-form) ──────────────────────────────────
export interface DeepDiveSegment {
  ko: string;
  vi: string;
  audio_path?: string;
  duration?: number;
}

export interface DeepDiveParagraph {
  label: string;
  ko: string;
  vi: string;
  analysis_ko: string;
  analysis_vi: string;
  audio_path?: string;
  duration?: number;
}

export interface DeepDiveVocabItem {
  word: string;
  explanation_ko: string;
  meaning_vi: string;
  example_ko: string;
  example_vi: string;
  audio_path?: string;
  duration?: number;
}

export interface DeepDiveGrammarItem {
  point: string;
  explanation_ko: string;
  meaning_vi: string;
  example_ko: string;
  example_vi: string;
  audio_path?: string;
  duration?: number;
}

export interface Video5DeepDive {
  meta: {
    title_ko: string;
    title_vi: string;
    description_vi?: string;
    hashtags?: string[];
  };
  opening: {
    hook_ko: string;
    hook_vi: string;
    intro_ko: string;
    intro_vi: string;
    duration_sec?: number;
    audio_path?: string;
  };
  news: {
    transition_ko: string;
    transition_vi: string;
    content_ko: string;
    content_vi: string;
    analysis_ko: string;
    analysis_vi: string;
    duration_sec?: number;
    audio_path?: string;
  };
  transition: {
    bridge_ko: string;
    bridge_vi: string;
    duration_sec?: number;
    audio_path?: string;
  };
  exam: {
    intro_ko: string;
    intro_vi: string;
    question_ko: string;
    question_vi: string;
    tips_ko: string;
    tips_vi: string;
    duration_sec?: number;
    audio_path?: string;
  };
  essay: {
    intro_ko: string;
    intro_vi: string;
    paragraphs: DeepDiveParagraph[];
    duration_sec?: number;
    audio_path?: string;
  };
  vocab: {
    intro_ko: string;
    intro_vi: string;
    items: DeepDiveVocabItem[];
    grammar_items: DeepDiveGrammarItem[];
    duration_sec?: number;
    audio_path?: string;
  };
  closing: {
    summary_ko: string;
    summary_vi: string;
    cta_ko: string;
    cta_vi: string;
    outro_ko: string;
    outro_vi: string;
    duration_sec?: number;
    audio_path?: string;
  };
  // Aggregated segments from main.py Phase 5 (with audio timing)
  segments?: DeepDiveSegmentData[];
  total_duration?: number;
  timestamps?: DeepDiveTimestamp[];
}

// ─── Deep Dive Segment (from Phase 5 audio build) ───────────────────────────
export interface DeepDiveSegmentData {
  section: string;        // "opening", "news", "exam", "essay_서론 (Mở bài)", etc.
  ko: string;             // Korean text
  vi: string;             // Vietnamese subtitle
  audio_path?: string;    // e.g., "/assets/deep_0.mp3"
  duration?: number;      // Duration in seconds from mutagen
}

// ─── Deep Dive Timestamp (for YouTube chapters) ─────────────────────────────
export interface DeepDiveTimestamp {
  section: string;
  start_sec: number;
  label: string;
}

// ─── Full tiktok_script block (mirrors Python JSON) ─────────────────────────
export interface TikTokScript {
  video_1_news?: Video1News;
  video_2_outline?: Video2Outline;
  video_3_vocab_quiz?: QuizData;
  video_4_grammar_quiz?: QuizData;
  video_5_deep_dive?: Video5DeepDive;  // YouTube Deep Dive (Phase 4)
}

// ─── Audio paths (relative, served by Remotion from /public) ─────────────────
export interface AudioPaths {
  video_1_news?: string;
  video_2_outline?: string;
  video_3_vocab_quiz?: string;
  video_4_grammar_quiz?: string;
  video_5_deep_dive?: string;      // YouTube Deep Dive audio
}

// ─── Audio Data (detailed timing from TTS generation) ────────────────────────
export interface AudioData {
  video_1_news?: {
    opening?: AudioPhase;
    segments?: BilingualSegment[];
    closing?: AudioPhase;
    total_duration?: number;
    combined_audio?: string;
    ssml_compressed?: boolean;
  };
  video_2_outline?: {
    opening?: AudioPhase;
    parts?: {
      role: string;
      label_vi?: string;
      ko: string;
      vi: string;
      audio_path?: string;
      duration?: number;
    }[];
    closing?: AudioPhase;
    total_duration?: number;
  };
  video_3_vocab_quiz?: {
    opening_audio?: AudioSegmentTiming & { text?: string };
    question_audio?: AudioSegmentTiming;
    answer_audio?: AudioSegmentTiming;
    closing_audio?: AudioSegmentTiming & { text?: string };
    silence_duration?: number;
    total_duration?: number;
    combined_audio?: string;
    audio_timing?: QuizAudioTiming;  // Fallback legacy structure
  };
  video_4_grammar_quiz?: {
    opening_audio?: AudioSegmentTiming & { text?: string };
    question_audio?: AudioSegmentTiming;
    answer_audio?: AudioSegmentTiming;
    closing_audio?: AudioSegmentTiming & { text?: string };
    silence_duration?: number;
    total_duration?: number;
    combined_audio?: string;
    audio_timing?: QuizAudioTiming;  // Fallback legacy structure
  };
  video_5_deep_dive?: {
    opening?: AudioPhase;
    segments?: BilingualSegment[];
    closing?: AudioPhase;
    total_duration?: number;
  };
}

// ─── Root props — passed via --props JSON to every composition ──────────────
export interface MyProps {
  tiktok_script: TikTokScript;
  audio_paths: AudioPaths;
  audio_data?: AudioData;          // NEW: Detailed audio timing from TTS
  video_bg?: string;               // e.g. "/assets/background.mp4"
  video_bg_duration?: number;      // NEW: Actual video background duration in seconds
  mode?: "vocab" | "grammar";      // only used by QuizGame
  platform?: "tiktok" | "youtube"; // NEW: Adaptive layout
  countdown_music?: string;        // NEW: Optional countdown music for quiz
}
