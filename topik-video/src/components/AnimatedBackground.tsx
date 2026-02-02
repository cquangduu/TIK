import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, OffthreadVideo, Loop } from "remotion";

// ═══════════════════════════════════════════════════════════════════════════════
// ANIMATED GRADIENT BACKGROUND
// Professional alternative to video backgrounds - 100% reliable, no loop issues
// ═══════════════════════════════════════════════════════════════════════════════

export type BackgroundVariant = 
  | "dark"        // Default dark mode - professional
  | "aurora"      // Teal/cyan accents - calming
  | "sunset"      // Purple/pink accents - warm
  | "ocean"       // Blue accents - focus
  | "forest"      // Green accents - natural
  | "quiz"        // Purple/violet - quiz games
  | "academic";   // Deep blue - deep dive content

interface AnimatedBackgroundProps {
  variant?: BackgroundVariant;
  intensity?: "subtle" | "normal" | "vibrant";
}

// Color palettes optimized for different content types
const PALETTES: Record<BackgroundVariant, {
  colors: string[];
  accent: string;
  secondary: string;
}> = {
  dark: {
    colors: ["#0d1117", "#161b22", "#1a1f2e", "#0f1419", "#12171f"],
    accent: "rgba(165, 214, 255, 0.08)",
    secondary: "rgba(136, 146, 176, 0.05)",
  },
  aurora: {
    colors: ["#0d1b2a", "#1b263b", "#2d3a4a", "#1a2634", "#0f1922"],
    accent: "rgba(100, 255, 218, 0.1)",
    secondary: "rgba(64, 224, 208, 0.06)",
  },
  sunset: {
    colors: ["#1a1423", "#2d1f3d", "#1f1a2e", "#291f35", "#1e1528"],
    accent: "rgba(255, 107, 107, 0.1)",
    secondary: "rgba(255, 154, 158, 0.06)",
  },
  ocean: {
    colors: ["#0a192f", "#112240", "#1d3557", "#14213d", "#0d1b2a"],
    accent: "rgba(100, 181, 246, 0.1)",
    secondary: "rgba(66, 165, 245, 0.06)",
  },
  forest: {
    colors: ["#0d1f0d", "#1a2e1a", "#1f3d1f", "#142d14", "#0f1f0f"],
    accent: "rgba(129, 199, 132, 0.1)",
    secondary: "rgba(76, 175, 80, 0.06)",
  },
  quiz: {
    colors: ["#1a1033", "#251745", "#2d1f52", "#1f1540", "#18102d"],
    accent: "rgba(156, 136, 255, 0.12)",
    secondary: "rgba(124, 77, 255, 0.08)",
  },
  academic: {
    colors: ["#0f0f23", "#1a1a2e", "#1e1e3f", "#151530", "#12122a"],
    accent: "rgba(124, 77, 255, 0.1)",
    secondary: "rgba(63, 81, 181, 0.06)",
  },
};

// Intensity multipliers
const INTENSITY_CONFIG = {
  subtle: { orb: 0.6, particle: 0.4, movement: 0.5 },
  normal: { orb: 1.0, particle: 1.0, movement: 1.0 },
  vibrant: { orb: 1.4, particle: 1.5, movement: 1.3 },
};

