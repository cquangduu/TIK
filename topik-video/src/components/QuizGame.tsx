import {
  AbsoluteFill,
  Audio,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  staticFile,
  Sequence,
} from "remotion";
import { Confetti } from "remotion-confetti";
import React, { useMemo } from "react";
import { QuizBackground } from "./AnimatedBackground";

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES — Extended for Azure TTS + YouTube Support
// ═══════════════════════════════════════════════════════════════════════════════

interface AudioSegmentTiming {
  path: string;
  duration: number;  // Duration in seconds
}

interface QuizAudioTiming {
  question?: AudioSegmentTiming;
  answer?: AudioSegmentTiming;
  opening?: AudioSegmentTiming;  // Opening ment audio
  closing?: AudioSegmentTiming;  // Closing ment audio
  silence_duration?: number;  // Thinking time in seconds (default 4s)
  total_duration?: number;
}

// Use imported QuizData from types.ts instead of local interface
// Local QuizData extended with additional local fields
interface LocalQuizData {
  target_word?: string;
  target_grammar?: string;
  opening_ment?: string;       // Korean greeting
  closing_ment?: string;       // Korean closing
  question_ko?: string;
  question_vi?: string;
  options_ko?: string[];
  options_vi?: string[];
  explanation_ko?: string;
  explanation_vi?: string;
  question?: string;
  options?: string[];
  correct_answer: string;
  explanation?: string;
  // NEW: Audio timing from Azure TTS
  audio_timing?: QuizAudioTiming;
  // NEW: SSML signal for long text (from Python)
  ssml_fast_mode?: boolean;
}

interface TikTokScript {
  video_1_news?: any;
  video_2_outline?: any;
  video_3_vocab_quiz?: LocalQuizData;
  video_4_grammar_quiz?: LocalQuizData;
  video_5_deep_dive?: any;
}

interface AudioPaths {
  video_1_news?: string;
  video_2_outline?: string;
  video_3_vocab_quiz?: string;
  video_4_grammar_quiz?: string;
  video_5_deep_dive?: string;
}

