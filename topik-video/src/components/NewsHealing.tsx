import React from "react";
import {
  AbsoluteFill,
  Audio,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  staticFile,
  Series,
  OffthreadVideo,
  Loop,
} from "remotion";
import { MyProps, Video1News } from "../types";

// ─── TikTok Safe Zone Constants ─────────────────────────────────────────────
const SAFE_ZONE = {
  paddingTop: 160,
  paddingBottom: 400,
  paddingRight: 130,
  paddingLeft: 40,
};

// ─── Color palette — Pastel Healing vibes ───────────────────────────────────
const CLR = {
  bgGradient1: "#0d1117",
  bgGradient2: "#161b22",
  korean: "#ffffff",
  koreanHighlight: "#a5d6ff",
  vietnamese: "#ffc857",
  subtitleBg: "rgba(0, 0, 0, 0.6)",
  accent: "#ff6b6b",
  accentSoft: "rgba(255, 107, 107, 0.15)",
};

// ─── Segment interface matching new audio structure ─────────────────────────
interface AudioSegment {
  ko: string;
  vi: string;
  audio_path?: string;
  duration?: number;  // Duration in seconds from audio generation
}

// ─── Helper: Extract segments from script ───────────────────────────────────
function getSegments(script: Video1News): AudioSegment[] {
  if (script?.segments && Array.isArray(script.segments)) {
    return script.segments;
  }
  // Legacy fallback
  if (script?.script_ko || script?.audio_text) {
    const koText = script.audio_text || script.script_ko || "";
    const viText = script.script_vi || "";
    const koSentences = koText.split(/(?<=[.?!])\s+/).filter(Boolean);
    const viSentences = viText.split(/(?<=[.?!])\s+/).filter(Boolean);
    return koSentences.map((ko: string, i: number) => ({
      ko: ko.trim(),
      vi: viSentences[i]?.trim() || "",
    }));
  }
  return [];
}

// Note: Total duration is calculated dynamically from Series sequences

// ─── ANIMATED GRADIENT BACKGROUND ──────────────────────────────────────────
// Professional alternative to video - never loops, always stable
// Uses smooth color transitions for a calming "healing" aesthetic

interface AnimatedGradientBackgroundProps {
  variant?: "dark" | "aurora" | "sunset" | "ocean";
}

