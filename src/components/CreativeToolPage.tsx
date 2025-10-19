import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { CosmicBackground } from "./CosmicBackground";
import { PixelStars } from "./PixelStars";
import { PixelMoon } from "./PixelMoon";
import { PixelShootingStar } from "./PixelShootingStar";
import { DynamicSlider } from "./DynamicSlider";
import { ConstellationLoading } from "./ConstellationLoading";
import { Image, Sparkles } from "lucide-react";



type Stage = 'input' | 'sliders' | 'loading';

interface CreativeToolPageProps {
  onGenerate?: () => void;
}

export function CreativeToolPage({ onGenerate }: CreativeToolPageProps = {}) {
  const [stage, setStage] = useState<Stage>('input');
  const [worldDescription, setWorldDescription] = useState('');
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [imageDescription, setImageDescription] = useState('');
  const [imageCategory, setImageCategory] = useState('Main Character');
  const [customCategory, setCustomCategory] = useState('');
  const [gameMode, setGameMode] = useState<'single' | 'multiplayer'>('single');
  const [isFocused, setIsFocused] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Slider values
  const [horrorLevel, setHorrorLevel] = useState(3);
  const [puzzleComplexity, setPuzzleComplexity] = useState(5);
  const [ageGroup, setAgeGroup] = useState(7);
  const [speedChaos, setSpeedChaos] = useState(4);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadedImage(reader.result as string);
        setShowImageModal(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerateSliders = () => {
    if (worldDescription.trim()) {
      setStage('sliders');
    }
  };

  const handleStartGenerating = () => {
    setStage('loading');
    // Trigger generation logic here
    console.log('Starting generation with:', {
      worldDescription,
      uploadedImage,
      imageDescription,
      imageCategory: imageCategory === 'Other' ? customCategory : imageCategory,
      gameMode,
      settings: {
        horrorLevel,
        puzzleComplexity,
        ageGroup,
        speedChaos,
      }
    });

    // After loading, transition to edit page
    setTimeout(() => {
      if (onGenerate) {
        onGenerate();
      }
    }, 4000);
  };

  return (
    <div className="relative min-h-screen">
      {/* Background elements */}
      <CosmicBackground />
      <PixelStars />
      <PixelShootingStar />
      <PixelMoon />

      {/* Main content */}
      <div className="relative z-10 px-6 py-12 pb-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="w-full max-w-2xl mx-auto"
        >
          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            style={{
              fontFamily: '"Press Start 2P", "Courier New", monospace',
              color: '#f8ecd7',
              fontSize: 'clamp(1rem, 2.5vw, 1.4rem)',
              textAlign: 'center',
              marginBottom: '2rem',
              letterSpacing: '0.1em',
              textShadow: '3px 3px 0px #000000',
              imageRendering: 'pixelated',
            }}
          >
            {stage === 'input' ? 'DESCRIBE YOUR WORLD' : 'CUSTOMIZE SETTINGS'}
          </motion.h1>

          {/* Input stage */}
          <AnimatePresence mode="wait">
            {stage === 'input' && (
              <motion.div
                key="input-stage"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
              >
                {/* Large text box with upload button */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 1.2 }}
                  className="relative"
                >
                  {/* Border animation wrapper */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.32, delay: 1.2 }}
                    style={{
                      position: 'relative',
                      boxShadow: isFocused
                        ? `
                          0 0 0 3px #1a4a6a,
                          0 0 0 4px #0a2a4a,
                          0 0 0 5px #00e5e5,
                          0 0 20px rgba(0, 229, 229, 0.4),
                          inset 0 2px 12px rgba(0, 0, 0, 0.4)
                        `
                        : `
                          0 0 0 3px #1a4a6a,
                          0 0 0 4px #0a2a4a,
                          0 0 0 5px #2a5a7a,
                          inset 0 2px 8px rgba(0, 0, 0, 0.4)
                        `,
                      transition: 'box-shadow 0.3s ease',
                    }}
                  >
                    <textarea
                      value={worldDescription}
                      onChange={(e) => setWorldDescription(e.target.value)}
                      onFocus={() => setIsFocused(true)}
                      onBlur={() => setIsFocused(false)}
                      placeholder="A mystical forest where time stands still..."
                      rows={4}
                      style={{
                        width: '100%',
                        padding: '16px',
                        paddingBottom: '50px',
                        background: 'rgba(26, 42, 90, 0.7)',
                        border: 'none',
                        color: '#f8ecd7',
                        fontFamily: '"Courier New", Courier, monospace',
                        fontSize: 'clamp(0.9rem, 1.4vw, 1.05rem)',
                        lineHeight: '1.6',
                        resize: 'none',
                        imageRendering: 'pixelated',
                        outline: 'none',
                      }}
                      className="placeholder:text-[#8a9ac7] placeholder:opacity-60"
                    />

                    {/* Upload button inside text box */}
                    <motion.button
                      whileHover={{ scale: 1.1, opacity: 1 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => fileInputRef.current?.click()}
                      style={{
                        position: 'absolute',
                        bottom: '16px',
                        left: '16px',
                        padding: '10px',
                        background: 'rgba(0, 229, 229, 0.15)',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        transition: 'all 0.2s',
                        boxShadow: '0 0 0 2px rgba(0, 229, 229, 0.3)',
                      }}
                      className="group"
                    >
                      <Image
                        size={20}
                        style={{
                          color: '#00e5e5',
                          opacity: 0.8,
                        }}
                        className="group-hover:opacity-100 transition-opacity"
                      />
                      <span
                        style={{
                          fontFamily: '"Courier New", Courier, monospace',
                          fontSize: '0.75rem',
                          color: '#00e5e5',
                          opacity: 0.8,
                        }}
                        className="group-hover:opacity-100 transition-opacity"
                      >
                        Upload Image
                      </span>
                      {/* Sparkle effect on hover */}
                      <motion.div
                        initial={{ opacity: 0, y: 0 }}
                        whileHover={{ opacity: [0, 1, 0], y: -20 }}
                        transition={{ duration: 0.8 }}
                        style={{
                          position: 'absolute',
                          top: '-10px',
                          right: '10px',
                        }}
                      >
                        <Sparkles size={12} style={{ color: '#00e5e5' }} />
                      </motion.div>
                    </motion.button>

                    {/* Hidden file input */}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />

                    {/* Uploaded image thumbnail */}
                    {uploadedImage && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3 }}
                        style={{
                          position: 'absolute',
                          bottom: '16px',
                          left: '140px',
                          width: '40px',
                          height: '40px',
                          border: '2px solid #00e5e5',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          imageRendering: 'pixelated',
                        }}
                      >
                        <img
                          src={uploadedImage}
                          alt="Uploaded"
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        />
                      </motion.div>
                    )}
                  </motion.div>

                  {/* Image upload modal */}
                  <AnimatePresence>
                    {showImageModal && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 20 }}
                        transition={{ duration: 0.25 }}
                        style={{
                          marginTop: '16px',
                          padding: '20px',
                          background: 'rgba(26, 42, 90, 0.8)',
                          boxShadow: `
                            0 0 0 2px #1a4a6a,
                            0 0 0 3px #0a2a4a,
                            0 0 0 4px #00e5e5,
                            0 0 12px rgba(0, 229, 229, 0.3)
                          `,
                        }}
                      >
                        {/* Describe this image field */}
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2 }}
                          className="mb-4"
                        >
                          <label
                            style={{
                              fontFamily: '"Press Start 2P", "Courier New", monospace',
                              fontSize: 'clamp(0.6rem, 1.1vw, 0.75rem)',
                              color: '#00e5e5',
                              letterSpacing: '0.08em',
                              display: 'block',
                              marginBottom: '12px',
                            }}
                          >
                            Describe this image:
                          </label>
                          <input
                            type="text"
                            value={imageDescription}
                            onChange={(e) => setImageDescription(e.target.value)}
                            placeholder="A brave knight in silver armor..."
                            style={{
                              width: '100%',
                              padding: '12px',
                              background: 'rgba(10, 20, 50, 0.6)',
                              border: '2px solid #1a4a6a',
                              borderRadius: '0',
                              color: '#f8ecd7',
                              fontFamily: '"Courier New", Courier, monospace',
                              fontSize: '0.95rem',
                              outline: 'none',
                            }}
                            className="placeholder:text-[#8a9ac7] placeholder:opacity-60"
                          />
                        </motion.div>

                        {/* Category dropdown */}
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2, delay: 0.2 }}
                        >
                          <label
                            style={{
                              fontFamily: '"Press Start 2P", "Courier New", monospace',
                              fontSize: 'clamp(0.6rem, 1.1vw, 0.75rem)',
                              color: '#00e5e5',
                              letterSpacing: '0.08em',
                              display: 'block',
                              marginBottom: '12px',
                            }}
                          >
                            Used as:
                          </label>
                          <select
                            value={imageCategory}
                            onChange={(e) => setImageCategory(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '12px',
                              background: 'rgba(10, 20, 50, 0.6)',
                              border: '2px solid #1a4a6a',
                              borderRadius: '0',
                              color: '#f8ecd7',
                              fontFamily: '"Courier New", Courier, monospace',
                              fontSize: '0.95rem',
                              outline: 'none',
                              cursor: 'pointer',
                            }}
                          >
                            <option value="Main Character">Main Character</option>
                            <option value="Enemy">Enemy</option>
                            <option value="Environment">Environment</option>
                            <option value="Other">Other</option>
                          </select>
                        </motion.div>

                        {/* Custom category field */}
                        {imageCategory === 'Other' && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="mt-3"
                          >
                            <input
                              type="text"
                              value={customCategory}
                              onChange={(e) => setCustomCategory(e.target.value)}
                              placeholder="Enter custom category..."
                              style={{
                                width: '100%',
                                padding: '12px',
                                background: 'rgba(10, 20, 50, 0.6)',
                                border: '2px solid #1a4a6a',
                                borderRadius: '0',
                                color: '#f8ecd7',
                                fontFamily: '"Courier New", Courier, monospace',
                                fontSize: '0.9rem',
                                outline: 'none',
                              }}
                              className="placeholder:text-[#8a9ac7] placeholder:opacity-60"
                            />
                          </motion.div>
                        )}

                        {/* Close button */}
                        <button
                          onClick={() => setShowImageModal(false)}
                          style={{
                            marginTop: '16px',
                            padding: '8px 20px',
                            background: 'rgba(0, 229, 229, 0.2)',
                            border: '2px solid #00e5e5',
                            borderRadius: '0',
                            color: '#00e5e5',
                            fontFamily: '"Press Start 2P", "Courier New", monospace',
                            fontSize: '0.65rem',
                            cursor: 'pointer',
                            letterSpacing: '0.08em',
                          }}
                          className="hover:bg-[rgba(0,229,229,0.3)] transition-colors"
                        >
                          DONE
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>

                {/* Game Mode Toggle */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 1.4 }}
                  className="mt-6 flex justify-center"
                >
                  <div
                    style={{
                      padding: '4px',
                      background: 'rgba(26, 42, 90, 0.6)',
                      boxShadow: `
                        0 0 0 2px #1a4a6a,
                        0 0 0 3px #0a2a4a,
                        inset 0 2px 6px rgba(0, 0, 0, 0.4)
                      `,
                      display: 'inline-flex',
                      gap: '4px',
                    }}
                  >
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setGameMode('single')}
                      style={{
                        padding: '12px 32px',
                        background: gameMode === 'single'
                          ? 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 50%, #00b8b8 100%)'
                          : 'transparent',
                        border: 'none',
                        borderRadius: '0',
                        fontFamily: '"Press Start 2P", "Courier New", monospace',
                        fontSize: 'clamp(0.65rem, 1.2vw, 0.8rem)',
                        color: gameMode === 'single' ? '#1a3a5a' : '#8a9ac7',
                        letterSpacing: '0.08em',
                        cursor: 'pointer',
                        boxShadow: gameMode === 'single'
                          ? '0 0 12px rgba(0, 229, 229, 0.5)'
                          : 'none',
                        transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                      }}
                    >
                      SINGLE PLAYER
                    </motion.button>

                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setGameMode('multiplayer')}
                      style={{
                        padding: '12px 32px',
                        background: gameMode === 'multiplayer'
                          ? 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 50%, #00b8b8 100%)'
                          : 'transparent',
                        border: 'none',
                        borderRadius: '0',
                        fontFamily: '"Press Start 2P", "Courier New", monospace',
                        fontSize: 'clamp(0.65rem, 1.2vw, 0.8rem)',
                        color: gameMode === 'multiplayer' ? '#1a3a5a' : '#8a9ac7',
                        letterSpacing: '0.08em',
                        cursor: 'pointer',
                        boxShadow: gameMode === 'multiplayer'
                          ? '0 0 12px rgba(0, 229, 229, 0.5)'
                          : 'none',
                        transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                      }}
                    >
                      MULTIPLAYER
                    </motion.button>
                  </div>
                </motion.div>

                {/* Generate Base Settings Button */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.6, delay: 1.6 }}
                  className="flex justify-center mt-8 mb-12"
                >
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98, y: 2 }}
                    onClick={handleGenerateSliders}
                    disabled={!worldDescription.trim()}
                    style={{
                      padding: '18px 60px',
                      background: !worldDescription.trim()
                        ? 'rgba(0, 197, 197, 0.3)'
                        : 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 50%, #00b8b8 100%)',
                      border: 'none',
                      borderRadius: '0',
                      boxShadow: `
                        0 0 0 3px #1a4a6a,
                        0 0 0 4px #0a2a4a,
                        0 0 0 5px #00e5e5,
                        6px 6px 0 rgba(0, 0, 0, 0.4),
                        0 0 30px rgba(0, 229, 229, 0.4)
                      `,
                      imageRendering: 'pixelated',
                      fontFamily: '"Press Start 2P", "Courier New", monospace',
                      fontSize: 'clamp(0.75rem, 1.4vw, 0.95rem)',
                      color: '#1a3a5a',
                      letterSpacing: '0.12em',
                      cursor: !worldDescription.trim() ? 'not-allowed' : 'pointer',
                      position: 'relative',
                      overflow: 'hidden',
                      opacity: !worldDescription.trim() ? 0.5 : 1,
                    }}
                  >
                    {/* Pulsing glow animation */}
                    <motion.div
                      animate={{
                        opacity: [0.3, 0.6, 0.3],
                        scale: [1, 1.1, 1],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      style={{
                        position: 'absolute',
                        inset: '-10px',
                        background: 'radial-gradient(circle, rgba(0, 229, 229, 0.3) 0%, transparent 70%)',
                        pointerEvents: 'none',
                      }}
                    />

                    <span className="relative z-10">
                      GENERATE BASE SETTINGS
                    </span>
                  </motion.button>
                </motion.div>
              </motion.div>
            )}

            {/* Sliders stage */}
            {stage === 'sliders' && (
              <motion.div
                key="sliders-stage"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                {/* Display sliders */}
                <motion.div
                  style={{
                    padding: '24px',
                    background: 'rgba(26, 42, 90, 0.5)',
                    boxShadow: `
                      0 0 0 2px #1a4a6a,
                      0 0 0 3px #0a2a4a,
                      0 0 0 4px #2a5a7a,
                      inset 0 2px 8px rgba(0, 0, 0, 0.4)
                    `,
                    marginBottom: '24px',
                  }}
                >
                  <DynamicSlider
                    label="Horror Level"
                    min={0}
                    max={10}
                    value={horrorLevel}
                    onChange={setHorrorLevel}
                    delay={0.2}
                  />
                  <DynamicSlider
                    label="Puzzle Complexity"
                    min={0}
                    max={10}
                    value={puzzleComplexity}
                    onChange={setPuzzleComplexity}
                    delay={0.4}
                  />
                  <DynamicSlider
                    label="Age Group"
                    min={3}
                    max={18}
                    value={ageGroup}
                    onChange={setAgeGroup}
                    delay={0.6}
                  />
                  <DynamicSlider
                    label="Speed / Chaos"
                    min={0}
                    max={10}
                    value={speedChaos}
                    onChange={setSpeedChaos}
                    delay={0.8}
                  />
                </motion.div>

                {/* Start Generating Button */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.6, delay: 1.2 }}
                  className="flex justify-center mt-8 mb-12"
                >
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98, y: 2 }}
                    onClick={handleStartGenerating}
                    style={{
                      padding: '18px 60px',
                      background: 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 50%, #00b8b8 100%)',
                      border: 'none',
                      borderRadius: '0',
                      boxShadow: `
                        0 0 0 3px #1a4a6a,
                        0 0 0 4px #0a2a4a,
                        0 0 0 5px #00e5e5,
                        6px 6px 0 rgba(0, 0, 0, 0.4),
                        0 0 30px rgba(0, 229, 229, 0.4)
                      `,
                      imageRendering: 'pixelated',
                      fontFamily: '"Press Start 2P", "Courier New", monospace',
                      fontSize: 'clamp(0.85rem, 1.6vw, 1.05rem)',
                      color: '#1a3a5a',
                      letterSpacing: '0.12em',
                      cursor: 'pointer',
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    {/* Pulsing glow animation */}
                    <motion.div
                      animate={{
                        opacity: [0.3, 0.6, 0.3],
                        scale: [1, 1.1, 1],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      style={{
                        position: 'absolute',
                        inset: '-10px',
                        background: 'radial-gradient(circle, rgba(0, 229, 229, 0.3) 0%, transparent 70%)',
                        pointerEvents: 'none',
                      }}
                    />

                    <span className="relative z-10">
                      START GENERATING
                    </span>
                  </motion.button>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Loading Screen */}
      <AnimatePresence>
        {stage === 'loading' && <ConstellationLoading />}
      </AnimatePresence>
    </div>
  );
}
