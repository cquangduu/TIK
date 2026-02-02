import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

// ─── Props Interface ─────────────────────────────────────────────────────────
interface KaraokeTextProps {
  text: string;
  startFrame: number;
  duration: number;
  fontSize?: number;
  fontWeight?: number;
  baseColor?: string;
  highlightColor?: string;
  fontFamily?: string;
  lineHeight?: number;
  textAlign?: "left" | "center" | "right";
}

// ─── Korean character segmentation ───────────────────────────────────────────
// Split text into syllable blocks for smooth karaoke highlighting
function splitKoreanText(text: string): string[] {
  // Korean characters are single blocks, so split by character
  // For mixed text, we group by words for smoother animation
  const words = text.split(/(\s+)/);
  const segments: string[] = [];
  
  words.forEach((word) => {
    if (/\s+/.test(word)) {
      // Preserve whitespace as segment
      segments.push(word);
    } else if (/[\uAC00-\uD7AF]/.test(word)) {
      // Korean word: split by syllable for karaoke effect
      segments.push(...word.split(""));
    } else {
      // Non-Korean word: keep as single unit
      segments.push(word);
    }
  });
  
  return segments;
}

// ─── KaraokeText Component ───────────────────────────────────────────────────
export const KaraokeText: React.FC<KaraokeTextProps> = ({
  text,
  startFrame,
  duration,
  fontSize = 38,
  fontWeight = 500,
  baseColor = "#374151",      // Gray-700 (unread)
  highlightColor = "#111827", // Gray-900 (read/active)
  fontFamily = "'Noto Sans KR', 'Malgun Gothic', sans-serif",
  lineHeight = 1.6,
  textAlign = "left",
}) => {
  const frame = useCurrentFrame();
  
  if (!text) return null;
  
  const segments = splitKoreanText(text);
  const totalSegments = segments.filter(s => !/^\s+$/.test(s)).length;
  
  // Progress through the text (0 to 1)
  const progress = interpolate(
    frame,
    [startFrame, startFrame + duration * 0.85], // Leave 15% buffer at end
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  
  // Current segment being highlighted
  const currentSegmentIndex = Math.floor(progress * totalSegments);
  
  let nonSpaceIndex = -1;
  
  return (
    <p
      style={{
        fontFamily,
        fontSize,
        fontWeight,
        margin: 0,
        lineHeight,
        textAlign,
      }}
    >
      {segments.map((segment, i) => {
        const isSpace = /^\s+$/.test(segment);
        
        if (!isSpace) {
          nonSpaceIndex++;
        }
        
        // Determine highlight state
        const isHighlighted = !isSpace && nonSpaceIndex <= currentSegmentIndex;
        const isActive = !isSpace && nonSpaceIndex === currentSegmentIndex;
        
        // Active character gets a subtle scale/glow effect
        const scale = isActive ? 1.05 : 1;
        const textShadow = isActive 
          ? "0 0 20px rgba(37, 99, 235, 0.3)" 
          : "none";
        
        return (
          <span
            key={i}
            style={{
              color: isHighlighted ? highlightColor : baseColor,
              display: "inline",
              transform: `scale(${scale})`,
              textShadow,
              transition: "color 0.1s ease-out",
            }}
          >
            {segment}
          </span>
        );
      })}
    </p>
  );
};
