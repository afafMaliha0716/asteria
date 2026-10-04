import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

interface ShootingStar {
  id: number;
  startX: number;
  startY: number;
  delay: number;
  angle: number;
}

export function ShootingStars() {
  const [stars, setStars] = useState<ShootingStar[]>([]);

  useEffect(() => {
    const shootingStars: ShootingStar[] = [];
    
    // Create a few shooting stars that will animate
    for (let i = 0; i < 4; i++) {
      shootingStars.push({
        id: i,
        startX: Math.random() * 60 + 10, // Start from left-center area
        startY: Math.random() * 40, // Keep them in upper portion
        delay: Math.random() * 8 + i * 5, // Stagger them more
        angle: Math.random() * 30 - 60, // Angle between -60 and -30 degrees
      });
    }
    
    setStars(shootingStars);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {stars.map((star) => (
        <motion.div
          key={star.id}
          className="absolute opacity-50"
          initial={{
            x: `${star.startX}vw`,
            y: `${star.startY}vh`,
            opacity: 0,
          }}
          animate={{
            x: [`${star.startX}vw`, `${star.startX + 50}vw`],
            y: [`${star.startY}vh`, `${star.startY + 35}vh`],
            opacity: [0, 0.3, 0.6, 0.4, 0],
          }}
          transition={{
            duration: 4,
            delay: star.delay,
            repeat: Infinity,
            repeatDelay: 18,
            ease: "linear",
          }}
        >
          {/* Shooting star trail */}
          <div
            className="relative"
            style={{
              width: '120px',
              height: '1.5px',
              background: 'linear-gradient(90deg, transparent 0%, rgba(241, 245, 249, 0.4) 40%, rgba(241, 245, 249, 0.8) 100%)',
              transform: `rotate(${star.angle}deg)`,
              boxShadow: '0 0 4px rgba(241, 245, 249, 0.3)',
            }}
          >
            {/* Head of shooting star */}
            <div
              className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-slate-100"
              style={{
                boxShadow: '0 0 8px rgba(241, 245, 249, 0.6), 0 0 16px rgba(241, 245, 249, 0.4)',
              }}
            />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
