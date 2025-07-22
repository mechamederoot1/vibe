import React from "react";

interface ReactionEmojiProps {
  type: string;
  size?: number;
  className?: string;
}

export const CustomReactionEmoji: React.FC<ReactionEmojiProps> = ({
  type,
  size = 24,
  className = "",
}) => {
  const svgStyle = {
    width: size,
    height: size,
  };

  switch (type) {
    case "like":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="likeGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#4267B2" />
              <stop offset="100%" stopColor="#365899" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#likeGradient)" />
          <path
            d="M7.5 11.5c0-1.5 1.2-2.7 2.7-2.7.8 0 1.5.3 2 .8.5-.5 1.2-.8 2-.8 1.5 0 2.7 1.2 2.7 2.7 0 .5-.1 1-.4 1.4l-4.3 4.3-4.3-4.3c-.3-.4-.4-.9-.4-1.4z"
            fill="white"
            transform="scale(0.8) translate(3,1)"
          />
          <path
            d="M8 14.5l2.5-2.5v6l-2.5-3.5z"
            fill="white"
            transform="scale(0.8) translate(3,1)"
          />
        </svg>
      );

    case "love":
    case "amei":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="loveGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#F25268" />
              <stop offset="100%" stopColor="#ED213A" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#loveGradient)" />
          <path
            d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
            fill="white"
            transform="scale(0.6) translate(4.8,3)"
          />
        </svg>
      );

    case "haha":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="hahaGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#FFD93D" />
              <stop offset="100%" stopColor="#F39C12" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#hahaGradient)" />
          <circle cx="8.5" cy="9" r="1.5" fill="#333" />
          <circle cx="15.5" cy="9" r="1.5" fill="#333" />
          <path
            d="M7 13.5c0 2.5 2.5 4.5 5 4.5s5-2 5-4.5"
            stroke="#333"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M6 14c1 1 2 1.5 3 1.5s2-.5 3-1.5 2-1 3-1 2 0 3 1"
            stroke="#333"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
          />
        </svg>
      );

    case "wow":
    case "uau":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="wowGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#FFD93D" />
              <stop offset="100%" stopColor="#F39C12" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#wowGradient)" />
          <circle cx="8.5" cy="9" r="2" fill="#333" />
          <circle cx="15.5" cy="9" r="2" fill="#333" />
          <ellipse cx="12" cy="15" rx="2" ry="3" fill="#333" />
          <circle cx="8.5" cy="9" r="0.5" fill="white" />
          <circle cx="15.5" cy="9" r="0.5" fill="white" />
        </svg>
      );

    case "sad":
    case "triste":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="sadGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#FFD93D" />
              <stop offset="100%" stopColor="#F39C12" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#sadGradient)" />
          <circle cx="8.5" cy="9" r="1.5" fill="#333" />
          <circle cx="15.5" cy="9" r="1.5" fill="#333" />
          <path
            d="M8 16c1-1.5 2.5-2 4-2s3 0.5 4 2"
            stroke="#333"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="9" cy="7" r="0.5" fill="#87CEEB" />
          <ellipse cx="9" cy="8.5" rx="0.3" ry="1" fill="#87CEEB" />
        </svg>
      );

    case "angry":
    case "grr":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="angryGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#E74C3C" />
              <stop offset="100%" stopColor="#C0392B" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#angryGradient)" />
          <circle cx="8.5" cy="10" r="1.5" fill="#FFF" />
          <circle cx="15.5" cy="10" r="1.5" fill="#FFF" />
          <circle cx="8.5" cy="10" r="1" fill="#333" />
          <circle cx="15.5" cy="10" r="1" fill="#333" />
          <path
            d="M7 7l2.5 2M17 7l-2.5 2"
            stroke="#FFF"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M8 16c1.5-1 3-1 4-1s2.5 0 4 1"
            stroke="#FFF"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
        </svg>
      );

    case "care":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="careGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#FFD93D" />
              <stop offset="100%" stopColor="#F39C12" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#careGradient)" />
          <circle cx="8.5" cy="9" r="1.5" fill="#333" />
          <circle cx="15.5" cy="9" r="1.5" fill="#333" />
          <path
            d="M7.5 14c1 2 2.5 3 4.5 3s3.5-1 4.5-3"
            stroke="#333"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M6 5c2 0 3 1 3 1s1-1 3-1 3 1 3 3-1 3-3 3-3-1-3-3"
            fill="#FFB6C1"
            opacity="0.8"
          />
        </svg>
      );

    case "nojinho":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="disgustGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#2ECC71" />
              <stop offset="100%" stopColor="#27AE60" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#disgustGradient)" />
          <circle cx="8.5" cy="9" r="1.5" fill="#FFF" />
          <circle cx="15.5" cy="9" r="1.5" fill="#FFF" />
          <circle cx="8.5" cy="9" r="1" fill="#333" />
          <circle cx="15.5" cy="9" r="1" fill="#333" />
          <path
            d="M9 15c1-0.5 2-0.5 3-0.5s2 0 3 0.5"
            stroke="#FFF"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <ellipse cx="12" cy="13" rx="1" ry="0.5" fill="#FFF" />
        </svg>
      );

    case "apaixonado":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="crushGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#FFD93D" />
              <stop offset="100%" stopColor="#F39C12" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#crushGradient)" />
          <path
            d="M6 8c0-1.5 1-2.5 2.5-2.5S11 6.5 11 8c0 1-0.5 1.5-1 1.5S8.5 9 8.5 8C8.5 7 8 6.5 7.5 6.5S6 7 6 8z"
            fill="#E74C3C"
          />
          <path
            d="M13 8c0-1.5 1-2.5 2.5-2.5S18 6.5 18 8c0 1-0.5 1.5-1 1.5S15.5 9 15.5 8C15.5 7 15 6.5 14.5 6.5S13 7 13 8z"
            fill="#E74C3C"
          />
          <ellipse cx="12" cy="15" rx="3" ry="1.5" fill="#333" />
          <path
            d="M9 14c1 1 2 1.5 3 1.5s2-0.5 3-1.5"
            stroke="#333"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
          />
        </svg>
      );

    case "pride":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="prideGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#9B59B6" />
              <stop offset="100%" stopColor="#8E44AD" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#prideGradient)" />
          <rect x="7" y="8" width="10" height="8" fill="white" rx="1" />
          <rect x="7" y="8" width="10" height="1.3" fill="#E74C3C" />
          <rect x="7" y="9.3" width="10" height="1.3" fill="#F39C12" />
          <rect x="7" y="10.6" width="10" height="1.3" fill="#F1C40F" />
          <rect x="7" y="11.9" width="10" height="1.3" fill="#2ECC71" />
          <rect x="7" y="13.2" width="10" height="1.3" fill="#3498DB" />
          <rect x="7" y="14.5" width="10" height="1.5" fill="#9B59B6" />
        </svg>
      );

    case "grateful":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="gratefulGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#2ECC71" />
              <stop offset="100%" stopColor="#27AE60" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#gratefulGradient)" />
          <path
            d="M8 8c0-1 1-2 2-2s2 1 2 2-1 2-2 2-2-1-2-2M14 8c0-1 1-2 2-2s2 1 2 2-1 2-2 2-2-1-2-2"
            fill="#FFF"
          />
          <path
            d="M8 14c1 2 2.5 3 4 3s3-1 4-3"
            stroke="#FFF"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <path
            d="M10 6l2 2 2-2M10 18l2-2 2 2"
            stroke="#FFF"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
          />
        </svg>
      );

    case "celebrating":
      return (
        <svg viewBox="0 0 24 24" style={svgStyle} className={className}>
          <defs>
            <linearGradient
              id="celebratingGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#E91E63" />
              <stop offset="100%" stopColor="#C2185B" />
            </linearGradient>
          </defs>
          <circle cx="12" cy="12" r="12" fill="url(#celebratingGradient)" />
          <circle cx="8.5" cy="9" r="1.5" fill="#FFF" />
          <circle cx="15.5" cy="9" r="1.5" fill="#FFF" />
          <path
            d="M7 14c1.5 2 3 3 5 3s3.5-1 5-3"
            stroke="#FFF"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="6" cy="6" r="1" fill="#FFD700" />
          <circle cx="18" cy="6" r="1" fill="#FFD700" />
          <circle cx="5" cy="10" r="0.8" fill="#FFD700" />
          <circle cx="19" cy="10" r="0.8" fill="#FFD700" />
          <circle cx="4" cy="14" r="0.6" fill="#FFD700" />
          <circle cx="20" cy="14" r="0.6" fill="#FFD700" />
        </svg>
      );

    default:
      return <span className={className}>😊</span>;
  }
};

export default CustomReactionEmoji;
