/**
 * Animation Utilities
 * Provides reusable animation classes and keyframes
 */

export const animations = {
  // Fade animations
  fadeIn: 'fadeIn 0.3s ease-in-out',
  fadeOut: 'fadeOut 0.3s ease-in-out',
  fadeInUp: 'fadeInUp 0.4s ease-out',
  fadeInDown: 'fadeInDown 0.4s ease-out',
  fadeInLeft: 'fadeInLeft 0.4s ease-out',
  fadeInRight: 'fadeInRight 0.4s ease-out',

  // Scale animations
  scaleIn: 'scaleIn 0.2s ease-out',
  scaleOut: 'scaleOut 0.2s ease-in',
  pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',

  // Slide animations
  slideInUp: 'slideInUp 0.3s ease-out',
  slideInDown: 'slideInDown 0.3s ease-out',
  slideInLeft: 'slideInLeft 0.3s ease-out',
  slideInRight: 'slideInRight 0.3s ease-out',
  slideOutUp: 'slideOutUp 0.3s ease-in',
  slideOutDown: 'slideOutDown 0.3s ease-in',
  slideOutLeft: 'slideOutLeft 0.3s ease-in',
  slideOutRight: 'slideOutRight 0.3s ease-in',

  // Rotation animations
  spin: 'spin 1s linear infinite',
  rotateIn: 'rotateIn 0.4s ease-out',
  rotateOut: 'rotateOut 0.4s ease-in',

  // Bounce animations
  bounce: 'bounce 1s infinite',
  bounceIn: 'bounceIn 0.6s ease-out',
  bounceOut: 'bounceOut 0.6s ease-in',

  // Shake animations
  shake: 'shake 0.8s ease-in-out',
  headShake: 'headShake 1s ease-in-out',

  // Loading animations
  loading: 'pulse 1.5s ease-in-out infinite',
  skeleton: 'skeleton 1.5s ease-in-out infinite',
  shimmer: 'shimmer 2s linear infinite',

  // Hover effects
  float: 'float 3s ease-in-out infinite',
  glow: 'glow 2s ease-in-out infinite alternate',

  // Attention seeking
  attention: 'attention 1s ease-in-out',
  wiggle: 'wiggle 0.8s ease-in-out',
} as const;

