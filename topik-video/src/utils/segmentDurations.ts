/**
 * Utility functions for calculating segment durations based on character count.
 * Useful for syncing text with audio when precise timing data is unavailable.
 */

// ─── Types ───────────────────────────────────────────────────────────────────
interface SegmentWithText {
  ko?: string;
  vi?: string;
  content?: string;
  text?: string;
  [key: string]: unknown;
}

interface SegmentDurationResult {
  startFrame: number;
  duration: number;
  endFrame: number;
}

// ─── Helper: Extract text from segment ───────────────────────────────────────
function getSegmentText(segment: SegmentWithText, textField?: string): string {
  if (textField && segment[textField]) {
    return String(segment[textField]);
  }
  // Try common field names in priority order
  return (
    segment.ko ||
    segment.content ||
    segment.text ||
    segment.vi ||
    ""
  );
}

// ─── Helper: Count characters (excluding whitespace for more accurate timing) ─
function countCharacters(text: string, excludeWhitespace: boolean = false): number {
  if (!text) return 0;
  if (excludeWhitespace) {
    return text.replace(/\s/g, "").length;
  }
  return text.length;
}

/**
 * Calculate segment durations based on character count distribution.
 * 
 * @param segments - Array of segment objects containing text
 * @param totalFrames - Total duration of the video in frames
 * @param options - Configuration options
 * @returns Array of startFrame numbers for each segment
 * 
 * @example
 * const segments = [
 *   { ko: "안녕하세요" },
 *   { ko: "반갑습니다" },
 *   { ko: "감사합니다" }
 * ];
 * const startFrames = calculateSegmentDurations(segments, 300);
 * // Returns: [0, 100, 200] (assuming equal character counts)
 */
export function calculateSegmentDurations(
  segments: SegmentWithText[],
  totalFrames: number,
  options: {
    textField?: string;           // Which field to read text from (auto-detect if not specified)
    minDurationFrames?: number;   // Minimum duration per segment (default: 30 = 1s @ 30fps)
    excludeWhitespace?: boolean;  // Exclude whitespace from character count (default: false)
  } = {}
): number[] {
  const {
    textField,
    minDurationFrames = 30,
    excludeWhitespace = false,
  } = options;

  if (!segments || segments.length === 0) {
    return [];
  }

  if (segments.length === 1) {
    return [0];
  }

  // Calculate character counts for each segment
  const charCounts = segments.map((segment) =>
    countCharacters(getSegmentText(segment, textField), excludeWhitespace)
  );

  // Total characters across all segments
  const totalChars = charCounts.reduce((sum, count) => sum + count, 0);

  // Handle edge case: no characters
  if (totalChars === 0) {
    // Equal distribution
    const equalDuration = totalFrames / segments.length;
    return segments.map((_, idx) => Math.round(idx * equalDuration));
  }

  // Calculate durations proportionally
  const durations = charCounts.map((count) => {
    const proportionalDuration = (count / totalChars) * totalFrames;
    return Math.max(proportionalDuration, minDurationFrames);
  });

  // Normalize durations to fit within totalFrames
  const totalDuration = durations.reduce((sum, d) => sum + d, 0);
  const scaleFactor = totalFrames / totalDuration;
  const scaledDurations = durations.map((d) => d * scaleFactor);

  // Calculate cumulative startFrames
  const startFrames: number[] = [];
  let cumulativeFrame = 0;

  for (let i = 0; i < scaledDurations.length; i++) {
    startFrames.push(Math.round(cumulativeFrame));
    cumulativeFrame += scaledDurations[i];
  }

  return startFrames;
}

/**
 * Extended version that returns full duration info for each segment.
 * 
 * @param segments - Array of segment objects containing text
 * @param totalFrames - Total duration of the video in frames
 * @param options - Configuration options
 * @returns Array of objects with startFrame, duration, and endFrame
 */
export function calculateSegmentDurationsDetailed(
  segments: SegmentWithText[],
  totalFrames: number,
  options: {
    textField?: string;
    minDurationFrames?: number;
    excludeWhitespace?: boolean;
  } = {}
): SegmentDurationResult[] {
  const startFrames = calculateSegmentDurations(segments, totalFrames, options);

  return startFrames.map((startFrame, idx) => {
    const nextStart = startFrames[idx + 1] ?? totalFrames;
    const duration = nextStart - startFrame;
    return {
      startFrame,
      duration,
      endFrame: nextStart,
    };
  });
}

/**
 * Calculate frames per character for a given segment.
 * Useful for karaoke-style character-by-character animations.
 * 
 * @param text - The text content
 * @param durationFrames - Duration in frames for this text
 * @returns Frames per character (for animation timing)
 */
export function getFramesPerCharacter(text: string, durationFrames: number): number {
  const charCount = countCharacters(text);
  if (charCount === 0) return 0;
  return durationFrames / charCount;
}

/**
 * Get the character index that should be highlighted at a given frame.
 * 
 * @param text - The text content
 * @param frameInSegment - Current frame within the segment (0-based)
 * @param segmentDuration - Total duration of the segment in frames
 * @param bufferPercent - Percentage of duration to reserve at end (default: 15%)
 * @returns The index of the last character that should be highlighted
 */
export function getHighlightedCharIndex(
  text: string,
  frameInSegment: number,
  segmentDuration: number,
  bufferPercent: number = 0.15
): number {
  const charCount = countCharacters(text);
  if (charCount === 0) return -1;

  const effectiveDuration = segmentDuration * (1 - bufferPercent);
  const progress = Math.min(frameInSegment / effectiveDuration, 1);
  
  return Math.floor(progress * charCount);
}