// Extended MyProps with new features
interface QuizGameProps {
  tiktok_script: TikTokScript;
  audio_paths: AudioPaths;
  audio_data?: {
    video_3_vocab_quiz?: {
      opening_audio?: { path: string; duration: number; text?: string };
      question_audio?: { path: string; duration: number };
      answer_audio?: { path: string; duration: number };
      closing_audio?: { path: string; duration: number; text?: string };
      silence_duration?: number;
      total_duration?: number;
    };
    video_4_grammar_quiz?: {
      opening_audio?: { path: string; duration: number; text?: string };
      question_audio?: { path: string; duration: number };
      answer_audio?: { path: string; duration: number };
      closing_audio?: { path: string; duration: number; text?: string };
      silence_duration?: number;
      total_duration?: number;
    };
  };
  video_bg?: string;
  video_bg_duration?: number;  // Duration of video background in seconds
  mode?: "vocab" | "grammar";
  // NEW: Platform-specific layout
  platform?: "tiktok" | "youtube";
  // NEW: Optional countdown music
  countdown_music?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// SAFE ZONE CONFIGURATIONS — Adaptive for TikTok vs YouTube
// ═══════════════════════════════════════════════════════════════════════════════

const SAFE_ZONES = {
  tiktok: {
    paddingTop: 180,
    paddingBottom: 420,   // Critical: Avoid TikTok UI elements
    paddingRight: 130,
    paddingLeft: 40,
  },
  youtube: {
    paddingTop: 120,
    paddingBottom: 150,   // YouTube has less UI overlap
    paddingRight: 80,
    paddingLeft: 80,
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// COLORS — High Contrast Gameshow Palette
// ═══════════════════════════════════════════════════════════════════════════════

const CLR = {
  bgTop: "#0a0e1a",
  bgBot: "#12182a",
  card: "rgba(255,255,255,0.08)",
  cardBorder: "rgba(255,255,255,0.15)",
  correct: "#4ade80",
  correctGlow: "rgba(74, 222, 128, 0.4)",
  wrong: "rgba(255,255,255,0.05)",
  accent: "#facc15",
  accentGlow: "rgba(250, 204, 21, 0.3)",
  korean: "#ffffff",
  vietnamese: "#ffc857",
  explanationBg: "rgba(0, 0, 0, 0.7)",
};

// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function getProgressColor(progress: number): string {
  if (progress > 0.6) return "#4ade80"; // Green
  if (progress > 0.3) return "#facc15"; // Yellow
  return "#ef4444"; // Red
}

/**
 * Calculate typewriter speed based on text length and SSML signal.
 * Longer text = faster typewriter to fit within audio duration.
 */
function getTypewriterSpeed(text: string, ssmlFastMode: boolean = false): number {
  const baseSpeed = ssmlFastMode ? 1.5 : 2; // chars per frame
  const length = text.length;
  
  if (length > 200) return baseSpeed * 2.5;  // Very long: super fast
  if (length > 100) return baseSpeed * 1.8;  // Long: faster
  if (length > 50) return baseSpeed * 1.3;   // Medium: slightly faster
  return baseSpeed;                           // Short: normal
}

/**
 * Typewriter text effect with adaptive speed.
 */
function useTypewriterText(
  text: string,
  startFrame: number,
  currentFrame: number,
  ssmlFastMode: boolean = false
): string {
  const speed = getTypewriterSpeed(text, ssmlFastMode);
  const elapsed = Math.max(0, currentFrame - startFrame);
  const charCount = Math.floor(elapsed * speed);
  return text.substring(0, Math.min(charCount, text.length));
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════════════════

export const QuizGame: React.FC<QuizGameProps> = (props) => {
  const {
    tiktok_script,
    audio_paths,
    audio_data,
    mode = "vocab",
    platform = "tiktok",
    countdown_music,
  } = props;

  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // ── Get Safe Zone based on platform ──────────────────────────────────────
  const SAFE_ZONE = SAFE_ZONES[platform];

  // ── Resolve Quiz Data ────────────────────────────────────────────────────
  const isGrammar = mode === "grammar";
  const quizData = isGrammar
    ? tiktok_script?.video_4_grammar_quiz
    : tiktok_script?.video_3_vocab_quiz;

  // ── Extract quiz content with fallbacks ──────────────────────────────────
  const questionKo = quizData?.question_ko || quizData?.question || "";
  const questionVi = quizData?.question_vi || "";
  const optionsKo = quizData?.options_ko || quizData?.options || [];
  const optionsVi = quizData?.options_vi || [];
  const correctAnswer = quizData?.correct_answer || "C";
  const explanationKo = quizData?.explanation_ko || quizData?.explanation || "";
  const explanationVi = quizData?.explanation_vi || "";
  const targetLabel = isGrammar ? quizData?.target_grammar : quizData?.target_word;
  const ssmlFastMode = quizData?.ssml_fast_mode || false;
  
  // ── Audio Timing from audio_data (NEW: from main.py TTS generation) ──────
  // audio_data contains the actual audio file paths and durations
  const audioDataForVideo = isGrammar
    ? audio_data?.video_4_grammar_quiz
    : audio_data?.video_3_vocab_quiz;
  
  // Opening/Closing ment: prefer quizData, fallback to audio_data.text
  const openingMent = quizData?.opening_ment || audioDataForVideo?.opening_audio?.text || "";
  const closingMent = quizData?.closing_ment || audioDataForVideo?.closing_audio?.text || "";

  // Map to expected structure
  const audioTiming = audioDataForVideo ? {
    opening: audioDataForVideo.opening_audio ? {
      path: audioDataForVideo.opening_audio.path,
      duration: audioDataForVideo.opening_audio.duration,
    } : undefined,
    question: audioDataForVideo.question_audio ? {
      path: audioDataForVideo.question_audio.path,
      duration: audioDataForVideo.question_audio.duration,
    } : undefined,
    answer: audioDataForVideo.answer_audio ? {
      path: audioDataForVideo.answer_audio.path,
      duration: audioDataForVideo.answer_audio.duration,
    } : undefined,
    closing: audioDataForVideo.closing_audio ? {
      path: audioDataForVideo.closing_audio.path,
      duration: audioDataForVideo.closing_audio.duration,
    } : undefined,
    silence_duration: audioDataForVideo.silence_duration || 4,
    total_duration: audioDataForVideo.total_duration,
  } : (quizData?.audio_timing || undefined);  // Fallback to legacy
  
  const hasSegmentedAudio = !!(audioTiming?.question && audioTiming?.answer);
  const hasOpeningAudio = !!(audioTiming?.opening?.path);
  const hasClosingAudio = !!(audioTiming?.closing?.path);

  // Calculate timing based on actual audio durations (including opening/closing)
  const timingConfig = useMemo(() => {
    if (hasSegmentedAudio && audioTiming) {
      const openingDuration = audioTiming.opening?.duration || 0;
      const questionDuration = audioTiming.question?.duration || 5;
      const silenceDuration = audioTiming.silence_duration || 4;
      const answerDuration = audioTiming.answer?.duration || 5;
      const closingDuration = audioTiming.closing?.duration || 0;

      // Warn if core durations are missing
      if (!audioTiming.question?.duration) {
        console.warn(`⚠️ QuizGame: Missing question duration, using fallback 5s`);
      }
      if (!audioTiming.answer?.duration) {
        console.warn(`⚠️ QuizGame: Missing answer duration, using fallback 5s`);
      }

      const openingFrames = Math.ceil(openingDuration * fps);
      const questionFrames = Math.ceil(questionDuration * fps);
      const silenceFrames = Math.ceil(silenceDuration * fps);
      const answerFrames = Math.ceil(answerDuration * fps);
      const closingFrames = Math.ceil(closingDuration * fps);

      // Timeline: opening → question → silence → answer → closing
      const openingEnd = openingFrames;
      const questionEnd = openingFrames + questionFrames;
      const thinkingStart = questionEnd;
      const thinkingEnd = questionEnd + silenceFrames;
      const revealStart = thinkingEnd;
      const answerEnd = revealStart + answerFrames;
      const closingStart = answerEnd;

      return {
        openingEnd,
        questionStart: openingEnd,
        questionEnd,
        thinkingStart,
        thinkingEnd,
        revealStart,
        answerEnd,
        closingStart,
        totalFrames: openingFrames + questionFrames + silenceFrames + answerFrames + closingFrames,
        silenceDuration,
        openingFrames,
        closingFrames,
      };
    }

    // Legacy fallback: Calculate from total duration
    const REVEAL_BUFFER = 60;  // 2s @ 30fps
    const SILENCE_FRAMES = 120; // 4s @ 30fps

    return {
      openingEnd: 0,
      questionStart: 0,
      questionEnd: durationInFrames - REVEAL_BUFFER - SILENCE_FRAMES,
      thinkingStart: durationInFrames - REVEAL_BUFFER - SILENCE_FRAMES,
      thinkingEnd: durationInFrames - REVEAL_BUFFER,
      revealStart: durationInFrames - REVEAL_BUFFER,
      answerEnd: durationInFrames,
      closingStart: durationInFrames,
      totalFrames: durationInFrames,
      silenceDuration: 4,
    };
  }, [hasSegmentedAudio, audioTiming, fps, durationInFrames]);

  // ── Phase Detection ──────────────────────────────────────────────────────
  const inThinkingPhase = frame >= timingConfig.thinkingStart && frame < timingConfig.revealStart;
  const inRevealPhase = frame >= timingConfig.revealStart;

  // ── Countdown Progress (1 → 0 during thinking phase) ─────────────────────
  const countdownProgress = interpolate(
    frame,
    [timingConfig.thinkingStart, timingConfig.revealStart],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const secondsLeft = Math.ceil(countdownProgress * timingConfig.silenceDuration);
  const isFinalCountdown = inThinkingPhase && countdownProgress < 0.5;
  const shakeIntensity = isFinalCountdown ? 4 : 2;

  // ── Global Fade Out ──────────────────────────────────────────────────────
  const fadeOutStart = durationInFrames - 18;
  const globalOpacity = interpolate(
    frame,
    [fadeOutStart, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Progress Bar Width ───────────────────────────────────────────────────
  const progressBarWidth = inThinkingPhase
    ? countdownProgress * 100
    : inRevealPhase
    ? 0
    : 100;

  // ── Reveal Spring Animation ──────────────────────────────────────────────
  const revealSpring = spring({
    frame: frame - timingConfig.revealStart,
    fps,
    config: { mass: 0.5, damping: 12, stiffness: 120 },
  });
  const revealProgress = frame < timingConfig.revealStart ? 0 : Math.min(revealSpring, 1);

  // ── Question Entrance Spring ─────────────────────────────────────────────
  const questionSpring = spring({
    frame,
    fps,
    config: { mass: 0.7, damping: 16, stiffness: 90 },
  });

  // ── Typewriter Text for Explanations (No-Audio Subtitles) ────────────────
  const explanationViTypewriter = useTypewriterText(
    explanationVi,
    timingConfig.revealStart,
    frame,
    ssmlFastMode
  );

  // ── Audio File Sources ───────────────────────────────────────────────────
  const legacyAudioPath = isGrammar
    ? audio_paths?.video_4_grammar_quiz
    : audio_paths?.video_3_vocab_quiz;

  // Opening/Closing Audio Sources
  const openingAudioSrc = hasOpeningAudio && audioTiming?.opening
    ? staticFile(audioTiming.opening.path.replace(/^\//, ""))
    : null;
  const closingAudioSrc = hasClosingAudio && audioTiming?.closing
    ? staticFile(audioTiming.closing.path.replace(/^\//, ""))
    : null;
  
  const questionAudioSrc = hasSegmentedAudio && audioTiming?.question
    ? staticFile(audioTiming.question.path.replace(/^\//, ""))
    : null;
  const answerAudioSrc = hasSegmentedAudio && audioTiming?.answer
    ? staticFile(audioTiming.answer.path.replace(/^\//, ""))
    : null;
  const legacyAudioSrc = legacyAudioPath
    ? staticFile(legacyAudioPath.replace(/^\//, ""))
    : null;
  const countdownMusicSrc = countdown_music
    ? staticFile(countdown_music.replace(/^\//, ""))
    : null;

  // ── Labels ───────────────────────────────────────────────────────────────
  const modeLabel = isGrammar ? "NGỮ PHÁP" : "TỪ VỰNG";
  const modeEmoji = isGrammar ? "📝" : "💡";

  // ── Opening/Closing Phase Detection ──────────────────────────────────────
  const inOpeningPhase = frame < timingConfig.openingEnd;
  const inClosingPhase = frame >= timingConfig.closingStart;

  // ═════════════════════════════════════════════════════════════════════════
  // RENDER
  // ═════════════════════════════════════════════════════════════════════════
  
  // Video background source
  const videoBgSrc = props.video_bg ? staticFile(props.video_bg.replace(/^\//, "")) : null;
  const videoBgDuration = props.video_bg_duration;

  return (
    <AbsoluteFill>
      {/* ══════════ Looping Video Background ══════════ */}
      <QuizBackground videoBgSrc={videoBgSrc} videoDurationSec={videoBgDuration} />
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: "rgba(8,10,20,0.85)",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Opening Ment Slide ══════════ */}
      {inOpeningPhase && openingMent && (
        <AbsoluteFill>
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: SAFE_ZONE.paddingLeft,
              background: "rgba(0,0,0,0.5)",
            }}
          >
            <div
              style={{
                background: CLR.card,
                border: `2px solid ${CLR.accent}`,
                borderRadius: 24,
                padding: "40px 50px",
                maxWidth: "90%",
              }}
            >
              <p
                style={{
                  fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
                  fontSize: platform === "youtube" ? 48 : 42,
                  fontWeight: 700,
                  color: "#fff",
                  margin: 0,
                  textAlign: "center",
                  lineHeight: 1.5,
                }}
              >
                {openingMent}
              </p>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ══════════ Decorative Elements ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: -80,
            right: -80,
            width: 200,
            height: 200,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${CLR.accentGlow} 0%, transparent 70%)`,
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -60,
            left: -60,
            width: 160,
            height: 160,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(100,160,255,0.1) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ MAIN QUIZ CONTENT (Hidden during opening/closing) ══════════ */}
      {!inOpeningPhase && !inClosingPhase && (
        <>
          {/* ══════════ Top Progress Bar ══════════ */}
          <AbsoluteFill>
            <div
              style={{
                position: "absolute",
                top: SAFE_ZONE.paddingTop - 20,
                left: SAFE_ZONE.paddingLeft,
                right: SAFE_ZONE.paddingRight,
                height: 5,
                background: "rgba(255, 255, 255, 0.1)",
                borderRadius: 3,
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progressBarWidth}%`,
                  background: inThinkingPhase
                    ? getProgressColor(countdownProgress)
                    : `linear-gradient(90deg, ${CLR.accent}, ${CLR.correct})`,
                  boxShadow: inThinkingPhase
                    ? `0 0 20px ${getProgressColor(countdownProgress)}`
                    : "none",
                  borderRadius: 3,
                  transition: "background 0.3s, width 0.1s linear",
                }}
              />
            </div>
          </AbsoluteFill>

          {/* ══════════ Main Content ══════════ */}
          <AbsoluteFill>
            <div
              style={{
                position: "absolute",
                top: SAFE_ZONE.paddingTop,
                left: SAFE_ZONE.paddingLeft,
                right: SAFE_ZONE.paddingRight,
                bottom: SAFE_ZONE.paddingBottom,
                display: "flex",
                flexDirection: "column",
                opacity: globalOpacity,
              }}
            >
          {/* ── Header Badge ── */}
          <div style={{ textAlign: "center", marginBottom: 16 }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 10,
                background: `${CLR.accent}18`,
                border: `2px solid ${CLR.accent}60`,
                borderRadius: 28,
                padding: "10px 22px",
              }}
            >
              <span style={{ fontSize: 20 }}>{modeEmoji}</span>
              <span
                style={{
                  fontFamily: "'Segoe UI', sans-serif",
                  fontSize: platform === "youtube" ? 18 : 15,
                  fontWeight: 700,
                  color: CLR.accent,
                  letterSpacing: 3,
                }}
              >
                {modeLabel}
              </span>
            </div>
          </div>

          {/* ── Question Card ── */}
          <div
            style={{
              background: CLR.card,
              border: `1.5px solid ${CLR.cardBorder}`,
              borderRadius: 20,
              padding: platform === "youtube" ? "28px 32px" : "24px 28px",
              marginBottom: 20,
              opacity: Math.min(questionSpring, 1),
              transform: `translateY(${interpolate(Math.min(questionSpring, 1), [0, 1], [30, 0])}px)`,
            }}
          >
            {/* Korean Question */}
            <p
              style={{
                fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
                fontSize: platform === "youtube" ? 54 : 48,
                fontWeight: 700,
                color: CLR.korean,
                margin: 0,
                lineHeight: 1.35,
                textAlign: "center",
                textShadow: "0 4px 20px rgba(0,0,0,0.5)",
              }}
            >
              {questionKo}
            </p>

            {/* Vietnamese Translation */}
            {questionVi && (
              <p
                style={{
                  fontFamily: "'Segoe UI', sans-serif",
                  fontSize: platform === "youtube" ? 30 : 26,
                  fontWeight: 400,
                  color: CLR.vietnamese,
                  margin: "16px 0 0",
                  lineHeight: 1.4,
                  textAlign: "center",
                }}
              >
                {questionVi}
              </p>
            )}

            {/* Target Word/Grammar */}
            {targetLabel && (
              <div style={{ textAlign: "center", marginTop: 14 }}>
                <span
                  style={{
                    display: "inline-block",
                    fontFamily: "'Noto Sans KR', sans-serif",
                    fontSize: platform === "youtube" ? 26 : 22,
                    fontWeight: 600,
                    color: CLR.accent,
                    background: `${CLR.accent}20`,
                    borderRadius: 12,
                    padding: "8px 20px",
                  }}
                >
                  {targetLabel}
                </span>
              </div>
            )}
          </div>

          {/* ══════════ Options Grid (2x2) ══════════ */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: platform === "youtube" ? 18 : 14,
              flex: 1,
              alignContent: "center",
            }}
          >
            {optionsKo.map((opt: string, idx: number) => {
              const letter = String.fromCharCode(65 + idx);
              const isCorrect = letter === correctAnswer;
              const viText = optionsVi[idx] || "";

              // Reveal Phase styling
              const cardBg = inRevealPhase
                ? isCorrect
                  ? `${CLR.correct}25`
                  : CLR.wrong
                : CLR.card;

              const cardBorder = inRevealPhase
                ? isCorrect
                  ? `2.5px solid ${CLR.correct}`
                  : "1px solid transparent"
                : `1px solid ${CLR.cardBorder}`;

              const textColor = inRevealPhase
                ? isCorrect
                  ? CLR.correct
                  : "rgba(255,255,255,0.25)"
                : "rgba(255,255,255,0.9)";

              // Staggered entrance
              const optSpring = spring({
                frame: frame - idx * 6,
                fps,
                config: { mass: 0.55, damping: 14, stiffness: 100 },
              });
              const optProgress = frame < idx * 6 ? 0 : Math.min(optSpring, 1);

              // Thinking Phase shake
              const shakeX = inThinkingPhase
                ? Math.sin(frame * 0.5 + idx * 2) * shakeIntensity
                : 0;
              const shakeY = inThinkingPhase
                ? Math.cos(frame * 0.4 + idx * 3) * (shakeIntensity * 0.6)
                : 0;

              // Reveal Phase pulse
              const correctScale =
                inRevealPhase && isCorrect
                  ? interpolate(
                      frame - timingConfig.revealStart,
                      [0, 8, 16, 24],
                      [1, 1.08, 1.03, 1],
                      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                    )
                  : 1;

              const glowShadow =
                inRevealPhase && isCorrect
                  ? `0 0 25px ${CLR.correctGlow}, 0 0 50px ${CLR.correctGlow}`
                  : "none";

              return (
                <div
                  key={letter}
                  style={{
                    background: cardBg,
                    border: cardBorder,
                    borderRadius: 18,
                    padding: platform === "youtube" ? "18px 20px" : "16px 18px",
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    opacity: optProgress * (inRevealPhase && !isCorrect ? 0.3 : 1),
                    transform: `
                      translateY(${interpolate(optProgress, [0, 1], [24, 0])}px)
                      translateX(${shakeX}px)
                      translateY(${shakeY}px)
                      scale(${correctScale})
                    `,
                    boxShadow: glowShadow,
                    transition: inRevealPhase
                      ? "background 0.3s, border 0.3s, box-shadow 0.3s"
                      : "none",
                  }}
                >
                  {/* Letter Badge */}
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "50%",
                      background:
                        inRevealPhase && isCorrect
                          ? CLR.correct
                          : "rgba(255,255,255,0.12)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: "'Segoe UI', sans-serif",
                        fontSize: 20,
                        fontWeight: 700,
                        color:
                          inRevealPhase && isCorrect
                            ? "#0a0e1a"
                            : "rgba(255,255,255,0.8)",
                      }}
                    >
                      {letter}
                    </span>
                  </div>

                  {/* Option Text */}
                  <div style={{ flex: 1 }}>
                    <span
                      style={{
                        fontFamily: "'Noto Sans KR', sans-serif",
                        fontSize: platform === "youtube" ? 28 : 24,
                        fontWeight: 600,
                        color: textColor,
                        lineHeight: 1.35,
                        display: "block",
                      }}
                    >
                      {opt.replace(/^[A-D]\.\s*/, "")}
                    </span>
                    {viText && (
                      <span
                        style={{
                          fontFamily: "'Segoe UI', sans-serif",
                          fontSize: platform === "youtube" ? 18 : 16,
                          color:
                            inRevealPhase && isCorrect
                              ? CLR.vietnamese
                              : "rgba(255,200,100,0.65)",
                          display: "block",
                          marginTop: 4,
                        }}
                      >
                        {viText.replace(/^[A-D]\.\s*/, "")}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* ══════════ Thinking Phase: Countdown Timer ══════════ */}
          {inThinkingPhase && (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                marginTop: 24,
              }}
            >
              <svg
                width={90}
                height={90}
                viewBox="0 0 90 90"
                style={{ overflow: "visible" }}
              >
                <circle
                  cx={45}
                  cy={45}
                  r={38}
                  fill="none"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth={6}
                />
                <circle
                  cx={45}
                  cy={45}
                  r={38}
                  fill="none"
                  stroke={getProgressColor(countdownProgress)}
                  strokeWidth={6}
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 38}`}
                  strokeDashoffset={`${2 * Math.PI * 38 * (1 - countdownProgress)}`}
                  transform="rotate(-90 45 45)"
                  style={{
                    filter: `drop-shadow(0 0 10px ${getProgressColor(countdownProgress)})`,
                    transition: "stroke 0.3s",
                  }}
                />
                <text
                  x={45}
                  y={45}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill="#fff"
                  fontSize={36}
                  fontWeight={700}
                  fontFamily="'Segoe UI', sans-serif"
                >
                  {secondsLeft}
                </text>
              </svg>

              <span
                style={{
                  fontFamily: "'Segoe UI', sans-serif",
                  fontSize: 16,
                  color: "rgba(255,255,255,0.6)",
                  marginTop: 12,
                  letterSpacing: 2,
                  textTransform: "uppercase",
                }}
              >
                🤔 생각해 보세요...
              </span>
            </div>
          )}
        </div>
      </AbsoluteFill>

          {/* ══════════ Reveal Phase: Answer + Explanation ══════════ */}
          {inRevealPhase && !inClosingPhase && (
        <AbsoluteFill>
          <div
            style={{
              position: "absolute",
              bottom: platform === "youtube" ? 180 : 450,
              left: SAFE_ZONE.paddingLeft,
              right: SAFE_ZONE.paddingRight,
              opacity: revealProgress * globalOpacity,
              transform: `translateY(${interpolate(revealProgress, [0, 1], [50, 0])}px)`,
            }}
          >
            {/* Correct Answer Banner */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 14,
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  width: 50,
                  height: 50,
                  borderRadius: "50%",
                  background: CLR.correct,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: `0 0 30px ${CLR.correctGlow}`,
                }}
              >
                <span style={{ color: "#0a0e1a", fontSize: 28, fontWeight: 800 }}>
                  ✓
                </span>
              </div>
              <span
                style={{
                  fontFamily: "'Noto Sans KR', sans-serif",
                  fontSize: platform === "youtube" ? 32 : 28,
                  fontWeight: 700,
                  color: CLR.correct,
                  letterSpacing: 2,
                }}
              >
                정답: {correctAnswer}
              </span>
            </div>

            {/* Explanation Card */}
            <div
              style={{
                background: CLR.explanationBg,
                borderRadius: 20,
                padding: platform === "youtube" ? 28 : (explanationKo.length > 100 ? 16 : 24),
                maxHeight: platform === "youtube" ? 350 : 280,
                overflow: "hidden",
              }}
            >
              {/* Korean Explanation */}
              <p
                style={{
                  fontFamily: "'Noto Sans KR', sans-serif",
                  fontSize: platform === "youtube" 
                    ? (explanationKo.length > 100 ? 28 : 34) 
                    : (explanationKo.length > 100 ? 24 : 30),
                  fontWeight: 500,
                  color: "#fff",
                  margin: 0,
                  lineHeight: explanationKo.length > 100 ? 1.35 : 1.45,
                  textAlign: "center",
                }}
              >
                {explanationKo}
              </p>

              {/* Vietnamese Explanation (No-Audio Subtitle with Typewriter) */}
              {explanationVi && (
                <p
                  style={{
                    fontFamily: "'Segoe UI', sans-serif",
                    fontSize: platform === "youtube" ? 28 : 24,
                    fontWeight: 400,
                    color: CLR.vietnamese,
                    margin: "16px 0 0",
                    lineHeight: 1.4,
                    textAlign: "center",
                    paddingTop: 16,
                    borderTop: "1px solid rgba(255,255,255,0.15)",
                    minHeight: "1.4em",
                  }}
                >
                  💡 {explanationViTypewriter}
                  {/* Blinking cursor during typewriter */}
                  {explanationViTypewriter.length < explanationVi.length && (
                    <span
                      style={{
                        opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
                        marginLeft: 2,
                      }}
                    >
                      |
                    </span>
                  )}
                </p>
              )}
            </div>
          </div>
        </AbsoluteFill>
      )}

          {/* ══════════ Confetti on Reveal ══════════ */}
          {inRevealPhase && !inClosingPhase && (
            <AbsoluteFill>
              <Confetti
                particleCount={100}
                startVelocity={45}
                spread={360}
                x={1080 / 2}
                y={1920 / 2}
                scalar={1.2}
                colors={["#4ade80", "#facc15", "#60a5fa", "#f472b6", "#ffffff"]}
                ticks={120}
              />
            </AbsoluteFill>
          )}
        </>
      )}

      {/* ══════════ Closing Ment Slide ══════════ */}
      {inClosingPhase && closingMent && (
        <AbsoluteFill>
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: SAFE_ZONE.paddingLeft,
              background: "rgba(0,0,0,0.5)",
            }}
          >
            <div
              style={{
                background: CLR.card,
                border: `2px solid ${CLR.correct}`,
                borderRadius: 24,
                padding: "40px 50px",
                maxWidth: "90%",
              }}
            >
              <p
                style={{
                  fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
                  fontSize: platform === "youtube" ? 48 : 42,
                  fontWeight: 700,
                  color: "#fff",
                  margin: 0,
                  textAlign: "center",
                  lineHeight: 1.5,
                }}
              >
                {closingMent}
              </p>
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ══════════ Multi-Track Audio ══════════ */}
      
      {/* Track 0: Opening Audio (plays first) */}
      {openingAudioSrc && (
        <Sequence from={0} durationInFrames={timingConfig.openingEnd}>
          <Audio src={openingAudioSrc} />
        </Sequence>
      )}

      {/* Track 1: Question Audio (plays after opening) */}
      {hasSegmentedAudio && questionAudioSrc && (
        <Sequence from={timingConfig.questionStart} durationInFrames={timingConfig.questionEnd - timingConfig.questionStart}>
          <Audio src={questionAudioSrc} />
        </Sequence>
      )}

      {/* Track 2: Countdown Music (plays during thinking phase) */}
      {countdownMusicSrc && (
        <Sequence
          from={timingConfig.thinkingStart}
          durationInFrames={timingConfig.revealStart - timingConfig.thinkingStart}
        >
          <Audio src={countdownMusicSrc} volume={0.4} />
        </Sequence>
      )}

      {/* Track 3: Answer Audio (plays during reveal phase) */}
      {hasSegmentedAudio && answerAudioSrc && (
        <Sequence
          from={timingConfig.revealStart}
          durationInFrames={timingConfig.answerEnd - timingConfig.revealStart}
        >
          <Audio src={answerAudioSrc} />
        </Sequence>
      )}

      {/* Track 4: Closing Audio (plays last) */}
      {closingAudioSrc && (
        <Sequence from={timingConfig.closingStart} durationInFrames={timingConfig.closingFrames || 0}>
          <Audio src={closingAudioSrc} />
        </Sequence>
      )}

      {/* Legacy: Single combined audio file */}
      {!hasSegmentedAudio && legacyAudioSrc && <Audio src={legacyAudioSrc} />}
    </AbsoluteFill>
  );
};

export default QuizGame;
