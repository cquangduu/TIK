import React from "react";
import {
  AbsoluteFill,
  Audio,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  staticFile,
  Series,
} from "remotion";
import { MyProps, AudioPhase } from "../types";
import { WritingCoachBackground } from "./AnimatedBackground";

// ─── Section metadata with accent colors ─────────────────────────────────────
const SECTIONS = [
  {
    key: "intro",
    role: "intro",
    label: "Mở Bài",
    korean: "서론",
    accent: "#6ecfff",
    emoji: "📝",
  },
  {
    key: "body_1",
    role: "body_1",
    label: "Thân Bài 1",
    korean: "본론 ①",
    accent: "#7ec8a0",
    emoji: "💡",
  },
  {
    key: "body_2",
    role: "body_2",
    label: "Thân Bài 2",
    korean: "본론 ②",
    accent: "#c9a6f5",
    emoji: "🔍",
  },
  {
    key: "conclusion",
    role: "conclusion",
    label: "Kết Bài",
    korean: "결론",
    accent: "#f5c96e",
    emoji: "🎯",
  },
] as const;

// ─── TikTok Safe Zone ────────────────────────────────────────────────────────
const SAFE_ZONE = {
  paddingTop: 180,
  paddingBottom: 420,
  paddingRight: 130,
  paddingLeft: 40,
};

// ─── Colors for flashcard design ─────────────────────────────────────────────
const CARD_COLORS = {
  bg: "#ffffff",
  shadow: "0 25px 60px rgba(0,0,0,0.4), 0 10px 20px rgba(0,0,0,0.25)",
  header: "#2563eb",
  body: "#1f2937",
  translation: "#4b5563",
};

// ─── Spring config ───────────────────────────────────────────────────────────
const SPRING_CFG = { mass: 0.6, damping: 14, stiffness: 100 };

// ─── Part interface matching new audio structure ─────────────────────────────
interface PartData {
  role: string;
  label_vi?: string;
  ko: string;
  vi: string;
  audio_path?: string;
  duration?: number;
}

// ─── Helper: Get section metadata by role ────────────────────────────────────
function getSectionMeta(role: string, isLastPart: boolean = false) {
  // If this is the last part, treat it as conclusion regardless of role name
  if (isLastPart && (role === "body_3" || role === "body_4" || role === "conclusion" || role === "outro")) {
    return SECTIONS.find((s) => s.role === "conclusion") || SECTIONS[3];
  }
  // Map body_3 or later to body_2 styling if not the last part
  if (role === "body_3" || role === "body_4") {
    return SECTIONS.find((s) => s.role === "body_2") || SECTIONS[2];
  }
  return SECTIONS.find((s) => s.role === role) || SECTIONS[0];
}

// ─── Helper: Extract parts from outline ──────────────────────────────────────
function getParts(outline: any): PartData[] {
  if (outline?.parts && Array.isArray(outline.parts)) {
    return outline.parts;
  }
  // Legacy fallback
  const legacyRoles = ["intro", "body_1", "body_2", "conclusion"];
  return legacyRoles
    .map((role) => ({
      role,
      ko: outline?.[role] || "",
      vi: "",
    }))
    .filter((p) => p.ko);
}

// ─── Individual Part Card Component ──────────────────────────────────────────
interface PartCardProps {
  part: PartData;
  partIndex: number;
  totalParts: number;
}