export const keyframes = `
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes fadeOut {
    from { opacity: 1; }
    to { opacity: 0; }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInLeft {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes fadeInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes scaleIn {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes scaleOut {
    from {
      opacity: 1;
      transform: scale(1);
    }
    to {
      opacity: 0;
      transform: scale(0.8);
    }
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  @keyframes slideInUp {
    from {
      transform: translateY(100%);
    }
    to {
      transform: translateY(0);
    }
  }

  @keyframes slideInDown {
    from {
      transform: translateY(-100%);
    }
    to {
      transform: translateY(0);
    }
  }

  @keyframes slideInLeft {
    from {
      transform: translateX(-100%);
    }
    to {
      transform: translateX(0);
    }
  }

  @keyframes slideInRight {
    from {
      transform: translateX(100%);
    }
    to {
      transform: translateX(0);
    }
  }

  @keyframes slideOutUp {
    from {
      transform: translateY(0);
    }
    to {
      transform: translateY(-100%);
    }
  }

  @keyframes slideOutDown {
    from {
      transform: translateY(0);
    }
    to {
      transform: translateY(100%);
    }
  }

  @keyframes slideOutLeft {
    from {
      transform: translateX(0);
    }
    to {
      transform: translateX(-100%);
    }
  }

  @keyframes slideOutRight {
    from {
      transform: translateX(0);
    }
    to {
      transform: translateX(100%);
    }
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes rotateIn {
    from {
      opacity: 0;
      transform: rotate(-180deg);
    }
    to {
      opacity: 1;
      transform: rotate(0deg);
    }
  }

  @keyframes rotateOut {
    from {
      opacity: 1;
      transform: rotate(0deg);
    }
    to {
      opacity: 0;
      transform: rotate(180deg);
    }
  }

  @keyframes bounce {
    0%, 100% {
      transform: translateY(-25%);
      animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
    }
    50% {
      transform: none;
      animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
    }
  }

  @keyframes bounceIn {
    0% {
      opacity: 0;
      transform: scale(0.3);
    }
    50% {
      opacity: 1;
      transform: scale(1.05);
    }
    70% {
      transform: scale(0.9);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes bounceOut {
    20% {
      transform: scale(0.9);
    }
    50%, 55% {
      opacity: 1;
      transform: scale(1.1);
    }
    to {
      opacity: 0;
      transform: scale(0.3);
    }
  }

  @keyframes shake {
    0%, 100% {
      transform: translateX(0);
    }
    10%, 30%, 50%, 70%, 90% {
      transform: translateX(-5px);
    }
    20%, 40%, 60%, 80% {
      transform: translateX(5px);
    }
  }

  @keyframes headShake {
    0% {
      transform: translateX(0);
    }
    6.5% {
      transform: translateX(-6px) rotateY(-9deg);
    }
    18.5% {
      transform: translateX(5px) rotateY(7deg);
    }
    31.5% {
      transform: translateX(-3px) rotateY(-5deg);
    }
    43.5% {
      transform: translateX(2px) rotateY(3deg);
    }
    50% {
      transform: translateX(0);
    }
  }

  @keyframes skeleton {
    0% {
      background-position: -200px 0;
    }
    100% {
      background-position: calc(200px + 100%) 0;
    }
  }

  @keyframes shimmer {
    0% {
      background-position: -1000px 0;
    }
    100% {
      background-position: 1000px 0;
    }
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  @keyframes glow {
    from {
      box-shadow: 0 0 20px var(--color-primary-light);
    }
    to {
      box-shadow: 0 0 30px var(--color-primary), 0 0 40px var(--color-primary);
    }
  }

  @keyframes attention {
    0% {
      transform: scale(1);
    }
    15% {
      transform: scale(1.1);
    }
    30% {
      transform: scale(1);
    }
    45% {
      transform: scale(1.05);
    }
    60% {
      transform: scale(1);
    }
    75% {
      transform: scale(1.02);
    }
    100% {
      transform: scale(1);
    }
  }

  @keyframes wiggle {
    0%, 7% {
      transform: rotateZ(0);
    }
    15% {
      transform: rotateZ(-15deg);
    }
    20% {
      transform: rotateZ(10deg);
    }
    25% {
      transform: rotateZ(-10deg);
    }
    30% {
      transform: rotateZ(6deg);
    }
    35% {
      transform: rotateZ(-4deg);
    }
    40%, 100% {
      transform: rotateZ(0);
    }
  }
`;

/**
 * Easing functions
 */
export const easings = {
  // Standard easing
  ease: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  easeIn: 'cubic-bezier(0.42, 0, 1, 1)',
  easeOut: 'cubic-bezier(0, 0, 0.58, 1)',
  easeInOut: 'cubic-bezier(0.42, 0, 0.58, 1)',

  // Material Design easing
  standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
  decelerate: 'cubic-bezier(0, 0, 0.2, 1)',
  accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',

  // Bounce easing
  bounceIn: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  bounceOut: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',

  // Elastic easing
  elasticIn: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
  elasticOut: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',

  // Back easing
  backIn: 'cubic-bezier(0.36, 0, 0.66, -0.56)',
  backOut: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
} as const;

/**
 * Duration presets
 */
export const durations = {
  fastest: '0.1s',
  fast: '0.2s',
  normal: '0.3s',
  slow: '0.5s',
  slowest: '0.8s',
} as const;

/**
 * Animation utility classes
 */