export const AnimatedBackground: React.FC<AnimatedBackgroundProps> = ({
  variant = "dark",
  intensity = "normal",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  
  const palette = PALETTES[variant];
  const intensityConfig = INTENSITY_CONFIG[intensity];
  
  // Very slow animation - one full cycle over ~30 seconds
  const progress = (frame / fps) * 0.03 * intensityConfig.movement;
  
  // Animated gradient angles
  const angle1 = 45 + Math.sin(progress) * 15;
  const angle2 = 135 + Math.cos(progress * 0.7) * 20;
  
  // Floating orbs positions (bokeh effect)
  const orbs = [
    { x: 20 + Math.sin(progress * 0.5) * 15, y: 30 + Math.cos(progress * 0.4) * 20 },
    { x: 70 + Math.cos(progress * 0.6) * 20, y: 60 + Math.sin(progress * 0.5) * 15 },
    { x: 40 + Math.sin(progress * 0.8) * 25, y: 80 + Math.cos(progress * 0.7) * 10 },
  ];
  
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
      
      {/* Secondary gradient overlay - radial orbs */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: `
            radial-gradient(ellipse at ${orbs[0].x}% ${orbs[0].y}%, ${palette.accent} 0%, transparent 50%),
            radial-gradient(ellipse at ${orbs[1].x}% ${orbs[1].y}%, ${palette.accent} 0%, transparent 40%),
            radial-gradient(ellipse at ${orbs[2].x}% ${orbs[2].y}%, ${palette.accent} 0%, transparent 45%)
          `,
          opacity: 0.8 * intensityConfig.orb,
        }}
      />
      
      {/* Subtle light sweep */}
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
        const x = 15 + i * 15 + Math.sin(progress * (0.3 + i * 0.1)) * 10;
        const y = 10 + i * 15 + Math.cos(progress * (0.4 + i * 0.1)) * 15;
        const baseOpacity = 0.03 + (i % 3) * 0.02;
        const opacity = baseOpacity * intensityConfig.particle;
        
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
              background: `radial-gradient(circle, ${palette.secondary.replace(/[\d.]+\)$/, `${opacity})`)} 0%, transparent 70%)`,
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

// ═══════════════════════════════════════════════════════════════════════════════
// LEGACY COMPATIBILITY WRAPPER
// Drop-in replacement for video-based LoopingBackground
// ═══════════════════════════════════════════════════════════════════════════════

interface LoopingBackgroundProps {
  videoBgSrc?: string | null;
  variant?: BackgroundVariant;
  intensity?: "subtle" | "normal" | "vibrant";
}

export const LoopingBackground: React.FC<LoopingBackgroundProps> = ({
  videoBgSrc: _videoBgSrc, // Ignored - we always use animated gradient
  variant = "dark",
  intensity = "normal",
}) => {
  // Always use animated gradient for stability
  // Video backgrounds have proven unreliable for looping
  return <AnimatedBackground variant={variant} intensity={intensity} />;
};

// ═══════════════════════════════════════════════════════════════════════════════
// VIDEO LOOP BACKGROUND
// Sử dụng OffthreadVideo với Loop - alternative khi cần dùng video thật
// ═══════════════════════════════════════════════════════════════════════════════

interface VideoLoopBackgroundProps {
  src: string;
  loopDuration?: number; // Duration in frames for one loop cycle
  blur?: number;
  brightness?: number;
  fallbackVariant?: BackgroundVariant;
}

