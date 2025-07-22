import React from "react";

interface ReactionIconProps {
  className?: string;
  animate?: boolean;
}

export const LikeIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="none"
  >
    <defs>
      <linearGradient
        id="like-gradient-faithful"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#1877F2" />
        <stop offset="100%" stopColor="#166FE5" />
      </linearGradient>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="#1877F2"
      stroke="#166FE5"
      strokeWidth="1"
    />
    <path
      d="M8 18c0-1.5 1-3 3-3 1 0 1.5.5 2 1 .5-1.5 1.5-2 3-2s3 1.5 3 3v4c0 1-1 2-2 2H10c-1 0-2-1-2-2v-3z"
      fill="white"
    />
    <path d="M16 14v-2c0-1 1-2 2-2s2 1 2 2c0 .5-.5 1-1 1h-3z" fill="white" />
  </svg>
);

// Keep the elegant heart as user requested
export const LoveIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-bounce" : ""}`}
    fill="none"
  >
    <defs>
      <linearGradient
        id="love-gradient-faithful"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#FF5722" />
        <stop offset="50%" stopColor="#F44336" />
        <stop offset="100%" stopColor="#E91E63" />
      </linearGradient>
      <filter id="love-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#E91E63"
          floodOpacity="0.4"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#love-gradient-faithful)"
      filter="url(#love-shadow)"
    />
    <path
      d="M16 25c0 0-7-4.5-7-9.5 0-2.5 2-4.5 4.5-4.5 1.5 0 2.5 1 2.5 1s1-1 2.5-1c2.5 0 4.5 2 4.5 4.5 0 5-7 9.5-7 9.5z"
      fill="white"
    />
  </svg>
);

export const HahaIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-bounce" : ""}`}
    fill="none"
  >
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="#FFDA44"
      stroke="#FFD93D"
      strokeWidth="1"
    />

    {/* Eyes - X shape for laughing */}
    <path
      d="M11 11l2 2m-2 0l2-2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M19 11l2 2m-2 0l2-2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
    />

    {/* Big smile */}
    <path
      d="M10 18c0 0 2.5 4 6 4s6-4 6-4"
      stroke="#333"
      strokeWidth="2.5"
      strokeLinecap="round"
      fill="none"
    />

    {/* Tear of joy */}
    <circle cx="8" cy="16" r="1.5" fill="#6BB6FF" opacity="0.8" />
  </svg>
);

export const WowIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="none"
  >
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="#FFDA44"
      stroke="#FFD93D"
      strokeWidth="1"
    />

    {/* Wide surprised eyes */}
    <circle cx="11" cy="12" r="2.5" fill="#333" />
    <circle cx="21" cy="12" r="2.5" fill="#333" />

    {/* Small surprised mouth */}
    <ellipse cx="16" cy="20" rx="2" ry="3" fill="#333" />

    {/* Raised eyebrows */}
    <path
      d="M8 8c1 0 2 .5 3 1"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M24 8c-1 0-2 .5-3 1"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

export const SadIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="none"
  >
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="#FFDA44"
      stroke="#FFD93D"
      strokeWidth="1"
    />

    {/* Sad eyes */}
    <ellipse cx="11" cy="12" rx="1.5" ry="1" fill="#333" />
    <ellipse cx="21" cy="12" rx="1.5" ry="1" fill="#333" />

    {/* Downturned mouth */}
    <path
      d="M10 20c0 0 2-2 6-2s6 2 6 2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />

    {/* Single tear */}
    <ellipse cx="22" cy="16" rx="1" ry="2.5" fill="#6BB6FF" />

    {/* Sad eyebrows */}
    <path
      d="M8 9c1 1 2 1 3 1"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <path
      d="M24 9c-1 1-2 1-3 1"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

export const AngryIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 32 32"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="none"
  >
    <circle
      cx="16"
      cy="16"
      r="14"
      fill="#F25022"
      stroke="#E54B2B"
      strokeWidth="1"
    />

    {/* Angry eyes */}
    <ellipse cx="11" cy="13" rx="1.5" ry="1" fill="#fff" />
    <ellipse cx="21" cy="13" rx="1.5" ry="1" fill="#fff" />

    {/* Angry frown */}
    <path
      d="M10 19c0 0 2-1.5 6-1.5s6 1.5 6 1.5"
      stroke="#fff"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />

    {/* Angry eyebrows */}
    <path d="M8 8l4 3" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
    <path d="M24 8l-4 3" stroke="#fff" strokeWidth="2" strokeLinecap="round" />

    {/* Steam lines */}
    <path
      d="M6 6l1 2M26 6l-1 2"
      stroke="#fff"
      strokeWidth="1.5"
      strokeLinecap="round"
      opacity="0.8"
    />
  </svg>
);

export const faithfulReactionIcons = {
  like: LikeIcon,
  love: LoveIcon,
  haha: HahaIcon,
  wow: WowIcon,
  sad: SadIcon,
  angry: AngryIcon,
};
