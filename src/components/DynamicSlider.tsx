import { motion } from 'motion/react';
import { useState } from 'react';

interface DynamicSliderProps {
  label: string;
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
  delay: number;
}

export function DynamicSlider({ label, min, max, value, onChange, delay }: DynamicSliderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        delay,
        ease: [0.34, 1.56, 0.64, 1]
      }}
      style={{
        marginBottom: '24px',
      }}
    >
      {/* Label with typewriter effect */}
      <motion.label
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ 
          duration: 0.4, 
          delay: delay + 0.2,
        }}
        style={{
          fontFamily: '"Press Start 2P", "Courier New", monospace',
          fontSize: 'clamp(0.6rem, 1.1vw, 0.75rem)',
          color: '#00e5e5',
          letterSpacing: '0.08em',
          display: 'block',
          marginBottom: '12px',
          textShadow: isDragging ? '0 0 12px rgba(0, 229, 229, 0.6)' : '0 0 8px rgba(0, 229, 229, 0.3)',
          transition: 'text-shadow 0.3s ease',
        }}
      >
        {label}: {value}
      </motion.label>

      {/* Slider container */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ 
          duration: 0.4, 
          delay: delay + 0.3,
          ease: 'easeOut'
        }}
        style={{
          position: 'relative',
          width: '100%',
          height: '12px',
          background: 'rgba(26, 42, 90, 0.7)',
          boxShadow: `
            0 0 0 2px #1a4a6a,
            0 0 0 3px #0a2a4a,
            0 0 0 4px ${isDragging ? '#00e5e5' : '#2a5a7a'},
            ${isDragging ? '0 0 16px rgba(0, 229, 229, 0.4)' : 'none'},
            inset 0 2px 6px rgba(0, 0, 0, 0.4)
          `,
          transformOrigin: 'left',
          transition: 'box-shadow 0.3s ease',
        }}
      >
        {/* Progress fill */}
        <motion.div
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            height: '100%',
            background: isDragging 
              ? 'linear-gradient(90deg, #00e5e5 0%, #00f5f5 100%)'
              : 'linear-gradient(90deg, rgba(0, 229, 229, 0.4) 0%, rgba(0, 229, 229, 0.6) 100%)',
            boxShadow: isDragging ? '0 0 12px rgba(0, 229, 229, 0.5)' : 'none',
            transition: 'background 0.2s ease, box-shadow 0.2s ease',
          }}
        />

        {/* Slider thumb */}
        <motion.input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={() => setIsDragging(false)}
          onTouchStart={() => setIsDragging(true)}
          onTouchEnd={() => setIsDragging(false)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: 'pointer',
            zIndex: 2,
          }}
        />

        {/* Visual thumb */}
        <motion.div
          animate={{ 
            left: `calc(${percentage}% - 10px)`,
            boxShadow: isDragging
              ? '0 0 0 3px #00e5e5, 0 0 20px rgba(0, 229, 229, 0.7)'
              : '0 0 0 2px #00e5e5, 0 0 12px rgba(0, 229, 229, 0.4)'
          }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          style={{
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            width: '20px',
            height: '20px',
            background: isDragging
              ? '#00f5f5'
              : 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 100%)',
            border: '2px solid #1a3a5a',
            pointerEvents: 'none',
            zIndex: 1,
          }}
        >
          {/* Pixel glow effect */}
          <motion.div
            animate={{
              opacity: isDragging ? [0.6, 1, 0.6] : 0.4,
              scale: isDragging ? [1, 1.3, 1] : 1,
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            style={{
              position: 'absolute',
              inset: '-4px',
              background: 'radial-gradient(circle, rgba(0, 229, 229, 0.6) 0%, transparent 70%)',
              pointerEvents: 'none',
            }}
          />
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
