export function OrbitalLines() {
  return (
    <div className="fixed inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
      <svg
        className="absolute w-full h-full"
        viewBox="0 0 1000 1000"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Orbital rings */}
        <ellipse
          cx="500"
          cy="500"
          rx="350"
          ry="180"
          stroke="rgba(255, 255, 255, 0.08)"
          strokeWidth="1"
          fill="none"
          className="opacity-60"
        />
        <ellipse
          cx="500"
          cy="500"
          rx="280"
          ry="140"
          stroke="rgba(255, 255, 255, 0.06)"
          strokeWidth="1"
          fill="none"
          className="opacity-50"
          transform="rotate(-25 500 500)"
        />
        <ellipse
          cx="500"
          cy="500"
          rx="420"
          ry="220"
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth="1"
          fill="none"
          className="opacity-40"
          transform="rotate(15 500 500)"
        />
        
        {/* Arc paths */}
        <path
          d="M 200 500 Q 350 300, 500 250"
          stroke="rgba(255, 255, 255, 0.07)"
          strokeWidth="1.5"
          fill="none"
          className="opacity-50"
        />
        <path
          d="M 800 500 Q 650 700, 500 750"
          stroke="rgba(255, 255, 255, 0.07)"
          strokeWidth="1.5"
          fill="none"
          className="opacity-50"
        />
        
        {/* Decorative small glowing orbs on orbits - navy themed */}
        <circle cx="350" cy="380" r="3" fill="rgba(203, 213, 225, 0.5)">
          <animate
            attributeName="opacity"
            values="0.3;0.7;0.3"
            dur="4s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="650" cy="620" r="3" fill="rgba(226, 232, 240, 0.5)">
          <animate
            attributeName="opacity"
            values="0.4;0.8;0.4"
            dur="5s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="300" cy="550" r="2.5" fill="rgba(241, 245, 249, 0.4)">
          <animate
            attributeName="opacity"
            values="0.2;0.6;0.2"
            dur="3.5s"
            repeatCount="indefinite"
          />
        </circle>
        <circle cx="700" cy="450" r="2.5" fill="rgba(241, 245, 249, 0.4)">
          <animate
            attributeName="opacity"
            values="0.3;0.7;0.3"
            dur="4.5s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>
    </div>
  );
}