const AnimatedGradientBackground: React.FC<AnimatedGradientBackgroundProps> = ({
  variant = "dark",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  // Slow, smooth animation - one full cycle over ~30 seconds
  const progress = (frame / fps) * 0.03; // Very slow rotation
  
  // Color palettes for different moods
  const palettes = {
    dark: {
      colors: ["#0d1117", "#161b22", "#1a1f2e", "#0f1419", "#12171f"],
      accent: "rgba(165, 214, 255, 0.08)",
    },
    aurora: {
      colors: ["#0d1b2a", "#1b263b", "#2d3a4a", "#1a2634", "#0f1922"],
      accent: "rgba(100, 255, 218, 0.1)",
    },
    sunset: {
      colors: ["#1a1423", "#2d1f3d", "#1f1a2e", "#291f35", "#1e1528"],
      accent: "rgba(255, 107, 107, 0.1)",
    },
    ocean: {
      colors: ["#0a192f", "#112240", "#1d3557", "#14213d", "#0d1b2a"],
      accent: "rgba(100, 181, 246, 0.1)",
    },
  };
  
  const palette = palettes[variant];
  
  // Animated gradient positions
  const angle1 = 45 + Math.sin(progress) * 15;
  const angle2 = 135 + Math.cos(progress * 0.7) * 20;
  
  // Floating orbs positions (bokeh effect)
  const orb1X = 20 + Math.sin(progress * 0.5) * 15;
  const orb1Y = 30 + Math.cos(progress * 0.4) * 20;
  const orb2X = 70 + Math.cos(progress * 0.6) * 20;
  const orb2Y = 60 + Math.sin(progress * 0.5) * 15;
  const orb3X = 40 + Math.sin(progress * 0.8) * 25;
  const orb3Y = 80 + Math.cos(progress * 0.7) * 10;
  
  return (
    <AbsoluteFill>
      {/* Base gradient layer */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `
            linear-gradient(${angle1}deg, ${palette.colors[0]} 0%, ${palette.colors[1]} 50%, ${palette.colors[2]} 100%)
          `,
        }}
      />
      
      {/* Secondary gradient overlay */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `
            radial-gradient(ellipse at ${orb1X}% ${orb1Y}%, ${palette.accent} 0%, transparent 50%),
            radial-gradient(ellipse at ${orb2X}% ${orb2Y}%, ${palette.accent} 0%, transparent 40%),
            radial-gradient(ellipse at ${orb3X}% ${orb3Y}%, ${palette.accent} 0%, transparent 45%)
          `,
          opacity: 0.8,
        }}
      />
      
      {/* Subtle noise texture overlay for depth */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `
            linear-gradient(${angle2}deg, transparent 40%, rgba(255,255,255,0.02) 50%, transparent 60%)
          `,
          opacity: 0.5,
        }}
      />
      
      {/* Floating particles/bokeh */}
      {[...Array(6)].map((_, i) => {
        const size = 100 + i * 50;
        const x = (15 + i * 15 + Math.sin(progress * (0.3 + i * 0.1)) * 10);
        const y = (10 + i * 15 + Math.cos(progress * (0.4 + i * 0.1)) * 15);
        const opacity = 0.03 + (i % 3) * 0.02;
        
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${palette.accent.replace('0.1', String(opacity))} 0%, transparent 70%)`,
              filter: "blur(40px)",
              transform: "translate(-50%, -50%)",
            }}
          />
        );
      })}
      
      {/* Vignette effect */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `
            radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.4) 100%)
          `,
        }}
      />
    </AbsoluteFill>
  );
};

// ─── Video Background Duration (fallback if not provided in props) ──────────
const DEFAULT_VIDEO_BG_DURATION_SEC = 28.12; // Fallback duration in seconds

// ─── Looping Background Component ───────────────────────────────────────
interface LoopingBackgroundProps {
  videoBgSrc: string | null;
  videoDurationSec?: number;       // Actual video duration from props
  useAnimatedGradient?: boolean;
  gradientVariant?: "dark" | "aurora" | "sunset" | "ocean";
}

const LoopingBackground: React.FC<LoopingBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
  useAnimatedGradient = false, // Default to video background
  gradientVariant = "dark",
}) => {
  const { fps, durationInFrames } = useVideoConfig();
  
  // Use provided duration or fallback to default
  const actualDuration = videoDurationSec || DEFAULT_VIDEO_BG_DURATION_SEC;
  
  // Calculate video duration in frames
  const videoDurationFrames = Math.ceil(actualDuration * fps);
  
  // Calculate how many loops we need
  const loopCount = Math.ceil(durationInFrames / videoDurationFrames);
  
  // If no video source or explicitly want gradient, use animated gradient
  if (!videoBgSrc || useAnimatedGradient) {
    return <AnimatedGradientBackground variant={gradientVariant} />;
  }
  
  // Use Loop component for reliable video looping
  return (
    <Loop durationInFrames={videoDurationFrames} times={loopCount}>
      <OffthreadVideo
        src={videoBgSrc}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
        muted
      />
    </Loop>
  );
};

// ─── Opening/Closing Slide Component ────────────────────────────────────────
interface OpeningClosingSlideProps {
  text: string;
  type: "opening" | "closing";
  videoBgSrc: string | null;
}

const OpeningClosingSlide: React.FC<OpeningClosingSlideProps> = ({
  text,
  type,
  videoBgSrc,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  
  const fadeOut = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  
  const opacity = fadeIn * fadeOut;

  const scale = interpolate(frame, [0, 20], [0.95, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const isOpening = type === "opening";
  const emoji = isOpening ? "👋" : "💫";

  return (
    <AbsoluteFill>
      {/* Dark Overlay */}
      <AbsoluteFill>
        <div style={{ width: "100%", height: "100%", background: "rgba(8, 12, 22, 0.8)" }} />
      </AbsoluteFill>

      {/* Content */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop,
            bottom: SAFE_ZONE.paddingBottom,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            opacity,
            transform: `scale(${scale})`,
          }}
        >
          <span style={{ fontSize: 60, marginBottom: 20 }}>{emoji}</span>
          <div
            style={{
              background: CLR.accentSoft,
              border: `2px solid ${CLR.accent}`,
              borderRadius: 20,
              padding: "24px 40px",
              backdropFilter: "blur(10px)",
            }}
          >
            <p
              style={{
                fontFamily: "'Noto Sans KR', sans-serif",
                fontSize: 42,
                fontWeight: 700,
                color: CLR.korean,
                textAlign: "center",
                lineHeight: 1.5,
                margin: 0,
              }}
            >
              {text}
            </p>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ─── Individual Segment Component ───────────────────────────────────────────
interface SegmentProps {
  segment: AudioSegment;
  segmentIndex: number;
  totalSegments: number;
  videoBgSrc: string | null;
}

const SegmentSlide: React.FC<SegmentProps> = ({
  segment,
  segmentIndex,
  totalSegments,
  videoBgSrc,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // ── FadeIn / FadeOut for this segment ────────────────────────────────────
  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  
  const opacity = fadeIn * fadeOut;

  // ── Text entrance animation ──────────────────────────────────────────────
  const textY = interpolate(frame, [0, 20], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Vietnamese delayed fade-in ───────────────────────────────────────────
  const viOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Progress indicator ───────────────────────────────────────────────────
  const segmentProgress = (segmentIndex + frame / durationInFrames) / totalSegments;

  // ── Pulsing dot ──────────────────────────────────────────────────────────
  const pulseDot = Math.sin(frame / 15) * 0.3 + 0.7;

  // ── Dynamic font size based on text length (improved for long text) ──────
  const koLength = segment.ko.length;
  const koreanFontSize = koLength > 80 ? 32 : koLength > 50 ? 36 : 46;
  const koLineHeight = koLength > 80 ? 1.4 : 1.5;
  
  // Vietnamese font size
  const viLength = segment.vi.length;
  const viFontSize = viLength > 120 ? 24 : viLength > 80 ? 26 : 30;
  const viLineHeight = viLength > 120 ? 1.3 : 1.4;

  // ── Audio for this segment ───────────────────────────────────────────────
  const segmentAudioSrc = segment.audio_path
    ? staticFile(segment.audio_path.replace(/^\//, ""))
    : null;

  return (
    <AbsoluteFill>
      {/* Background is handled at root level (NewsHealing) - no duplicate here */}

      {/* ══════════ Dark Overlay ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: "rgba(8, 12, 22, 0.75)",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Vignette Effect ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background:
              "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.5) 100%)",
            pointerEvents: "none",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Film Grain ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
            backgroundRepeat: "repeat",
            opacity: 0.04,
            mixBlendMode: "overlay",
            pointerEvents: "none",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Progress Bar ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop - 10,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            height: 4,
            background: "rgba(255, 255, 255, 0.1)",
            borderRadius: 2,
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${segmentProgress * 100}%`,
              background: `linear-gradient(90deg, ${CLR.accent}, ${CLR.koreanHighlight})`,
              borderRadius: 2,
              boxShadow: `0 0 20px ${CLR.accent}`,
            }}
          />
        </div>
      </AbsoluteFill>

      {/* ══════════ Top Badge ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            justifyContent: "center",
            opacity: opacity,
          }}
        >
          <div
            style={{
              background: CLR.accentSoft,
              border: `1.5px solid ${CLR.accent}`,
              borderRadius: 28,
              padding: "10px 24px",
              display: "flex",
              alignItems: "center",
              gap: 10,
              backdropFilter: "blur(10px)",
            }}
          >
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: CLR.accent,
                opacity: pulseDot,
                boxShadow: `0 0 8px ${CLR.accent}`,
              }}
            />
            <span
              style={{
                fontFamily: "'Noto Sans KR', 'Segoe UI', sans-serif",
                fontSize: 14,
                fontWeight: 700,
                color: "#fff",
                letterSpacing: 3,
                textTransform: "uppercase",
              }}
            >
              DAILY KOREAN
            </span>
          </div>
        </div>
      </AbsoluteFill>

      {/* ══════════ Segment Indicator Dots ══════════ */}
      {totalSegments > 1 && (
        <AbsoluteFill>
          <div
            style={{
              position: "absolute",
              top: SAFE_ZONE.paddingTop + 60,
              left: SAFE_ZONE.paddingLeft,
              right: SAFE_ZONE.paddingRight,
              display: "flex",
              justifyContent: "center",
              gap: 8,
              opacity: opacity * 0.8,
            }}
          >
            {Array.from({ length: totalSegments }).map((_, idx) => (
              <div
                key={idx}
                style={{
                  width: idx === segmentIndex ? 24 : 8,
                  height: 8,
                  borderRadius: 4,
                  background:
                    idx === segmentIndex
                      ? CLR.accent
                      : idx < segmentIndex
                      ? "rgba(255,255,255,0.6)"
                      : "rgba(255,255,255,0.2)",
                }}
              />
            ))}
          </div>
        </AbsoluteFill>
      )}

      {/* ══════════ Korean Text (Center) ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop + 100,
            bottom: SAFE_ZONE.paddingBottom + 100,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            opacity: opacity,
            transform: `translateY(${textY}px)`,
          }}
        >
          <p
            style={{
              fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
              fontSize: koreanFontSize,
              fontWeight: 700,
              color: CLR.korean,
              textAlign: "center",
              lineHeight: koLineHeight,
              margin: 0,
              textShadow: "0 2px 20px rgba(0,0,0,0.5)",
            }}
          >
            {segment.ko}
          </p>
        </div>
      </AbsoluteFill>

      {/* ══════════ Vietnamese Subtitle (Bottom) ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            bottom: SAFE_ZONE.paddingBottom + 20,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            justifyContent: "center",
            opacity: viOpacity * fadeOut,
          }}
        >
          <div
            style={{
              background: CLR.subtitleBg,
              borderRadius: 16,
              padding: viLength > 100 ? "12px 18px" : "16px 24px",
              maxWidth: "100%",
              maxHeight: 100,
              overflow: "hidden",
            }}
          >
            <p
              style={{
                fontFamily: "'Segoe UI', 'Arial', sans-serif",
                fontSize: viFontSize,
                fontWeight: 500,
                color: CLR.vietnamese,
                textAlign: "center",
                lineHeight: viLineHeight,
                margin: 0,
              }}
            >
              {segment.vi}
            </p>
          </div>
        </div>
      </AbsoluteFill>

      {/* ══════════ Decorative Lines ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop - 20,
            left: SAFE_ZONE.paddingLeft,
            width: 40,
            height: 2,
            background: `linear-gradient(90deg, ${CLR.accent}, transparent)`,
            opacity: opacity * 0.6,
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: SAFE_ZONE.paddingBottom - 20,
            right: SAFE_ZONE.paddingRight,
            width: 40,
            height: 2,
            background: `linear-gradient(90deg, transparent, ${CLR.koreanHighlight})`,
            opacity: opacity * 0.6,
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Segment Audio ══════════ */}
      {segmentAudioSrc && <Audio src={segmentAudioSrc} />}
    </AbsoluteFill>
  );
};

