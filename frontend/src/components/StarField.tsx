import { useEffect, useState } from 'react';

interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  animationDelay: number;
  animationDuration: number;
  opacity: number;
  moveX: number;
  moveY: number;
  moveDuration: number;
}

export function StarField() {
  const [stars, setStars] = useState<Star[]>([]);

  useEffect(() => {
    // Generate stars
    const newStars: Star[] = [];
    
    // Small twinkling stars (many)
    for (let i = 0; i < 120; i++) {
      newStars.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 2 + 1,
        animationDelay: Math.random() * 5,
        animationDuration: Math.random() * 2 + 1.5, // Faster twinkling
        opacity: Math.random() * 0.4 + 0.1, // Lower min opacity for more dramatic effect
        moveX: (Math.random() - 0.5) * 8, // More noticeable horizontal drift
        moveY: (Math.random() - 0.5) * 8, // More noticeable vertical drift
        moveDuration: Math.random() * 15 + 20, // Slightly faster movement
      });
    }
    
    // Larger glowing stars (fewer)
    for (let i = 120; i < 135; i++) {
      newStars.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 3,
        animationDelay: Math.random() * 4,
        animationDuration: Math.random() * 3 + 2, // Faster glow
        opacity: Math.random() * 0.3 + 0.3, // Lower min opacity
        moveX: (Math.random() - 0.5) * 10, // More movement
        moveY: (Math.random() - 0.5) * 10,
        moveDuration: Math.random() * 20 + 25,
      });
    }
    
    setStars(newStars);
  }, []);

  return (
    <>
      <style>{`
        @keyframes twinkle {
          0%, 100% { opacity: var(--opacity-min); transform: scale(1); }
          50% { opacity: 1; transform: scale(1.2); }
        }
        
        @keyframes glow {
          0%, 100% { opacity: var(--opacity-min); filter: blur(0px); }
          50% { opacity: 1; filter: blur(1px); }
        }
        
        @keyframes move-x {
          0% { transform: translateX(0); }
          100% { transform: translateX(var(--move-x)); }
        }
        
        @keyframes move-y {
          0% { transform: translateY(0); }
          100% { transform: translateY(var(--move-y)); }
        }
      `}</style>
      
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {stars.map((star) => (
          <div
            key={star.id}
            className="absolute rounded-full bg-slate-100"
            style={{
              left: `${star.x}%`,
              top: `${star.y}%`,
              width: `${star.size}px`,
              height: `${star.size}px`,
              animation: `
                ${star.size > 3 ? 'glow' : 'twinkle'} var(--duration) infinite ease-in-out,
                move-x var(--move-duration) infinite ease-in-out alternate,
                move-y var(--move-duration-offset) infinite ease-in-out alternate
              `,
              animationDelay: `${star.animationDelay}s`,
              // @ts-ignore
              '--duration': `${star.animationDuration}s`,
              '--opacity-min': star.opacity,
              '--move-x': `${star.moveX}vw`,
              '--move-y': `${star.moveY}vh`,
              '--move-duration': `${star.moveDuration}s`,
              '--move-duration-offset': `${star.moveDuration * 1.3}s`,
              opacity: star.opacity,
              boxShadow: star.size > 3 ? `0 0 ${star.size * 2}px rgba(241, 245, 249, 0.6)` : 'none',
            }}
          />
        ))}
      </div>
    </>
  );
}
