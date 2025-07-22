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
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="like-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#4F46E5" />
        <stop offset="100%" stopColor="#3B82F6" />
      </linearGradient>
    </defs>
    <path
      d="M7.493 18.75c-.425 0-.82-.236-.975-.632A7.48 7.48 0 016 15.375c0-1.75.599-3.358 1.602-4.634.151-.192.373-.309.6-.397.473-.183.89-.514 1.212-.924a9.042 9.042 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 01.75-.75A2.25 2.25 0 0116.5 4.5c0 1.152-.26 2.243-.723 3.218-.266.558-.107 1.282.725 1.282h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 01-2.649 7.521c-.388.482-.987.729-1.605.729H14.23c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 00-1.423-.23h-.777zM2.331 10.977a11.969 11.969 0 00-.831 4.398 12 12 0 00.52 3.507c.26.85 1.084 1.368 1.973 1.368H4.9c.445 0 .72-.498.523-.898a8.963 8.963 0 01-.924-3.977c0-1.708.476-3.305 1.302-4.666.245-.403-.028-.959-.5-.959H4.25c-.832 0-1.612.453-1.918 1.227z"
      fill="url(#like-gradient)"
    />
  </svg>
);

export const LoveIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-bounce" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="love-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FF6B6B" />
        <stop offset="50%" stopColor="#FF5722" />
        <stop offset="100%" stopColor="#E91E63" />
      </linearGradient>
    </defs>
    <path
      d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"
      fill="url(#love-gradient)"
    />
  </svg>
);

export const HahaIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-spin" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="haha-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FFC107" />
        <stop offset="100%" stopColor="#FF9800" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" fill="url(#haha-gradient)" />
    <circle cx="8" cy="9" r="1.5" fill="#333" />
    <circle cx="16" cy="9" r="1.5" fill="#333" />
    <path
      d="M8 14s1.5 3 4 3 4-3 4-3"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />
    <path
      d="M6 6l2 2M18 6l-2 2"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

export const WowIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="wow-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FFC107" />
        <stop offset="100%" stopColor="#FF9800" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" fill="url(#wow-gradient)" />
    <circle cx="8" cy="9" r="2" fill="#333" />
    <circle cx="16" cy="9" r="2" fill="#333" />
    <ellipse cx="12" cy="15" rx="2" ry="3" fill="#333" />
    <path
      d="M7 5c1 0 2 1 2 2M17 5c-1 0-2 1-2 2"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
      fill="none"
    />
  </svg>
);

export const SadIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-bounce" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="sad-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#64B5F6" />
        <stop offset="100%" stopColor="#2196F3" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" fill="url(#sad-gradient)" />
    <circle cx="8" cy="9" r="1.5" fill="#333" />
    <circle cx="16" cy="9" r="1.5" fill="#333" />
    <path
      d="M8 16s1.5-2 4-2 4 2 4 2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />
    <path
      d="M7 7l1 3M17 7l-1 3"
      stroke="#64B5F6"
      strokeWidth="2"
      strokeLinecap="round"
      opacity="0.7"
    />
  </svg>
);

export const AngryIcon: React.FC<ReactionIconProps> = ({
  className = "",
  animate = false,
}) => (
  <svg
    viewBox="0 0 24 24"
    className={`${className} ${animate ? "animate-pulse" : ""}`}
    fill="currentColor"
  >
    <defs>
      <linearGradient id="angry-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FF5722" />
        <stop offset="100%" stopColor="#D32F2F" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" fill="url(#angry-gradient)" />
    <circle cx="8" cy="10" r="1.5" fill="#333" />
    <circle cx="16" cy="10" r="1.5" fill="#333" />
    <path
      d="M8 15s2-1 4-1 4 1 4 1"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />
    <path
      d="M6 7l3 2M18 7l-3 2"
      stroke="#333"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M9 6l1 1M15 6l-1 1"
      stroke="#333"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

export const reactionIcons = {
  like: LikeIcon,
  love: LoveIcon,
  haha: HahaIcon,
  wow: WowIcon,
  sad: SadIcon,
  angry: AngryIcon,
};
