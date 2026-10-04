import { motion } from 'motion/react';

export function PixelShootingStar() {
  return (
    <>
      {/* First shooting star - diagonal with pixel trail */}
      <motion.div
        className="fixed pointer-events-none z-10"
        initial={{
          x: '10vw',
          y: '15vh',
          opacity: 0,
        }}
        animate={{
          x: ['10vw', '50vw'],
          y: ['15vh', '55vh'],
          opacity: [0, 0.9, 1, 0.7, 0],
        }}
        transition={{
          duration: 2.8,
          delay: 4,
          repeat: Infinity,
          repeatDelay: 20,
          ease: "linear",
        }}
      >
        <svg width="140" height="70" viewBox="0 0 140 70" fill="none" style={{ imageRendering: 'pixelated' }}>
          <g>
            {/* Star head - solid yellow */}
            <rect x="115" y="12" width="5" height="5" fill="#f8e8a8" />
            <rect x="120" y="12" width="5" height="5" fill="#fff8d8" />
            <rect x="115" y="17" width="5" height="5" fill="#fff8d8" />
            <rect x="120" y="17" width="5" height="5" fill="#f8e8a8" />
            
            {/* Pixel trail - solid blocks fading */}
            <rect x="108" y="18" width="7" height="4" fill="#f8e8a8" opacity="0.9" />
            <rect x="101" y="22" width="7" height="4" fill="#f8e8a8" opacity="0.75" />
            <rect x="94" y="26" width="7" height="4" fill="#e8d898" opacity="0.6" />
            <rect x="87" y="30" width="6" height="3" fill="#d8c888" opacity="0.45" />
            <rect x="81" y="33" width="6" height="3" fill="#c8b878" opacity="0.3" />
            <rect x="75" y="36" width="6" height="3" fill="#b8a868" opacity="0.2" />
          </g>
        </svg>
      </motion.div>

      {/* Second shooting star - different angle, lighter blue tone */}
      <motion.div
        className="fixed pointer-events-none z-10"
        initial={{
          x: '70vw',
          y: '10vh',
          opacity: 0,
        }}
        animate={{
          x: ['70vw', '92vw'],
          y: ['10vh', '32vh'],
          opacity: [0, 0.8, 0.95, 0.6, 0],
        }}
        transition={{
          duration: 2.2,
          delay: 14,
          repeat: Infinity,
          repeatDelay: 20,
          ease: "linear",
        }}
      >
        <svg width="100" height="50" viewBox="0 0 100 50" fill="none" style={{ imageRendering: 'pixelated' }}>
          <g>
            {/* Small star head - solid blue */}
            <rect x="78" y="10" width="4" height="4" fill="#b8d0f0" />
            <rect x="82" y="10" width="4" height="4" fill="#d8e8ff" />
            <rect x="78" y="14" width="4" height="4" fill="#d8e8ff" />
            <rect x="82" y="14" width="4" height="4" fill="#b8d0f0" />
            
            {/* Trail - solid blocks fading */}
            <rect x="72" y="15" width="6" height="3" fill="#b8d0f0" opacity="0.85" />
            <rect x="66" y="18" width="6" height="3" fill="#a8c0e0" opacity="0.65" />
            <rect x="60" y="21" width="5" height="3" fill="#98b0d0" opacity="0.45" />
            <rect x="55" y="24" width="5" height="2" fill="#88a0c0" opacity="0.25" />
          </g>
        </svg>
      </motion.div>
    </>
  );
}
