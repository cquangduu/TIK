import "./index.css";
import { Composition, getInputProps } from "remotion";
import { NewsHealing } from "./components/NewsHealing";
import { WritingCoach } from "./components/WritingCoach";
import { QuizGame } from "./components/QuizGame";
import { DeepDive } from "./components/DeepDive";
import type { MyProps } from "./types";

// ─── Constants ───────────────────────────────────────────────────────────────
const FPS = 30;
const MAX_TIKTOK_DURATION_SEC = 59;  // TikTok max 60s, we use 59s for safety
const DEFAULT_TIKTOK_DURATION_SEC = 55;  // Default if no audio data
const DEFAULT_YOUTUBE_DURATION_SEC = 600;  // 10 minutes for YouTube

// Default props for development/preview
const defaultProps: MyProps = {
  tiktok_script: {
    video_1_news: { script_ko: "샘플 뉴스", script_vi: "Tin mẫu" },
    video_2_outline: { intro: "서론", body_1: "본론 1", body_2: "본론 2", body_3: "결론" },
    video_3_vocab_quiz: { question: "질문?", options: ["A", "B", "C", "D"], correct_answer: "C", explanation: "설명" },
    video_4_grammar_quiz: { question: "문법?", options: ["A", "B", "C", "D"], correct_answer: "B", explanation: "설명" },
  },
  audio_paths: {
    video_1_news: "/assets/v1_news.mp3",
    video_2_outline: "/assets/v2_outline.mp3",
    video_3_vocab_quiz: "/assets/v3_vocab_quiz.mp3",
    video_4_grammar_quiz: "/assets/v4_grammar_quiz.mp3",
  },
  video_bg: "/assets/background.mp4",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const AnyComposition = Composition as any;

/**
 * Calculate duration in frames based on audio data.
 * For TikTok shorts: uses actual audio duration (capped at 59s).
 * For YouTube: uses actual audio duration or default 10 minutes.
 */
function calculateDurationFrames(
  audioDuration: number | undefined,
  maxDuration: number,
  defaultDuration: number
): number {
  if (!audioDuration || audioDuration <= 0) {
    console.warn(`⚠️ No audio duration found, using default ${defaultDuration}s`);
    return Math.ceil(defaultDuration * FPS);
  }
  
  // Clamp to max duration and add 2 second buffer for fade-out + UI elements
  const BUFFER_SECONDS = 2;
  const clampedDuration = Math.min(audioDuration + BUFFER_SECONDS, maxDuration);
  return Math.ceil(clampedDuration * FPS);
}

export const RemotionRoot: React.FC = () => {
  // Get props from CLI (--props flag) or use defaults
  const inputProps = getInputProps() as Partial<MyProps>;
  const props: MyProps = { ...defaultProps, ...inputProps };

  // ─── Extract audio durations from audio_data ───────────────────────────────
  const audioData = props.audio_data;
  
  // Video 1: News - total_duration from audio_data
  const v1Duration = audioData?.video_1_news?.total_duration;
  const v1Frames = calculateDurationFrames(v1Duration, MAX_TIKTOK_DURATION_SEC, DEFAULT_TIKTOK_DURATION_SEC);
  
  // Video 2: Writing Coach - total_duration from audio_data
  const v2Duration = audioData?.video_2_outline?.total_duration;
  const v2Frames = calculateDurationFrames(v2Duration, MAX_TIKTOK_DURATION_SEC, DEFAULT_TIKTOK_DURATION_SEC);
  
  // Video 3: Vocab Quiz - total_duration from audio_data (flat structure)
  const v3Duration = audioData?.video_3_vocab_quiz?.total_duration 
    || (audioData?.video_3_vocab_quiz as any)?.audio_timing?.total_duration;
  const v3Frames = calculateDurationFrames(v3Duration, MAX_TIKTOK_DURATION_SEC, DEFAULT_TIKTOK_DURATION_SEC);
  
  // Video 4: Grammar Quiz - total_duration from audio_data (flat structure)
  const v4Duration = audioData?.video_4_grammar_quiz?.total_duration
    || (audioData?.video_4_grammar_quiz as any)?.audio_timing?.total_duration;
  const v4Frames = calculateDurationFrames(v4Duration, MAX_TIKTOK_DURATION_SEC, DEFAULT_TIKTOK_DURATION_SEC);
  
  // Video 5: YouTube Deep Dive - total_duration from audio_data
  const v5Duration = audioData?.video_5_deep_dive?.total_duration;
  const v5Frames = calculateDurationFrames(v5Duration, 1800, DEFAULT_YOUTUBE_DURATION_SEC);  // Max 30 min for YouTube

  return (
    <>
      {/* ═══════════════════ Video 1: News Healing ═══════════════════ */}
      <AnyComposition
        id="TikTok-NewsHealing"
        component={NewsHealing}
        durationInFrames={v1Frames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={props}
      />

      {/* ═══════════════════ Video 2: Writing Coach ═══════════════════ */}
      <AnyComposition
        id="TikTok-WritingCoach"
        component={WritingCoach}
        durationInFrames={v2Frames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={props}
      />

      {/* ═══════════════════ Video 3: Vocabulary Quiz ═══════════════════ */}
      <AnyComposition
        id="TikTok-VocabQuiz"
        component={QuizGame}
        durationInFrames={v3Frames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ ...props, mode: "vocab" }}
      />

      {/* ═══════════════════ Video 4: Grammar Quiz ═══════════════════ */}
      <AnyComposition
        id="TikTok-GrammarQuiz"
        component={QuizGame}
        durationInFrames={v4Frames}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ ...props, mode: "grammar" }}
      />

      {/* ═══════════════════ Video 5: Deep Dive (YouTube 16:9) ═══════════════════ */}
      <AnyComposition
        id="YouTube-DeepDive"
        component={DeepDive}
        durationInFrames={v5Frames}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{ ...props, platform: "youtube" }}
      />
    </>
  );
};
