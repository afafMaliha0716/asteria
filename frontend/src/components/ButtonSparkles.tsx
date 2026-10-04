import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

interface Sparkle {
  id: number;
  x: number;
  y: number;
  delay: number;
}

export function ButtonSparkles({ show }: { show: boolean }) {
  const [sparkles, setSparkles] = useState<Sparkle[]>([]);

  useEffect(() => {
    if (show) {
      // Generate sparkle particles
      const newSparkles: Sparkle[] = [];
      for (let i = 0; i < 8; i++) {
        newSparkles.push({
          id: i,
          x: (Math.random() - 0.5) * 120,
          y: (Math.random() - 0.5) * 80,
          delay: i * 0.05,
        });
      }
      setSparkles(newSparkles);
    }
  }, [show]);

  if (!show) return null;

  return (
    <div className="absolute inset-0 pointer-events-none">
      {sparkles.map((sparkle) => (
        <motion.div
          key={sparkle.id}
          className="absolute top-1/2 left-1/2"
          initial={{
            x: 0,
            y: 0,
            opacity: 1,
            scale: 1,
          }}
          animate={{
            x: sparkle.x,
            y: sparkle.y,
            opacity: 0,
            scale: 0.3,
          }}
          transition={{
            duration: 1,
            delay: sparkle.delay,
            ease: "easeOut",
          }}
        >
          {/* Tiny pixel star sparkle */}
          <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
            <rect x="3" y="0" width="2" height="8" fill="#f8ecd7" />
            <rect x="0" y="3" width="8" height="2" fill="#f8ecd7" />
          </svg>
        </motion.div>
      ))}
    </div>
  );
}