// ─── Main Component using Series ────────────────────────────────────────────
export const NewsHealing: React.FC<MyProps> = (props) => {
  const { tiktok_script, audio_paths, audio_data, video_bg, video_bg_duration } = props;
  const { fps } = useVideoConfig();
  
  // Video background source from props
  const videoBgSrc = video_bg ? staticFile(video_bg.replace(/^\//, "")) : null;
  
  const script = tiktok_script?.video_1_news ?? {} as Video1News;
  
  // Ưu tiên lấy audio data từ audio_data (có timing chính xác)
  // Fallback về tiktok_script nếu không có
  const audioInfo = audio_data?.video_1_news;
  
  // Opening: ưu tiên audio_data, fallback về script
  const opening = audioInfo?.opening || script?.opening;
  const openingText = opening?.text || script?.opening_ment || "안녕하세요! 오늘의 한국 사회 이슈, 함께 들어볼까요?";
  
  // Segments: ưu tiên audio_data (có duration chính xác), fallback về script
  const segments = audioInfo?.segments || getSegments(script);
  
  // Closing: ưu tiên audio_data, fallback về script  
  const closing = audioInfo?.closing || script?.closing;
  const closingText = closing?.text || script?.closing_ment || "다음 영상에서 또 만나요!";

  // Check if we have new audio structure with timing
  const hasNewStructure = (opening?.audio_path && opening?.duration) || 
                          segments.some((s) => s.audio_path && s.duration);

  if (!hasNewStructure) {
    // Legacy mode: use combined audio with character-based timing
    const audioSrc = audio_paths?.video_1_news
      ? staticFile(audio_paths.video_1_news.replace(/^\//, ""))
      : null;

    return (
      <AbsoluteFill>
        {/* Background: Use video if available, fallback to animated gradient */}
        <LoopingBackground 
          videoBgSrc={videoBgSrc} 
          videoDurationSec={video_bg_duration}
        />
        <LegacyNewsHealing
          segments={segments}
          videoBgSrc={videoBgSrc}
          audioSrc={audioSrc}
        />
      </AbsoluteFill>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NEW: Series-based rendering with PERFECT audio sync
  // Audio order: opening_ment → content segments → closing_ment
  // Background: Use video if available, fallback to animated gradient
  // ═══════════════════════════════════════════════════════════════════════════
  return (
    <AbsoluteFill>
      {/* Background: Use video if available, fallback to animated gradient */}
      <LoopingBackground 
        videoBgSrc={videoBgSrc} 
        videoDurationSec={video_bg_duration}
      />
      
      {/* Content Series: Opening → Segments → Closing */}
      <Series>
        {/* Opening Ment - LUÔN HIỂN THỊ NẾU CÓ */}
        {opening?.audio_path && opening.duration && opening.duration > 0 && (
          <Series.Sequence durationInFrames={Math.ceil(opening.duration * fps)}>
            <OpeningClosingSlide
              text={openingText}
              type="opening"
              videoBgSrc={videoBgSrc}
            />
            <Audio src={staticFile(opening.audio_path.replace(/^\//, ""))} />
          </Series.Sequence>
        )}

        {/* Content Segments - AUDIO KHỚP VỚI NỘI DUNG */}
        {segments.map((segment, idx) => {
          // Duration from audio data - warn if missing
          const segmentDuration = segment.duration;
          if (!segmentDuration || segmentDuration <= 0) {
            console.warn(`⚠️ NewsHealing Segment ${idx}: Missing duration, using fallback 3s`);
          }
          const durationFrames = Math.ceil((segmentDuration || 3) * fps);

          return (
            <Series.Sequence key={`seg-${idx}`} durationInFrames={durationFrames}>
              <SegmentSlide
                segment={segment}
                segmentIndex={idx}
                totalSegments={segments.length}
                videoBgSrc={videoBgSrc}
              />
            </Series.Sequence>
          );
        })}

        {/* Closing Ment - LUÔN HIỂN THỊ NẾU CÓ */}
        {closing?.audio_path && closing.duration && closing.duration > 0 && (
          <Series.Sequence durationInFrames={Math.ceil(closing.duration * fps)}>
            <OpeningClosingSlide
              text={closingText}
              type="closing"
              videoBgSrc={videoBgSrc}
            />
            <Audio src={staticFile(closing.audio_path.replace(/^\//, ""))} />
          </Series.Sequence>
        )}
      </Series>
    </AbsoluteFill>
  );
};

// ─── Legacy Component (fallback for old data format) ────────────────────────
interface LegacyProps {
  segments: AudioSegment[];
  videoBgSrc: string | null;
  audioSrc: string | null;
}

const LegacyNewsHealing: React.FC<LegacyProps> = ({
  segments,
  videoBgSrc,
  audioSrc,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Character-based timing (legacy)
  const totalChars = segments.reduce((sum, s) => sum + s.ko.length, 0);
  let currentIdx = 0;
  let charsSoFar = 0;
  const charProgress = (frame / durationInFrames) * totalChars;

  for (let i = 0; i < segments.length; i++) {
    charsSoFar += segments[i].ko.length;
    if (charProgress < charsSoFar) {
      currentIdx = i;
      break;
    }
    currentIdx = i;
  }

  const currentSegment = segments[currentIdx] || { ko: "", vi: "" };
  const koreanFontSize = currentSegment.ko.length > 50 ? 36 : 46;

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - fps, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const pulseDot = Math.sin(frame / 15) * 0.3 + 0.7;
  const overallProgress = frame / durationInFrames;

  return (
    <AbsoluteFill>
      {/* Background is handled at caller level - no duplicate here */}

      {/* Overlay */}
      <AbsoluteFill>
        <div style={{ width: "100%", height: "100%", background: "rgba(8,12,22,0.75)" }} />
      </AbsoluteFill>

      {/* Progress Bar */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop - 10,
          left: SAFE_ZONE.paddingLeft,
          right: SAFE_ZONE.paddingRight,
          height: 4,
          background: "rgba(255,255,255,0.1)",
          borderRadius: 2,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${overallProgress * 100}%`,
            background: `linear-gradient(90deg, ${CLR.accent}, ${CLR.koreanHighlight})`,
            borderRadius: 2,
          }}
        />
      </div>

      {/* Badge */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop,
          left: SAFE_ZONE.paddingLeft,
          right: SAFE_ZONE.paddingRight,
          display: "flex",
          justifyContent: "center",
          opacity: fadeOut,
        }}
      >
        <div
          style={{
            background: CLR.accentSoft,
            border: `1.5px solid ${CLR.accent}`,
            borderRadius: 28,
            padding: "10px 24px",
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              background: CLR.accent,
              opacity: pulseDot,
            }}
          />
          <span style={{ fontSize: 14, fontWeight: 700, color: "#fff", letterSpacing: 3 }}>
            DAILY KOREAN
          </span>
        </div>
      </div>

      {/* Segment Dots */}
      {segments.length > 1 && (
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop + 60,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            justifyContent: "center",
            gap: 8,
            opacity: fadeOut * 0.8,
          }}
        >
          {segments.map((_, idx) => (
            <div
              key={idx}
              style={{
                width: idx === currentIdx ? 24 : 8,
                height: 8,
                borderRadius: 4,
                background: idx === currentIdx ? CLR.accent : "rgba(255,255,255,0.3)",
              }}
            />
          ))}
        </div>
      )}

      {/* Korean Text */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop + 100,
          bottom: SAFE_ZONE.paddingBottom + 100,
          left: SAFE_ZONE.paddingLeft,
          right: SAFE_ZONE.paddingRight,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: fadeOut,
        }}
      >
        <p
          style={{
            fontFamily: "'Noto Sans KR', sans-serif",
            fontSize: koreanFontSize,
            fontWeight: 700,
            color: CLR.korean,
            textAlign: "center",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          {currentSegment.ko}
        </p>
      </div>

      {/* Vietnamese Subtitle */}
      <div
        style={{
          position: "absolute",
          bottom: SAFE_ZONE.paddingBottom + 20,
          left: SAFE_ZONE.paddingLeft,
          right: SAFE_ZONE.paddingRight,
          display: "flex",
          justifyContent: "center",
          opacity: fadeOut,
        }}
      >
        <div
          style={{
            background: CLR.subtitleBg,
            borderRadius: 16,
            padding: "16px 24px",
          }}
        >
          <p
            style={{
              fontFamily: "'Segoe UI', sans-serif",
              fontSize: 30,
              fontWeight: 500,
              color: CLR.vietnamese,
              textAlign: "center",
              margin: 0,
            }}
          >
            {currentSegment.vi}
          </p>
        </div>
      </div>

      {/* Audio */}
      {audioSrc && <Audio src={audioSrc} />}
    </AbsoluteFill>
  );
};
