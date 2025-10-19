import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Upload, Star, Play } from 'lucide-react';

interface EditPageProps {
  onRefineWorld: () => void;
  onNewProject: () => void;
  onSaveProject: () => void;
}

interface CursorTrail {
  id: number;
  x: number;
  y: number;
}

interface BackgroundStar {
  id: number;
  x: number;
  y: number;
  size: number;
  delay: number;
}

export default function EditPage({ onRefineWorld, onNewProject, onSaveProject }: EditPageProps) {
  const [cursorTrails, setCursorTrails] = useState<CursorTrail[]>([]);
  const [hoverSparkles, setHoverSparkles] = useState<{ id: number; x: number; y: number }[]>([]);
  const [promptValue, setPromptValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [characterAnim, setCharacterAnim] = useState(false);
  const [enemyAnim, setEnemyAnim] = useState(false);
  const trailIdRef = useRef(0);
  const sparkleIdRef = useRef(0);

  // Background twinkling stars
  const [bgStars] = useState<BackgroundStar[]>(() => 
    Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 1,
      delay: Math.random() * 3,
    }))
  );

  // Cursor trail effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const id = trailIdRef.current++;
      setCursorTrails(prev => [...prev, { id, x: e.clientX, y: e.clientY }]);
      
      setTimeout(() => {
        setCursorTrails(prev => prev.filter(t => t.id !== id));
      }, 300);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Character idle animation every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      setCharacterAnim(true);
      setTimeout(() => setCharacterAnim(false), 1000);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  // Enemy idle animation every 30s
  useEffect(() => {
    const interval = setInterval(() => {
      setEnemyAnim(true);
      setTimeout(() => setEnemyAnim(false), 1000);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleHover = (e: React.MouseEvent) => {
    const id = sparkleIdRef.current++;
    const rect = e.currentTarget.getBoundingClientRect();
    setHoverSparkles(prev => [...prev, { 
      id, 
      x: e.clientX - rect.left, 
      y: e.clientY - rect.top 
    }]);
    
    setTimeout(() => {
      setHoverSparkles(prev => prev.filter(s => s.id !== id));
    }, 500);
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'linear-gradient(180deg, #030B1A 0%, #0E1735 100%)',
        overflow: 'hidden',
      }}
    >
      {/* Background stars */}
      {bgStars.map(star => (
        <motion.div
          key={star.id}
          initial={{ opacity: 0.3 }}
          animate={{ 
            opacity: [0.3, 1, 0.3],
            x: [star.x + '%', (star.x - 0.5) + '%'],
          }}
          transition={{
            opacity: { duration: 2 + star.delay, repeat: Infinity, ease: 'easeInOut' },
            x: { duration: 60, repeat: Infinity, ease: 'linear' },
          }}
          style={{
            position: 'absolute',
            left: star.x + '%',
            top: star.y + '%',
            width: star.size + 'px',
            height: star.size + 'px',
            backgroundColor: '#00e5e5',
            borderRadius: '50%',
            boxShadow: '0 0 4px rgba(0, 229, 229, 0.8)',
          }}
        />
      ))}

      {/* Cursor trails */}
      <AnimatePresence>
        {cursorTrails.map(trail => (
          <motion.div
            key={trail.id}
            initial={{ opacity: 0.6, scale: 1 }}
            animate={{ opacity: 0, scale: 0.5 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              position: 'fixed',
              left: trail.x - 2,
              top: trail.y - 2,
              width: '4px',
              height: '4px',
              backgroundColor: '#00e5e5',
              borderRadius: '50%',
              pointerEvents: 'none',
              zIndex: 9999,
            }}
          />
        ))}
      </AnimatePresence>

      {/* Header bar */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        style={{
          position: 'relative',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '20px 40px',
          zIndex: 50,
        }}
      >
        <div style={{
          fontFamily: '"Press Start 2P", "Courier New", monospace',
          fontSize: '1.2rem',
          color: '#E6C97E',
          textShadow: '0 0 20px rgba(230, 201, 126, 0.6)',
          letterSpacing: '0.1em',
        }}>
          ASTERIA
        </div>
        
        <div style={{ display: 'flex', gap: '20px' }}>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onNewProject}
            onMouseEnter={handleHover}
            style={{
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              fontSize: '0.7rem',
              padding: '10px 20px',
              background: 'transparent',
              border: '2px solid #E6C97E',
              color: '#E6C97E',
              cursor: 'pointer',
              boxShadow: '0 0 10px rgba(230, 201, 126, 0.3)',
              transition: 'all 0.2s',
            }}
          >
            New Project
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onSaveProject}
            onMouseEnter={handleHover}
            style={{
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              fontSize: '0.7rem',
              padding: '10px 20px',
              background: 'transparent',
              border: '2px solid #00e5e5',
              color: '#00e5e5',
              cursor: 'pointer',
              boxShadow: '0 0 10px rgba(0, 229, 229, 0.3)',
              transition: 'all 0.2s',
            }}
          >
            Save Project
          </motion.button>
        </div>
      </motion.header>

      {/* Main content area */}
      <div style={{
        display: 'flex',
        gap: '30px',
        padding: '0 40px',
        height: 'calc(100vh - 250px)',
        position: 'relative',
      }}>
        {/* Left side - Game Preview (70%) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.4, ease: [0.65, 0, 0.35, 1] }}
          style={{
            flex: '0 0 70%',
            position: 'relative',
          }}
        >
          <motion.div
            whileHover={{ 
              boxShadow: '0 0 30px rgba(0, 229, 229, 0.7), inset 0 0 20px rgba(0, 229, 229, 0.1)',
            }}
            style={{
              width: '100%',
              height: '100%',
              background: 'rgba(3, 11, 26, 0.6)',
              border: '3px solid #00e5e5',
              borderImage: 'linear-gradient(135deg, #00e5e5 0%, rgba(0, 229, 229, 0.5) 100%) 1',
              boxShadow: '0 0 20px rgba(0, 229, 229, 0.4), inset 0 0 10px rgba(0, 229, 229, 0.05)',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Twinkling particles inside preview */}
            {Array.from({ length: 10 }).map((_, i) => (
              <motion.div
                key={i}
                initial={{ 
                  x: Math.random() * 100 + '%', 
                  y: Math.random() * 100 + '%',
                  opacity: 0 
                }}
                animate={{
                  x: [
                    Math.random() * 100 + '%',
                    (Math.random() * 100 - 10) + '%',
                  ],
                  y: [
                    Math.random() * 100 + '%',
                    (Math.random() * 100 - 10) + '%',
                  ],
                  opacity: [0, 0.6, 0],
                }}
                transition={{
                  duration: 5 + Math.random() * 5,
                  repeat: Infinity,
                  delay: Math.random() * 3,
                }}
                style={{
                  position: 'absolute',
                  width: '3px',
                  height: '3px',
                  backgroundColor: '#00e5e5',
                  borderRadius: '50%',
                  boxShadow: '0 0 6px rgba(0, 229, 229, 0.8)',
                }}
              />
            ))}

            {/* Play in New Tab button */}
            <motion.button
              whileHover={{ 
                scale: 1.05,
                boxShadow: '0 0 15px rgba(0, 229, 229, 1)',
              }}
              whileTap={{ scale: 0.95, y: 2 }}
              onMouseEnter={handleHover}
              style={{
                position: 'absolute',
                top: '15px',
                right: '15px',
                fontFamily: '"Press Start 2P", "Courier New", monospace',
                fontSize: '0.6rem',
                padding: '8px 15px',
                background: 'rgba(0, 229, 229, 0.1)',
                border: '2px solid #00e5e5',
                color: '#00e5e5',
                cursor: 'pointer',
                boxShadow: '0 0 10px rgba(0, 229, 229, 0.6)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                zIndex: 10,
              }}
            >
              <Play size={12} />
              Play in New Tab
            </motion.button>

            {/* Preview content placeholder */}
            <div style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#00e5e5',
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              fontSize: '1rem',
              opacity: 0.3,
            }}>
              Game Preview
            </div>
          </motion.div>

          {/* Live Preview label */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            transition={{ delay: 0.8 }}
            style={{
              fontFamily: '"Inter", sans-serif',
              fontSize: '0.75rem',
              color: '#00e5e5',
              marginTop: '10px',
              textAlign: 'center',
              letterSpacing: '0.05em',
            }}
          >
            Live Preview
          </motion.div>
        </motion.div>

        {/* Right side - Character & Enemy panels (30%) */}
        <div style={{
          flex: '0 0 calc(30% - 30px)',
          display: 'flex',
          flexDirection: 'column',
          gap: '30px',
        }}>
          {/* Main Character */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5, ease: [0.65, 0, 0.35, 1] }}
            style={{ flex: 1 }}
          >
            <div style={{
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              fontSize: '0.7rem',
              color: '#00e5e5',
              marginBottom: '10px',
              letterSpacing: '0.05em',
            }}>
              Main Character
            </div>
            
            <motion.div
              whileHover={{ 
                boxShadow: '0 0 25px rgba(0, 229, 229, 0.7)',
              }}
              style={{
                width: '100%',
                height: '100%',
                background: 'rgba(3, 11, 26, 0.6)',
                border: '3px solid #00e5e5',
                boxShadow: '0 0 15px rgba(0, 229, 229, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Character sprite */}
              <motion.div
                animate={characterAnim ? {
                  y: [0, -10, 0],
                  rotate: [0, 5, -5, 0],
                } : {}}
                transition={{ duration: 1, ease: 'easeInOut' }}
                style={{
                  width: '64px',
                  height: '64px',
                  background: 'linear-gradient(135deg, #00e5e5 0%, #0099cc 100%)',
                  borderRadius: '8px',
                  boxShadow: '0 0 20px rgba(0, 229, 229, 0.5)',
                  position: 'relative',
                }}
              >
                {/* Simple pixel character representation */}
                <div style={{
                  position: 'absolute',
                  top: '20%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '40%',
                  height: '30%',
                  background: '#fff',
                  borderRadius: '50%',
                }} />
                <div style={{
                  position: 'absolute',
                  bottom: '20%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '60%',
                  height: '40%',
                  background: 'rgba(255, 255, 255, 0.8)',
                  borderRadius: '4px',
                }} />
              </motion.div>
            </motion.div>
          </motion.div>

          {/* Enemy */}
          <motion.div
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.6, ease: [0.65, 0, 0.35, 1] }}
            style={{ flex: 1 }}
          >
            <div style={{
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              fontSize: '0.7rem',
              color: '#E6C97E',
              marginBottom: '10px',
              letterSpacing: '0.05em',
            }}>
              Enemy
            </div>
            
            <motion.div
              whileHover={{ 
                boxShadow: '0 0 25px rgba(230, 100, 50, 0.7)',
              }}
              style={{
                width: '100%',
                height: '100%',
                background: 'rgba(3, 11, 26, 0.6)',
                border: '3px solid #E66432',
                boxShadow: '0 0 15px rgba(230, 100, 50, 0.4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              {/* Enemy sprite */}
              <motion.div
                animate={enemyAnim ? {
                  x: [-3, 3, -3, 0],
                  scale: [1, 1.05, 1],
                } : {}}
                transition={{ duration: 1, ease: 'easeInOut' }}
                style={{
                  width: '64px',
                  height: '64px',
                  background: 'linear-gradient(135deg, #E66432 0%, #cc3300 100%)',
                  borderRadius: '8px',
                  boxShadow: '0 0 20px rgba(230, 100, 50, 0.5)',
                  position: 'relative',
                }}
              >
                {/* Simple pixel enemy representation */}
                <div style={{
                  position: 'absolute',
                  top: '25%',
                  left: '25%',
                  width: '15%',
                  height: '15%',
                  background: '#fff',
                  borderRadius: '50%',
                }} />
                <div style={{
                  position: 'absolute',
                  top: '25%',
                  right: '25%',
                  width: '15%',
                  height: '15%',
                  background: '#fff',
                  borderRadius: '50%',
                }} />
                <div style={{
                  position: 'absolute',
                  bottom: '25%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  width: '50%',
                  height: '20%',
                  background: 'rgba(255, 255, 255, 0.9)',
                  clipPath: 'polygon(0 100%, 50% 0, 100% 100%)',
                }} />
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Bottom prompt bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        style={{
          position: 'absolute',
          bottom: '40px',
          left: '40px',
          right: '40px',
          zIndex: 60,
        }}
      >
        <motion.div
          animate={isFocused ? {
            boxShadow: '0 0 30px rgba(0, 229, 229, 0.6), inset 0 0 20px rgba(0, 229, 229, 0.1)',
          } : {
            boxShadow: '0 0 15px rgba(0, 229, 229, 0.3), inset 0 0 10px rgba(0, 229, 229, 0.05)',
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            padding: '15px 20px',
            background: 'rgba(3, 11, 26, 0.8)',
            border: '2px solid #00e5e5',
            borderRadius: '4px',
            position: 'relative',
          }}
        >
          {/* Focus border stars */}
          {isFocused && (
            <>
              {Array.from({ length: 5 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ x: 0, opacity: 0 }}
                  animate={{ 
                    x: ['0%', '100%'],
                    opacity: [0, 1, 0],
                  }}
                  transition={{
                    duration: 2,
                    delay: i * 0.4,
                    repeat: Infinity,
                  }}
                  style={{
                    position: 'absolute',
                    top: '-3px',
                    left: (i * 20) + '%',
                    width: '4px',
                    height: '4px',
                    backgroundColor: '#00e5e5',
                    borderRadius: '50%',
                    boxShadow: '0 0 6px rgba(0, 229, 229, 0.8)',
                  }}
                />
              ))}
            </>
          )}

          {/* Upload icon */}
          <motion.button
            whileHover={{ rotate: [-3, 3, -3, 0] }}
            whileTap={{ scale: 0.9 }}
            transition={{ duration: 0.3 }}
            onMouseEnter={handleHover}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#00e5e5',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              padding: '5px',
            }}
          >
            <Upload size={20} />
          </motion.button>

          {/* Text input */}
          <input
            type="text"
            value={promptValue}
            onChange={(e) => setPromptValue(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Refine your world…"
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#00e5e5',
              fontFamily: '"Inter", sans-serif',
              fontSize: '1rem',
              letterSpacing: '0.02em',
            }}
          />

          {/* Send star button */}
          <motion.button
            whileHover={{ 
              scale: 1.1,
              boxShadow: '0 0 20px rgba(0, 229, 229, 0.8)',
            }}
            whileTap={{ scale: 0.9 }}
            onClick={onRefineWorld}
            onMouseEnter={handleHover}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#00e5e5',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              padding: '5px',
              position: 'relative',
            }}
          >
            <motion.div
              animate={{
                opacity: [0.6, 1, 0.6],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <Star size={24} fill="#00e5e5" />
            </motion.div>
          </motion.button>
        </motion.div>
      </motion.div>
    </div>
  );
}
