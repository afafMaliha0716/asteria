import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  type: 'burst' | 'cross' | 'plus' | 'dot' | 'small' | 'tiny';
  animationDelay: number;
  animationDuration: number;
  color: string;
  brightness: number;
}

export function PixelStars() {
  const [stars, setStars] = useState<Star[]>([]);

  useEffect(() => {
    const newStars: Star[] = [];
    
    // Generate varied pixel stars with natural density (not grid)
    for (let i = 0; i < 150; i++) {
      const randType = Math.random();
      const randColor = Math.random();
      
      // Color distribution: pale yellow, light blue, lavender, soft white
      let color;
      if (randColor > 0.75) {
        color = '#f8f0d0'; // Soft pale yellow
      } else if (randColor > 0.6) {
        color = '#f4e8b8'; // Pale yellow
      } else if (randColor > 0.45) {
        color = '#e8f0f8'; // Very pale blue/white
      } else if (randColor > 0.3) {
        color = '#c8dce8'; // Light blue
      } else if (randColor > 0.18) {
        color = '#d8d0e8'; // Lavender
      } else {
        color = '#e8d8f0'; // Soft violet
      }
      
      // Varied sizes - some much smaller, some medium, few large
      let baseSize;
      if (Math.random() > 0.95) {
        baseSize = 4; // Large
      } else if (Math.random() > 0.8) {
        baseSize = 3; // Medium
      } else {
        baseSize = 2; // Small
      }
      
      newStars.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: baseSize,
        type: randType > 0.96 ? 'burst' : randType > 0.91 ? 'cross' : randType > 0.7 ? 'plus' : randType > 0.45 ? 'dot' : randType > 0.25 ? 'small' : 'tiny',
        animationDelay: Math.random() * 10,
        animationDuration: Math.random() * 5 + 3,
        color: color,
        brightness: Math.random() * 0.65 + 0.35, // 0.35 to 1.0
      });
    }
    
    setStars(newStars);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {stars.map((star) => (
        <motion.div
          key={star.id}
          className="absolute"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            imageRendering: 'pixelated',
          }}
          animate={{
            opacity: star.type === 'burst' || star.type === 'cross'
              ? [star.brightness * 0.5, star.brightness, star.brightness * 0.5]
              : [star.brightness * 0.25, star.brightness * 0.8, star.brightness * 0.25],
          }}
          transition={{
            duration: star.animationDuration,
            delay: star.animationDelay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {star.type === 'burst' ? (
            // Solid burst - no glow
            <svg
              width={star.size * 8}
              height={star.size * 8}
              viewBox="0 0 24 24"
              fill="none"
            >
              <rect x="10" y="2" width="4" height="20" fill={star.color} />
              <rect x="2" y="10" width="20" height="4" fill={star.color} />
              <rect x="6" y="6" width="2" height="12" fill={star.color} />
              <rect x="16" y="6" width="2" height="12" fill={star.color} />
              <rect x="6" y="6" width="12" height="2" fill={star.color} />
              <rect x="6" y="16" width="12" height="2" fill={star.color} />
            </svg>
          ) : star.type === 'cross' ? (
            // Solid cross
            <svg
              width={star.size * 7}
              height={star.size * 7}
              viewBox="0 0 21 21"
              fill="none"
            >
              <rect x="8" y="2" width="5" height="17" fill={star.color} />
              <rect x="2" y="8" width="17" height="5" fill={star.color} />
            </svg>
          ) : star.type === 'plus' ? (
            // Solid plus
            <svg
              width={star.size * 5}
              height={star.size * 5}
              viewBox="0 0 15 15"
              fill="none"
            >
              <rect x="6" y="1" width="3" height="13" fill={star.color} />
              <rect x="1" y="6" width="13" height="3" fill={star.color} />
            </svg>
          ) : star.type === 'dot' ? (
            <div
              style={{
                width: `${star.size * 2}px`,
                height: `${star.size * 2}px`,
                backgroundColor: star.color,
              }}
            />
          ) : star.type === 'small' ? (
            <div
              style={{
                width: `${star.size}px`,
                height: `${star.size}px`,
                backgroundColor: star.color,
              }}
            />
          ) : (
            <div
              style={{
                width: '2px',
                height: '2px',
                backgroundColor: star.color,
              }}
            />
          )}
        </motion.div>
      ))}
    </div>
  );
}
