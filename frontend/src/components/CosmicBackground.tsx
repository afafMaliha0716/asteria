export function CosmicBackground() {
  return (
    <div className="fixed inset-0 -z-10">
      {/* Main pixelated night sky background - dreamy navy, indigo, violet */}
      <div 
        className="absolute inset-0"
        style={{
          background: `
            radial-gradient(ellipse at 30% 35%, #1a2545 0%, transparent 50%),
            radial-gradient(ellipse at 70% 40%, #251a40 0%, transparent 55%),
            radial-gradient(ellipse at 50% 45%, #16203a 0%, #0f1628 35%, #0b1020 75%, #090e1a 100%)
          `,
          imageRendering: 'pixelated',
        }}
      />
      
      {/* Constellation lines and curved orbit paths */}
      <div className="absolute inset-0 opacity-[0.25]">
        <svg className="w-full h-full" viewBox="0 0 1000 1000" preserveAspectRatio="none">
          {/* Faint curved orbit lines near top corners */}
          <path 
            d="M 50 100 Q 150 80, 250 100 T 400 120" 
            stroke="#4a5a7f" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="3,7"
          />
          <path 
            d="M 950 120 Q 850 100, 750 120 T 600 140" 
            stroke="#4a5a7f" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="3,7"
          />
          
          {/* Dotted curved orbits centered around title area */}
          <ellipse 
            cx="500" 
            cy="350" 
            rx="450" 
            ry="300" 
            stroke="#3a4a70" 
            strokeWidth="1.5" 
            fill="none"
            strokeDasharray="4,9"
          />
          <ellipse 
            cx="500" 
            cy="350" 
            rx="370" 
            ry="240" 
            stroke="#4a5a80" 
            strokeWidth="1.2" 
            fill="none"
            strokeDasharray="3,8"
          />
          <ellipse 
            cx="500" 
            cy="350" 
            rx="290" 
            ry="190" 
            stroke="#2a3a60" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="5,10"
          />
          
          {/* Constellation connection lines */}
          <path 
            d="M 200 250 L 280 220 L 320 280 L 380 240" 
            stroke="#4a5a80" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="2,6"
            opacity="0.6"
          />
          <path 
            d="M 650 300 L 720 280 L 760 330 L 800 310" 
            stroke="#4a5a80" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="2,6"
            opacity="0.6"
          />
          <path 
            d="M 150 600 L 220 580 L 250 640" 
            stroke="#3a4a70" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="2,6"
            opacity="0.5"
          />
          <path 
            d="M 800 650 L 850 620 L 900 660 L 880 700" 
            stroke="#3a4a70" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="2,6"
            opacity="0.5"
          />
          
          {/* Flowing curved paths for depth */}
          <path 
            d="M 100 380 Q 300 260, 500 320 T 900 400" 
            stroke="#3a4a70" 
            strokeWidth="1.5" 
            fill="none"
            strokeDasharray="6,11"
          />
          <path 
            d="M 150 530 Q 350 430, 550 490 T 950 580" 
            stroke="#2a3a60" 
            strokeWidth="1.2" 
            fill="none"
            strokeDasharray="5,10"
          />
          <path 
            d="M 50 280 Q 250 180, 450 240 T 850 320" 
            stroke="#4a5a80" 
            strokeWidth="1" 
            fill="none"
            strokeDasharray="4,9"
          />
          
          {/* Additional curved arc details */}
          <path 
            d="M 300 150 Q 400 120, 500 150" 
            stroke="#4a5a7f" 
            strokeWidth="0.8" 
            fill="none"
            strokeDasharray="3,7"
          />
          <path 
            d="M 650 750 Q 750 720, 850 750" 
            stroke="#3a4a70" 
            strokeWidth="0.8" 
            fill="none"
            strokeDasharray="3,7"
          />
        </svg>
      </div>
      

    </div>
  );
}
