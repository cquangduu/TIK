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
import type { MyProps, DeepDiveSegmentData } from "../types";
import { DeepDiveBackground } from "./AnimatedBackground";

// ─── Video Background Duration (fallback if not provided in props) ────────────
const DEFAULT_VIDEO_BG_DURATION_SEC = 28.12;

// ─── YouTube 16:9 Safe Zone Constants ─────────────────────────────────
const SAFE_ZONE = {
  paddingTop: 60,          // Less padding for YouTube
  paddingBottom: 80,       // Space for progress bar
  paddingHorizontal: 80,   // Wider margins for 16:9
};

// ─── Color Palette — Deep Dive Academic Theme ───────────────────────────────
const CLR = {
  bgGradient1: "#0f0f23",
  bgGradient2: "#1a1a2e",
  korean: "#ffffff",
  koreanHighlight: "#64b5f6",
  vietnamese: "#ffd54f",
  sectionBg: "rgba(0, 0, 0, 0.7)",
  accent: "#7c4dff",
  accentSoft: "rgba(124, 77, 255, 0.2)",
  examBg: "rgba(255, 87, 34, 0.15)",
  examAccent: "#ff5722",
  essayBg: "rgba(76, 175, 80, 0.15)",
  essayAccent: "#4caf50",
  vocabBg: "rgba(33, 150, 243, 0.15)",
  vocabAccent: "#2196f3",
};

// ─── Section Labels ─────────────────────────────────────────────────────────
const SECTION_LABELS: Record<string, { icon: string; title: string }> = {
  opening: { icon: "🎬", title: "Opening" },
  news: { icon: "📰", title: "News" },
  transition: { icon: "🔗", title: "Transition" },
  exam: { icon: "📝", title: "TOPIK 54" },
  essay: { icon: "✍️", title: "Essay" },
  essay_intro: { icon: "✍️", title: "Essay Intro" },
  vocab: { icon: "📚", title: "Vocabulary" },
  vocab_intro: { icon: "📚", title: "Vocab Intro" },
  closing: { icon: "🎯", title: "Closing" },
};

// ─── Helper: Get section base (e.g., "essay_서론" → "essay") ────────────────
function getSectionBase(section: string): string {
  if (section.startsWith("essay")) return "essay";
  if (section.startsWith("vocab")) return "vocab";
  return section;
}

// ─── Individual Segment Slide Component ─────────────────────────────────────
interface SegmentSlideProps {
  segment: DeepDiveSegmentData;
  segmentIndex: number;
  totalSegments: number;
  title: string;
}

