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
        id="like-gradient-elegant"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#4285F4" />
        <stop offset="100%" stopColor="#1976D2" />
      </linearGradient>
      <filter id="like-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#1976D2"
          floodOpacity="0.3"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#like-gradient-elegant)"
      filter="url(#like-shadow)"
    />
    <path
      d="M20.5 12.5C20.5 11.12 19.38 10 18 10c-1.13 0-2 .88-2 2 0-1.12-.87-2-2-2-1.38 0-2.5 1.12-2.5 2.5 0 2.5 4.5 6.5 4.5 6.5s4.5-4 4.5-6.5z"
      fill="white"
      stroke="white"
      strokeWidth="0.5"
    />
  </svg>
);

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
        id="love-gradient-elegant"
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
      fill="url(#love-gradient-elegant)"
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
    <defs>
      <linearGradient
        id="haha-gradient-elegant"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#FFD54F" />
        <stop offset="100%" stopColor="#FF9800" />
      </linearGradient>
      <filter id="haha-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#FF9800"
          floodOpacity="0.3"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#haha-gradient-elegant)"
      filter="url(#haha-shadow)"
    />

    {/* Eyes */}
    <ellipse cx="12" cy="12" rx="1.5" ry="2" fill="#333" />
    <ellipse cx="20" cy="12" rx="1.5" ry="2" fill="#333" />

    {/* Mouth */}
    <path
      d="M10 18c0 0 2 4 6 4s6-4 6-4"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />

    {/* Tear drops */}
    <ellipse cx="8" cy="14" rx="1" ry="2" fill="#87CEEB" opacity="0.8" />
    <ellipse cx="24" cy="14" rx="1" ry="2" fill="#87CEEB" opacity="0.8" />
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
    <defs>
      <linearGradient
        id="wow-gradient-elegant"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#FFD54F" />
        <stop offset="100%" stopColor="#FFA726" />
      </linearGradient>
      <filter id="wow-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#FFA726"
          floodOpacity="0.3"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#wow-gradient-elegant)"
      filter="url(#wow-shadow)"
    />

    {/* Wide eyes */}
    <circle cx="12" cy="12" r="3" fill="white" />
    <circle cx="12" cy="12" r="2" fill="#333" />
    <circle cx="20" cy="12" r="3" fill="white" />
    <circle cx="20" cy="12" r="2" fill="#333" />

    {/* Open mouth */}
    <ellipse cx="16" cy="20" rx="2.5" ry="4" fill="#333" />
    <ellipse cx="16" cy="20" rx="1.5" ry="3" fill="white" />
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
    <defs>
      <linearGradient
        id="sad-gradient-elegant"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#64B5F6" />
        <stop offset="100%" stopColor="#1976D2" />
      </linearGradient>
      <filter id="sad-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#1976D2"
          floodOpacity="0.3"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#sad-gradient-elegant)"
      filter="url(#sad-shadow)"
    />

    {/* Sad eyes */}
    <ellipse cx="12" cy="12" rx="1.5" ry="1" fill="#333" />
    <ellipse cx="20" cy="12" rx="1.5" ry="1" fill="#333" />

    {/* Sad mouth */}
    <path
      d="M10 22c0 0 2-3 6-3s6 3 6 3"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />

    {/* Tear */}
    <ellipse cx="21" cy="16" rx="1.5" ry="3" fill="#87CEEB" opacity="0.9" />
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
    <defs>
      <linearGradient
        id="angry-gradient-elegant"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stopColor="#FF5722" />
        <stop offset="100%" stopColor="#D32F2F" />
      </linearGradient>
      <filter id="angry-shadow">
        <feDropShadow
          dx="0"
          dy="2"
          stdDeviation="3"
          floodColor="#D32F2F"
          floodOpacity="0.4"
        />
      </filter>
    </defs>
    <circle
      cx="16"
      cy="16"
      r="15"
      fill="url(#angry-gradient-elegant)"
      filter="url(#angry-shadow)"
    />

    {/* Angry eyes */}
    <ellipse cx="12" cy="13" rx="1.5" ry="1" fill="#333" />
    <ellipse cx="20" cy="13" rx="1.5" ry="1" fill="#333" />

    {/* Angry eyebrows */}
    <path d="M9 9l4 2" stroke="#333" strokeWidth="2" strokeLinecap="round" />
    <path d="M23 9l-4 2" stroke="#333" strokeWidth="2" strokeLinecap="round" />

    {/* Angry mouth */}
    <path
      d="M10 20c0 0 2-2 6-2s6 2 6 2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />

    {/* Steam */}
    <path
      d="M8 6l1 3"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
      opacity="0.7"
    />
    <path
      d="M24 6l-1 3"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
      opacity="0.7"
    />
  </svg>
);

export const elegantReactionIcons = {
  like: LikeIcon,
  love: LoveIcon,
  haha: HahaIcon,
  wow: WowIcon,
  sad: SadIcon,
  angry: AngryIcon,
};