export const animationClasses = {
  // Basic animations
  'animate-fade-in': `animation: ${animations.fadeIn}`,
  'animate-fade-out': `animation: ${animations.fadeOut}`,
  'animate-fade-in-up': `animation: ${animations.fadeInUp}`,
  'animate-fade-in-down': `animation: ${animations.fadeInDown}`,
  'animate-fade-in-left': `animation: ${animations.fadeInLeft}`,
  'animate-fade-in-right': `animation: ${animations.fadeInRight}`,

  'animate-scale-in': `animation: ${animations.scaleIn}`,
  'animate-scale-out': `animation: ${animations.scaleOut}`,
  'animate-pulse': `animation: ${animations.pulse}`,

  'animate-slide-in-up': `animation: ${animations.slideInUp}`,
  'animate-slide-in-down': `animation: ${animations.slideInDown}`,
  'animate-slide-in-left': `animation: ${animations.slideInLeft}`,
  'animate-slide-in-right': `animation: ${animations.slideInRight}`,

  'animate-spin': `animation: ${animations.spin}`,
  'animate-bounce': `animation: ${animations.bounce}`,
  'animate-shake': `animation: ${animations.shake}`,

  // Loading states
  'animate-loading': `animation: ${animations.loading}`,
  'animate-skeleton': `animation: ${animations.skeleton}`,
  'animate-shimmer': `animation: ${animations.shimmer}`,

  // Hover effects
  'animate-float': `animation: ${animations.float}`,
  'animate-glow': `animation: ${animations.glow}`,

  // Attention seeking
  'animate-attention': `animation: ${animations.attention}`,
  'animate-wiggle': `animation: ${animations.wiggle}`,
} as const;

/**
 * Skeleton loading styles
 */
export const skeletonStyles = {
  base: `
    background: linear-gradient(
      90deg,
      var(--color-gray-200) 0%,
      var(--color-gray-300) 50%,
      var(--color-gray-200) 100%
    );
    background-size: 200px 100%;
    animation: ${animations.skeleton};
  `,
  dark: `
    background: linear-gradient(
      90deg,
      var(--color-gray-700) 0%,
      var(--color-gray-600) 50%,
      var(--color-gray-700) 100%
    );
    background-size: 200px 100%;
    animation: ${animations.skeleton};
  `,
} as const;

/**
 * Transition utilities
 */
export const transitions = {
  none: 'transition: none',
  all: `transition: all ${durations.normal} ${easings.standard}`,
  colors: `transition: color ${durations.normal} ${easings.standard}, background-color ${durations.normal} ${easings.standard}, border-color ${durations.normal} ${easings.standard}`,
  opacity: `transition: opacity ${durations.normal} ${easings.standard}`,
  shadow: `transition: box-shadow ${durations.normal} ${easings.standard}`,
  transform: `transition: transform ${durations.normal} ${easings.standard}`,
} as const;

/**
 * Animation state management
 */
export type AnimationState = 'idle' | 'entering' | 'entered' | 'exiting' | 'exited';

export interface AnimationConfig {
  duration?: keyof typeof durations | string;
  easing?: keyof typeof easings | string;
  delay?: string;
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
  iterationCount?: number | 'infinite';
}

export const createAnimation = (
  keyframeName: string,
  config: AnimationConfig = {}
): string => {
  const {
    duration = 'normal',
    easing = 'standard',
    delay = '0s',
    fillMode = 'both',
    iterationCount = 1,
  } = config;

  const durationValue = duration in durations ? durations[duration as keyof typeof durations] : duration;
  const easingValue = easing in easings ? easings[easing as keyof typeof easings] : easing;

  return `${keyframeName} ${durationValue} ${easingValue} ${delay} ${iterationCount} ${fillMode}`;
};

/**
 * CSS-in-JS animation helper
 */
export const cssAnimation = (animationName: keyof typeof animations): string => {
  return animations[animationName];
};

/**
 * Stagger animation utility for lists
 */
export const staggerAnimation = (
  index: number,
  baseDelay = 0.1,
  animationName: keyof typeof animations = 'fadeInUp'
): React.CSSProperties => {
  return {
    animation: animations[animationName],
    animationDelay: `${index * baseDelay}s`,
    animationFillMode: 'both',
  };
};

import React from 'react';