export const VideoLoopBackground: React.FC<VideoLoopBackgroundProps> = ({
  src,
  loopDuration = 300, // 10 seconds at 30fps
  blur = 3,
  brightness = 0.6,
  fallbackVariant = "dark",
}) => {
  // Fallback to animated gradient if no source
  if (!src) {
    return <AnimatedBackground variant={fallbackVariant} />;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      <Loop durationInFrames={loopDuration}>
        <OffthreadVideo
          src={src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: `blur(${blur}px) brightness(${brightness})`,
          }}
        />
      </Loop>
    </AbsoluteFill>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// HYBRID BACKGROUND
// Chọn giữa video hoặc gradient tùy theo điều kiện
// ═══════════════════════════════════════════════════════════════════════════════

interface HybridBackgroundProps {
  videoSrc?: string | null;
  useVideo?: boolean; // Force video mode
  loopDuration?: number;
  blur?: number;
  brightness?: number;
  variant?: BackgroundVariant;
  intensity?: "subtle" | "normal" | "vibrant";
}

export const HybridBackground: React.FC<HybridBackgroundProps> = ({
  videoSrc,
  useVideo = false,
  loopDuration = 300,
  blur = 3,
  brightness = 0.6,
  variant = "dark",
  intensity = "normal",
}) => {
  // Dùng video nếu có source và được yêu cầu
  if (useVideo && videoSrc) {
    return (
      <VideoLoopBackground
        src={videoSrc}
        loopDuration={loopDuration}
        blur={blur}
        brightness={brightness}
        fallbackVariant={variant}
      />
    );
  }

  // Mặc định dùng animated gradient (ổn định hơn)
  return <AnimatedBackground variant={variant} intensity={intensity} />;
};

// ═══════════════════════════════════════════════════════════════════════════════
// UNIVERSAL LOOPING VIDEO BACKGROUND
// Shared component for all video types - handles video loop with fallback
// ═══════════════════════════════════════════════════════════════════════════════

const DEFAULT_VIDEO_BG_DURATION_SEC = 28.12; // Fallback duration in seconds

export interface UniversalLoopingBackgroundProps {
  videoBgSrc?: string | null;
  videoDurationSec?: number;
  variant?: BackgroundVariant;
  intensity?: "subtle" | "normal" | "vibrant";
  blur?: number;
  brightness?: number;
}

export const UniversalLoopingBackground: React.FC<UniversalLoopingBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
  variant = "dark",
  intensity = "normal",
  blur = 3,
  brightness = 0.5,
}) => {
  const { fps, durationInFrames } = useVideoConfig();
  
  // Calculate loop parameters
  const actualDuration = videoDurationSec || DEFAULT_VIDEO_BG_DURATION_SEC;
  const videoDurationFrames = Math.ceil(actualDuration * fps);
  const loopCount = Math.ceil(durationInFrames / videoDurationFrames);
  
  // Fallback to animated gradient if no video source
  if (!videoBgSrc) {
    return <AnimatedBackground variant={variant} intensity={intensity} />;
  }
  
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Loop durationInFrames={videoDurationFrames} times={loopCount}>
        <OffthreadVideo
          src={videoBgSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: `blur(${blur}px) brightness(${brightness})`,
          }}
          muted
        />
      </Loop>
    </AbsoluteFill>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// PRESET BACKGROUNDS FOR SPECIFIC CONTENT TYPES
// All now support video loop with fallback to animated gradient
// ═══════════════════════════════════════════════════════════════════════════════

interface PresetBackgroundProps {
  videoBgSrc?: string | null;
  videoDurationSec?: number;
}

// News/Healing content background
export const NewsHealingBackground: React.FC<PresetBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
}) => (
  <UniversalLoopingBackground
    videoBgSrc={videoBgSrc}
    videoDurationSec={videoDurationSec}
    variant="dark"
    intensity="subtle"
    blur={4}
    brightness={0.45}
  />
);

// Quiz game background
export const QuizBackground: React.FC<PresetBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
}) => (
  <UniversalLoopingBackground
    videoBgSrc={videoBgSrc}
    videoDurationSec={videoDurationSec}
    variant="quiz"
    intensity="normal"
    blur={5}
    brightness={0.4}
  />
);

// Deep dive academic background
export const DeepDiveBackground: React.FC<PresetBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
}) => (
  <UniversalLoopingBackground
    videoBgSrc={videoBgSrc}
    videoDurationSec={videoDurationSec}
    variant="academic"
    intensity="normal"
    blur={6}
    brightness={0.35}
  />
);

// Writing coach background
export const WritingCoachBackground: React.FC<PresetBackgroundProps> = ({
  videoBgSrc,
  videoDurationSec,
}) => (
  <UniversalLoopingBackground
    videoBgSrc={videoBgSrc}
    videoDurationSec={videoDurationSec}
    variant="ocean"
    intensity="subtle"
    blur={4}
    brightness={0.45}
  />
);

export default AnimatedBackground;