const SegmentSlide: React.FC<SegmentSlideProps> = ({
  segment,
  segmentIndex,
  totalSegments,
  title,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // ── Animation timing ─────────────────────────────────────────────────────
  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = fadeIn * fadeOut;

  // ── Text entrance ────────────────────────────────────────────────────────
  const textY = interpolate(frame, [0, 25], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Vietnamese delayed fade ──────────────────────────────────────────────
  const viOpacity = interpolate(frame, [25, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Progress ─────────────────────────────────────────────────────────────
  const segmentProgress = (segmentIndex + frame / durationInFrames) / totalSegments;

  // ── Section-specific styling (handle prefixes like "essay_서론") ─────────
  const sectionBase = getSectionBase(segment.section);
  const sectionInfo = SECTION_LABELS[segment.section] || SECTION_LABELS[sectionBase] || { icon: "📌", title: "Content" };
  const isExam = sectionBase === "exam";
  const isEssay = sectionBase === "essay";
  const isVocab = sectionBase === "vocab";

  const accentColor = isExam ? CLR.examAccent : isEssay ? CLR.essayAccent : isVocab ? CLR.vocabAccent : CLR.accent;
  const bgTint = isExam ? CLR.examBg : isEssay ? CLR.essayBg : isVocab ? CLR.vocabBg : CLR.accentSoft;

  // ── Dynamic font sizing (improved for very long text) ─────────────────────
  const koLength = segment.ko.length;
  const koreanFontSize = koLength > 500 ? 22 : koLength > 400 ? 24 : koLength > 300 ? 26 : koLength > 150 ? 32 : 38;
  const viLength = segment.vi.length;
  const viFontSize = viLength > 300 ? 18 : viLength > 200 ? 20 : viLength > 100 ? 24 : 28;
  
  // Adjust line height for very long text
  const koLineHeight = koLength > 400 ? 1.4 : 1.6;
  const viLineHeight = viLength > 200 ? 1.3 : 1.5;

  // ── Audio ────────────────────────────────────────────────────────────────
  const audioSrc = segment.audio_path
    ? staticFile(segment.audio_path.replace(/^\//, ""))
    : null;

  return (
    <AbsoluteFill>
      {/* ══════════ Section Tint Overlay ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: bgTint,
            opacity: 0.5,
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Progress Bar (Top) ══════════ */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: SAFE_ZONE.paddingHorizontal,
          right: SAFE_ZONE.paddingHorizontal,
          height: 4,
          background: "rgba(255, 255, 255, 0.15)",
          borderRadius: 2,
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${segmentProgress * 100}%`,
            background: `linear-gradient(90deg, ${accentColor}, ${CLR.koreanHighlight})`,
            borderRadius: 2,
            boxShadow: `0 0 15px ${accentColor}`,
          }}
        />
      </div>

      {/* ══════════ Title Badge (Top Left) ══════════ */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop,
          left: SAFE_ZONE.paddingHorizontal,
          display: "flex",
          alignItems: "center",
          gap: 12,
          opacity: opacity,
        }}
      >
        <div
          style={{
            background: bgTint,
            border: `2px solid ${accentColor}`,
            borderRadius: 12,
            padding: "8px 16px",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <span style={{ fontSize: 24 }}>{sectionInfo.icon}</span>
          <span
            style={{
              fontFamily: "'Noto Sans KR', sans-serif",
              fontSize: 16,
              fontWeight: 700,
              color: "#fff",
              letterSpacing: 1,
            }}
          >
            {sectionInfo.title}
          </span>
        </div>
      </div>

      {/* ══════════ Segment Counter (Top Right) ══════════ */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop,
          right: SAFE_ZONE.paddingHorizontal,
          opacity: opacity * 0.7,
        }}
      >
        <span
          style={{
            fontFamily: "'Roboto Mono', monospace",
            fontSize: 14,
            color: "rgba(255,255,255,0.6)",
          }}
        >
          {segmentIndex + 1} / {totalSegments}
        </span>
      </div>

      {/* ══════════ Main Content Area ══════════ */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop + 80,
          bottom: SAFE_ZONE.paddingBottom + 150,
          left: SAFE_ZONE.paddingHorizontal,
          right: SAFE_ZONE.paddingHorizontal,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          opacity: opacity,
          transform: `translateY(${textY}px)`,
        }}
      >
        {/* Korean Text */}
        <div
          style={{
            background: CLR.sectionBg,
            borderRadius: 20,
            padding: koLength > 400 ? "20px 30px" : "30px 40px",
            maxWidth: "95%",
            maxHeight: "70%",
            overflow: "hidden",
            backdropFilter: "blur(10px)",
            border: `1px solid rgba(255,255,255,0.1)`,
          }}
        >
          <p
            style={{
              fontFamily: "'Noto Sans KR', sans-serif",
              fontSize: koreanFontSize,
              fontWeight: 600,
              color: CLR.korean,
              textAlign: "center",
              lineHeight: koLineHeight,
              margin: 0,
              whiteSpace: "pre-line",
            }}
          >
            {segment.ko}
          </p>
        </div>
      </div>

      {/* ══════════ Vietnamese Subtitle (Bottom) ══════════ */}
      <div
        style={{
          position: "absolute",
          bottom: SAFE_ZONE.paddingBottom,
          left: SAFE_ZONE.paddingHorizontal,
          right: SAFE_ZONE.paddingHorizontal,
          display: "flex",
          justifyContent: "center",
          opacity: opacity * viOpacity,
        }}
      >
        <div
          style={{
            background: "rgba(0, 0, 0, 0.75)",
            borderRadius: 16,
            padding: viLength > 200 ? "12px 20px" : "20px 30px",
            maxWidth: "90%",
            maxHeight: 120,
            overflow: "hidden",
            border: `1px solid ${CLR.vietnamese}33`,
          }}
        >
          <p
            style={{
              fontFamily: "'Segoe UI', sans-serif",
              fontSize: viFontSize,
              fontWeight: 500,
              color: CLR.vietnamese,
              textAlign: "center",
              lineHeight: viLineHeight,
              margin: 0,
              whiteSpace: "pre-line",
            }}
          >
            {segment.vi}
          </p>
        </div>
      </div>

      {/* ══════════ Segment Audio ══════════ */}
      {audioSrc && <Audio src={audioSrc} />}
    </AbsoluteFill>
  );
};

// ─── YouTube Video Background Component ─────────────────────────────────────
interface YouTubeBackgroundProps {
  videoBgSrc: string | null;
  videoDurationSec?: number;    // Actual video duration from props
  useAnimatedGradient?: boolean;
}

const YouTubeBackground: React.FC<YouTubeBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
  useAnimatedGradient = false,
}) => {
  const { fps, durationInFrames } = useVideoConfig();
  
  // Use provided duration or fallback to default
  const actualDuration = videoDurationSec || DEFAULT_VIDEO_BG_DURATION_SEC;
  const videoDurationFrames = Math.ceil(actualDuration * fps);
  const loopCount = Math.ceil(durationInFrames / videoDurationFrames);
  
  if (!videoBgSrc || useAnimatedGradient) {
    return <DeepDiveBackground />;
  }
  
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

// ─── Main DeepDive Component (YouTube 16:9) ─────────────────────────────────
export const DeepDive: React.FC<MyProps> = (props) => {
  const { tiktok_script, video_bg, video_bg_duration } = props;
  const { fps } = useVideoConfig();

  // Video background source
  const videoBgSrc = video_bg ? staticFile(video_bg.replace(/^\//, "")) : null;
  
  const deepDive = tiktok_script?.video_5_deep_dive;
  
  // ═══════════════════════════════════════════════════════════════════════════
  // Read segments directly from data (populated by main.py Phase 5)
  // segments array has: { section, ko, vi, audio_path, duration }
  // ═══════════════════════════════════════════════════════════════════════════
  const segments = deepDive?.segments || [];

  // Get title from meta
  const title = deepDive?.meta?.title_ko || "DAILY KOREAN | 데일리 코리안";

  if (segments.length === 0) {
    // Fallback: Show placeholder
    return (
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: `linear-gradient(180deg, ${CLR.bgGradient1}, ${CLR.bgGradient2})`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 20,
          }}
        >
          <p style={{ color: "#fff", fontSize: 32 }}>DAILY KOREAN</p>
          <p style={{ color: "#888", fontSize: 20 }}>No segments found. Run main.py Phase 5 to build audio.</p>
        </div>
      </AbsoluteFill>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // YouTube 16:9 Layout with Video Background
  // ═══════════════════════════════════════════════════════════════════════════
  
  return (
    <AbsoluteFill>
      {/* ══════════ Video Background (Root Level) ══════════ */}
      <YouTubeBackground 
        videoBgSrc={videoBgSrc} 
        videoDurationSec={video_bg_duration}
        useAnimatedGradient={!videoBgSrc} 
      />
      
      {/* Dark overlay for readability */}
      <div style={{ 
        position: "absolute",
        inset: 0,
        background: "rgba(10, 10, 30, 0.65)" 
      }} />

      {/* ══════════ Content Segments ══════════ */}
      <Series>
        {segments.map((segment, idx) => {
          // Duration from mutagen (accurate MP3 measurement)
          // Warn if duration is missing
          if (!segment.duration || segment.duration <= 0) {
            console.warn(`⚠️ DeepDive Segment ${idx}: Missing duration, using fallback 10s`);
          }
          const durationFrames = Math.ceil((segment.duration || 10) * fps);

          return (
            <Series.Sequence key={idx} durationInFrames={durationFrames}>
              <SegmentSlide
                segment={segment}
                segmentIndex={idx}
                totalSegments={segments.length}
                title={title}
              />
            </Series.Sequence>
          );
        })}
      </Series>
    </AbsoluteFill>
  );
};