const PartCard: React.FC<PartCardProps> = ({
  part,
  partIndex,
  totalParts,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Check if this is the last part to show "Kết Bài" instead of fallback
  const isLastPart = partIndex === totalParts - 1;
  const section = getSectionMeta(part.role, isLastPart);

  // ── Card entrance animation ──────────────────────────────────────────────
  const cardSpring = spring({
    frame,
    fps,
    config: SPRING_CFG,
  });
  const cardProgress = Math.min(cardSpring, 1);
  const translateY = interpolate(cardProgress, [0, 1], [50, 0]);
  const scale = interpolate(cardProgress, [0, 1], [0.94, 1]);

  // ── FadeOut at end of segment ────────────────────────────────────────────
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 8, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Typewriter for Vietnamese (1 char per 2 frames) ──────────────────────
  const viCharsToShow = Math.floor(frame / 2);
  const viText = part.vi ? part.vi.substring(0, viCharsToShow) : "";
  const viComplete = part.vi && viCharsToShow >= part.vi.length;


  // ── Audio for this part ──────────────────────────────────────────────────
  const partAudioSrc = part.audio_path
    ? staticFile(part.audio_path.replace(/^\//, ""))
    : null;

  return (
    <AbsoluteFill>
      {/* Background is handled at root level - no video/gradient here */}

      {/* ══════════ Progress Indicator ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            display: "flex",
            gap: 10,
            opacity: fadeOut,
          }}
        >
          {SECTIONS.slice(0, totalParts).map((sec, idx) => (
            <div
              key={sec.key}
              style={{
                flex: 1,
                height: 6,
                borderRadius: 3,
                background:
                  idx < partIndex
                    ? sec.accent
                    : idx === partIndex
                    ? `linear-gradient(90deg, ${sec.accent} ${(frame / durationInFrames) * 100}%, rgba(255,255,255,0.2) ${(frame / durationInFrames) * 100}%)`
                    : "rgba(255,255,255,0.2)",
                boxShadow: idx <= partIndex ? `0 0 10px ${sec.accent}` : "none",
              }}
            />
          ))}
        </div>
      </AbsoluteFill>

      {/* ══════════ Flashcard Container ══════════ */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop + 40,
            left: "7.5%",
            width: "85%",
            bottom: SAFE_ZONE.paddingBottom,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: cardProgress * fadeOut,
            transform: `translateY(${translateY}px) scale(${scale})`,
          }}
        >
          {/* ═══════════ FLASHCARD ═══════════ */}
          <div
            style={{
              width: "100%",
              background: CARD_COLORS.bg,
              borderRadius: 28,
              padding: "36px 32px",
              boxShadow: CARD_COLORS.shadow,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Accent stripe at top */}
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 0,
                height: 6,
                background: section.accent,
              }}
            />

            {/* ─── HEADER: Role/Label ─── */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                marginBottom: 20,
                marginTop: 4,
              }}
            >
              {/* Icon circle */}
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: "50%",
                  background: `${section.accent}20`,
                  border: `3px solid ${section.accent}`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  flexShrink: 0,
                }}
              >
                <span style={{ fontSize: 24 }}>{section.emoji}</span>
              </div>

              {/* Label */}
              <div>
                <span
                  style={{
                    fontFamily: "'Segoe UI', sans-serif",
                    fontSize: 38,
                    fontWeight: 700,
                    color: CARD_COLORS.header,
                    display: "block",
                    lineHeight: 1.1,
                  }}
                >
                  {section.label}
                </span>
                <span
                  style={{
                    fontFamily: "'Noto Sans KR', sans-serif",
                    fontSize: 20,
                    color: "#9ca3af",
                    fontWeight: 500,
                  }}
                >
                  {section.korean}
                </span>
              </div>
            </div>

            {/* ─── BODY: Korean Text ─── */}
            <p
              style={{
                fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
                fontSize: part.ko.length > 60 ? 32 : 36,
                fontWeight: 500,
                color: CARD_COLORS.body,
                margin: 0,
                lineHeight: 1.6,
                marginBottom: part.vi ? 20 : 0,
              }}
            >
              {part.ko || "—"}
            </p>

            {/* ─── FOOTER: Vietnamese (Typewriter) ─── */}
            {part.vi && (
              <div
                style={{
                  paddingTop: 16,
                  borderTop: "2px solid #e5e7eb",
                }}
              >
                <p
                  style={{
                    fontFamily: "'Segoe UI', sans-serif",
                    fontSize: 28,
                    fontWeight: 400,
                    color: CARD_COLORS.translation,
                    margin: 0,
                    lineHeight: 1.5,
                    fontStyle: "italic",
                    minHeight: 42,
                  }}
                >
                  💡 {viText}
                  {!viComplete && (
                    <span
                      style={{
                        opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
                        color: CARD_COLORS.header,
                      }}
                    >
                      |
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>
        </div>
      </AbsoluteFill>

      {/* ══════════ Part Audio ══════════ */}
      {partAudioSrc && <Audio src={partAudioSrc} />}
    </AbsoluteFill>
  );
};

// ─── Main Component using Series ────────────────────────────────────────────
export const WritingCoach: React.FC<MyProps> = (props) => {
  const { tiktok_script, audio_paths, audio_data, video_bg, video_bg_duration } = props;
  const { fps } = useVideoConfig();

  const videoBgSrc = video_bg ? staticFile(video_bg.replace(/^\//, "")) : null;
  const outline = tiktok_script?.video_2_outline ?? {};
  
  // Get parts from tiktok_script (already has audio_path + duration)
  const parts = getParts(outline);

  // Extract opening and closing data
  // Priority: audio_data > tiktok_script
  const openingMent = outline?.opening_ment || "";
  const closingMent = outline?.closing_ment || "";
  
  // Opening/Closing from audio_data (has audio_path & duration)
  const audioDataOutline = audio_data?.video_2_outline;
  const opening: AudioPhase | undefined = audioDataOutline?.opening || outline?.opening;
  const closing: AudioPhase | undefined = audioDataOutline?.closing || outline?.closing;

  // Check if parts have per-part audio data
  const hasPartAudio = parts.some((p) => p.audio_path && p.duration);

  if (!hasPartAudio) {
    // Legacy mode: use combined audio with character-based timing
    const audioSrc = audio_paths?.video_2_outline
      ? staticFile(audio_paths.video_2_outline.replace(/^\//, ""))
      : null;

    return (
      <AbsoluteFill>
        <LegacyWritingCoach
          parts={parts}
          videoBgSrc={videoBgSrc}
          videoDurationSec={video_bg_duration}
          audioSrc={audioSrc}
        />
      </AbsoluteFill>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NEW: Series-based rendering with PERFECT audio sync
  // Opening → Parts → Closing sequence
  // ═══════════════════════════════════════════════════════════════════════════
  
  return (
    <AbsoluteFill>
      {/* ══════════ Looping Video Background ══════════ */}
      <WritingCoachBackground videoBgSrc={videoBgSrc} videoDurationSec={video_bg_duration} />

      {/* Dark overlay */}
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: "rgba(15, 23, 42, 0.70)",
          }}
        />
      </AbsoluteFill>

      {/* ══════════ Content Series: Opening → Parts → Closing ══════════ */}
      <Series>
        {/* Opening Ment */}
        {opening?.audio_path && opening.duration && (
          <Series.Sequence durationInFrames={Math.ceil(opening.duration * fps)}>
            <OpeningClosingSlide
              text={openingMent}
              type="opening"
              audioPath={opening.audio_path}
            />
          </Series.Sequence>
        )}

        {/* Content Parts */}
        {parts.map((part, idx) => {
          // Warn if duration is missing
          if (!part.duration || part.duration <= 0) {
            console.warn(`⚠️ WritingCoach Part ${idx}: Missing duration, using fallback 4s`);
          }
          const durationFrames = Math.ceil((part.duration || 4) * fps);
          return (
            <Series.Sequence key={idx} durationInFrames={durationFrames}>
              <PartCard
                part={part}
                partIndex={idx}
                totalParts={parts.length}
              />
            </Series.Sequence>
          );
        })}

        {/* Closing Ment */}
        {closing?.audio_path && closing.duration && (
          <Series.Sequence durationInFrames={Math.ceil(closing.duration * fps)}>
            <OpeningClosingSlide
              text={closingMent}
              type="closing"
              audioPath={closing.audio_path}
            />
          </Series.Sequence>
        )}
      </Series>
    </AbsoluteFill>
  );
};

// ─── Opening/Closing Slide Component ─────────────────────────────────────────
interface OpeningClosingSlideProps {
  text: string;
  type: "opening" | "closing";
  audioPath: string;
}

const OpeningClosingSlide: React.FC<OpeningClosingSlideProps> = ({
  text,
  type,
  audioPath,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const isOpening = type === "opening";
  const accentColor = isOpening ? "#6ecfff" : "#f5c96e";
  const emoji = isOpening ? "👋" : "✨";

  // Entrance animation
  const entrance = spring({
    frame,
    fps,
    config: SPRING_CFG,
  });
  const entranceProgress = Math.min(entrance, 1);
  const translateY = interpolate(entranceProgress, [0, 1], [40, 0]);

  // Fade out at end
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 8, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const audioSrc = staticFile(audioPath.replace(/^\//, ""));

  return (
    <AbsoluteFill>
      {/* Content */}
      <AbsoluteFill>
        <div
          style={{
            position: "absolute",
            top: SAFE_ZONE.paddingTop,
            left: SAFE_ZONE.paddingLeft,
            right: SAFE_ZONE.paddingRight,
            bottom: SAFE_ZONE.paddingBottom,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: entranceProgress * fadeOut,
            transform: `translateY(${translateY}px)`,
          }}
        >
          <div
            style={{
              background: CARD_COLORS.bg,
              borderRadius: 28,
              padding: "48px 40px",
              boxShadow: CARD_COLORS.shadow,
              position: "relative",
              maxWidth: "90%",
            }}
          >
            {/* Accent stripe */}
            <div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                top: 0,
                height: 6,
                background: accentColor,
              }}
            />

            {/* Emoji icon */}
            <div style={{ textAlign: "center", marginBottom: 20 }}>
              <span style={{ fontSize: 48 }}>{emoji}</span>
            </div>

            {/* Text */}
            <p
              style={{
                fontFamily: "'Noto Sans KR', 'Malgun Gothic', sans-serif",
                fontSize: 40,
                fontWeight: 600,
                color: CARD_COLORS.body,
                margin: 0,
                textAlign: "center",
                lineHeight: 1.5,
              }}
            >
              {text}
            </p>
          </div>
        </div>
      </AbsoluteFill>

      {/* Audio */}
      <Audio src={audioSrc} />
    </AbsoluteFill>
  );
};

// ─── Legacy Component (fallback for old data format) ────────────────────────
interface LegacyProps {
  parts: PartData[];
  videoBgSrc: string | null;
  videoDurationSec?: number;
  audioSrc: string | null;
}

const LegacyWritingCoach: React.FC<LegacyProps> = ({
  parts,
  videoBgSrc,
  videoDurationSec,
  audioSrc,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Character-based timing
  const totalChars = parts.reduce((sum, p) => sum + p.ko.length, 0);
  let currentIdx = 0;
  let charsSoFar = 0;
  const charProgress = (frame / durationInFrames) * totalChars;

  for (let i = 0; i < parts.length; i++) {
    charsSoFar += parts[i].ko.length;
    if (charProgress < charsSoFar) {
      currentIdx = i;
      break;
    }
    currentIdx = i;
  }

  const currentPart = parts[currentIdx] || { role: "intro", ko: "", vi: "" };
  // Check if this is the last part to show "Kết Bài"
  const isLastPart = currentIdx === parts.length - 1;
  const section = getSectionMeta(currentPart.role, isLastPart);

  // Typewriter
  const startFrame = Math.floor(
    (charsSoFar - currentPart.ko.length) / totalChars * durationInFrames
  );
  const viCharsToShow = Math.floor((frame - startFrame) / 2);
  const viText = currentPart.vi
    ? currentPart.vi.substring(0, viCharsToShow)
    : "";
  const viComplete =
    currentPart.vi && viCharsToShow >= currentPart.vi.length;

  // Fade out
  const fadeOut = interpolate(
    frame,
    [durationInFrames - fps * 0.8, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill>
      {/* Looping Video Background */}
      <WritingCoachBackground videoBgSrc={videoBgSrc} videoDurationSec={videoDurationSec} />
      <AbsoluteFill>
        <div
          style={{
            width: "100%",
            height: "100%",
            background: "rgba(15, 23, 42, 0.70)",
          }}
        />
      </AbsoluteFill>

      {/* Progress Bar */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop,
          left: SAFE_ZONE.paddingLeft,
          right: SAFE_ZONE.paddingRight,
          display: "flex",
          gap: 10,
          opacity: fadeOut,
        }}
      >
        {SECTIONS.slice(0, parts.length).map((sec, idx) => (
          <div
            key={sec.key}
            style={{
              flex: 1,
              height: 6,
              borderRadius: 3,
              background:
                idx <= currentIdx ? sec.accent : "rgba(255,255,255,0.2)",
              boxShadow: idx <= currentIdx ? `0 0 10px ${sec.accent}` : "none",
            }}
          />
        ))}
      </div>

      {/* Flashcard */}
      <div
        style={{
          position: "absolute",
          top: SAFE_ZONE.paddingTop + 40,
          left: "7.5%",
          width: "85%",
          bottom: SAFE_ZONE.paddingBottom,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: fadeOut,
        }}
      >
        <div
          style={{
            width: "100%",
            background: CARD_COLORS.bg,
            borderRadius: 28,
            padding: "36px 32px",
            boxShadow: CARD_COLORS.shadow,
            position: "relative",
          }}
        >
          {/* Accent stripe */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              height: 6,
              background: section.accent,
            }}
          />

          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              marginBottom: 20,
              marginTop: 4,
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: "50%",
                background: `${section.accent}20`,
                border: `3px solid ${section.accent}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span style={{ fontSize: 24 }}>{section.emoji}</span>
            </div>
            <div>
              <span
                style={{
                  fontFamily: "'Segoe UI', sans-serif",
                  fontSize: 38,
                  fontWeight: 700,
                  color: CARD_COLORS.header,
                  display: "block",
                  lineHeight: 1.1,
                }}
              >
                {section.label}
              </span>
              <span
                style={{
                  fontFamily: "'Noto Sans KR', sans-serif",
                  fontSize: 20,
                  color: "#9ca3af",
                  fontWeight: 500,
                }}
              >
                {section.korean}
              </span>
            </div>
          </div>

          {/* Korean Text */}
          <p
            style={{
              fontFamily: "'Noto Sans KR', sans-serif",
              fontSize: currentPart.ko.length > 60 ? 32 : 36,
              fontWeight: 500,
              color: CARD_COLORS.body,
              margin: 0,
              lineHeight: 1.6,
              marginBottom: currentPart.vi ? 20 : 0,
            }}
          >
            {currentPart.ko || "—"}
          </p>

          {/* Vietnamese */}
          {currentPart.vi && (
            <div style={{ paddingTop: 16, borderTop: "2px solid #e5e7eb" }}>
              <p
                style={{
                  fontFamily: "'Segoe UI', sans-serif",
                  fontSize: 28,
                  fontWeight: 400,
                  color: CARD_COLORS.translation,
                  margin: 0,
                  lineHeight: 1.5,
                  fontStyle: "italic",
                  minHeight: 42,
                }}
              >
                💡 {viText}
                {!viComplete && (
                  <span
                    style={{
                      opacity: Math.sin(frame * 0.3) > 0 ? 1 : 0,
                      color: CARD_COLORS.header,
                    }}
                  >
                    |
                  </span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Audio */}
      {audioSrc && <Audio src={audioSrc} />}
    </AbsoluteFill>
  );
};
