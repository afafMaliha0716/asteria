import { motion } from 'motion/react';

export function PixelMoon() {
  return (
    <motion.div
      className="fixed top-[16%] right-[20%] pointer-events-none z-10"
      animate={{
        y: [0, -12, 0],
      }}
      transition={{
        duration: 11,
        repeat: Infinity,
        ease: "easeInOut",
      }}
      style={{
        filter: 'none',
      }}
    >
      <svg width="135" height="135" viewBox="0 0 135 135" fill="none" style={{ imageRendering: 'pixelated' }}>
        {/* Pixel planet - solid color blocks */}
        <g>
          {/* Outline */}
          <rect x="50" y="18" width="6" height="6" fill="#c87848" />
          <rect x="56" y="18" width="6" height="6" fill="#c87848" />
          <rect x="62" y="18" width="6" height="6" fill="#c87848" />
          <rect x="68" y="18" width="6" height="6" fill="#c87848" />
          <rect x="74" y="18" width="6" height="6" fill="#c87848" />
          
          <rect x="38" y="24" width="6" height="6" fill="#c87848" />
          <rect x="92" y="24" width="6" height="6" fill="#c87848" />
          
          <rect x="32" y="30" width="6" height="6" fill="#c87848" />
          <rect x="98" y="30" width="6" height="6" fill="#c87848" />
          
          <rect x="26" y="36" width="6" height="36" fill="#c87848" />
          <rect x="98" y="36" width="6" height="36" fill="#c87848" />
          
          <rect x="32" y="72" width="6" height="6" fill="#c87848" />
          <rect x="92" y="72" width="6" height="6" fill="#c87848" />
          
          <rect x="38" y="78" width="6" height="6" fill="#c87848" />
          <rect x="86" y="78" width="6" height="6" fill="#c87848" />
          
          <rect x="50" y="84" width="6" height="6" fill="#c87848" />
          <rect x="56" y="84" width="6" height="6" fill="#c87848" />
          <rect x="62" y="84" width="6" height="6" fill="#c87848" />
          <rect x="68" y="84" width="6" height="6" fill="#c87848" />
          <rect x="74" y="84" width="6" height="6" fill="#c87848" />
          
          {/* Top section - light orange */}
          <rect x="44" y="24" width="48" height="6" fill="#f8b878" />
          <rect x="38" y="30" width="60" height="6" fill="#f8b878" />
          
          {/* Main body - medium orange */}
          <rect x="32" y="36" width="66" height="36" fill="#e8a868" />
          
          {/* Bottom section - darker orange */}
          <rect x="38" y="72" width="54" height="6" fill="#d89858" />
          <rect x="44" y="78" width="42" height="6" fill="#d89858" />
          
          {/* Crater details - solid dark spots */}
          <rect x="46" y="40" width="6" height="6" fill="#b87848" />
          <rect x="76" y="50" width="6" height="6" fill="#b87848" />
          <rect x="42" y="60" width="6" height="6" fill="#b87848" />
        </g>
      </svg>
    </motion.div>
  );
}
