import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { motion } from 'motion/react';
import { CosmicBackground } from './CosmicBackground';
import { AsteriaTitle } from './AsteriaTitle';
import { PixelStars } from './PixelStars';
import { PixelMoon } from './PixelMoon';
import { PixelShootingStar } from './PixelShootingStar';
import { ButtonSparkles } from './ButtonSparkles';
export function LandingPage({ onStart }) {
    const [showSparkles, setShowSparkles] = useState(false);
    const [isPressed, setIsPressed] = useState(false);
    const handleClick = () => {
        setIsPressed(true);
        setShowSparkles(true);
        // Trigger page transition after animation
        setTimeout(() => {
            onStart();
        }, 500);
        // Reset after animation
        setTimeout(() => {
            setIsPressed(false);
            setShowSparkles(false);
        }, 600);
    };
    return (_jsxs("div", { className: "relative min-h-screen", children: [_jsx(CosmicBackground, {}), _jsx(PixelStars, {}), _jsx(PixelShootingStar, {}), _jsx(PixelMoon, {}), _jsx("div", { className: "relative z-10 flex min-h-screen items-center justify-center px-6 py-12", children: _jsxs(motion.div, { initial: { opacity: 0, y: 30 }, animate: { opacity: 1, y: 0 }, transition: { duration: 1.4, ease: "easeOut" }, className: "flex flex-col items-center text-center max-w-4xl", children: [_jsx(AsteriaTitle, {}), _jsx(motion.p, { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 1.2, delay: 0.6 }, style: {
                                marginTop: '1.2rem', // Closer to title
                                fontSize: 'clamp(0.75rem, 1.5vw, 0.95rem)', // 75% of previous
                                fontFamily: '"Courier New", Courier, monospace',
                                color: '#d4c5a8',
                                letterSpacing: '0.06em',
                                maxWidth: '600px',
                                lineHeight: '1.6',
                            }, children: "Dream, Describe, Dive into your world" }), _jsxs(motion.button, { initial: { opacity: 0, y: 20 }, animate: {
                                opacity: 1,
                                y: 0,
                            }, transition: {
                                opacity: { duration: 1.2, delay: 0.9 },
                                y: { duration: 1.2, delay: 0.9 },
                            }, onClick: handleClick, className: "group relative overflow-visible transition-all duration-150", style: {
                                marginTop: '2.4rem', // Closer spacing
                                padding: '16px 56px',
                                background: isPressed
                                    ? '#00c5c5'
                                    : 'linear-gradient(180deg, #00e5e5 0%, #00d0d0 50%, #00b8b8 100%)',
                                border: 'none',
                                borderRadius: '0',
                                boxShadow: isPressed
                                    ? `
                  inset 0 0 0 3px #1a4a6a,
                  inset 0 0 0 4px #0a2a4a,
                  inset 4px 4px 8px rgba(0, 0, 0, 0.4)
                `
                                    : `
                  0 0 0 3px #1a4a6a,
                  0 0 0 4px #0a2a4a,
                  0 0 0 5px #2a5a7a,
                  6px 6px 0 rgba(0, 0, 0, 0.4)
                `,
                                imageRendering: 'pixelated',
                                transform: isPressed ? 'translate(3px, 3px)' : 'translate(0, 0)',
                                position: 'relative',
                            }, children: [_jsx(ButtonSparkles, { show: showSparkles }), _jsxs("div", { style: {
                                        position: 'absolute',
                                        inset: '-5px',
                                        pointerEvents: 'none',
                                        imageRendering: 'pixelated',
                                    }, children: [_jsx("div", { style: {
                                                position: 'absolute',
                                                top: '0',
                                                left: '0',
                                                width: '12px',
                                                height: '12px',
                                                background: `
                  linear-gradient(135deg, 
                    transparent 0%, transparent 41.5%, 
                    #2a5a7a 41.5%, #2a5a7a 58.5%,
                    transparent 58.5%, transparent 100%
                  )
                `,
                                            } }), _jsx("div", { style: {
                                                position: 'absolute',
                                                top: '0',
                                                right: '0',
                                                width: '12px',
                                                height: '12px',
                                                background: `
                  linear-gradient(225deg, 
                    transparent 0%, transparent 41.5%, 
                    #2a5a7a 41.5%, #2a5a7a 58.5%,
                    transparent 58.5%, transparent 100%
                  )
                `,
                                            } }), _jsx("div", { style: {
                                                position: 'absolute',
                                                bottom: '0',
                                                left: '0',
                                                width: '12px',
                                                height: '12px',
                                                background: `
                  linear-gradient(45deg, 
                    transparent 0%, transparent 41.5%, 
                    #2a5a7a 41.5%, #2a5a7a 58.5%,
                    transparent 58.5%, transparent 100%
                  )
                `,
                                            } }), _jsx("div", { style: {
                                                position: 'absolute',
                                                bottom: '0',
                                                right: '0',
                                                width: '12px',
                                                height: '12px',
                                                background: `
                  linear-gradient(315deg, 
                    transparent 0%, transparent 41.5%, 
                    #2a5a7a 41.5%, #2a5a7a 58.5%,
                    transparent 58.5%, transparent 100%
                  )
                `,
                                            } })] }), _jsx("span", { className: "relative z-10 transition-colors duration-300", style: {
                                        fontSize: 'clamp(0.85rem, 1.6vw, 1.05rem)',
                                        fontFamily: '"Press Start 2P", "Courier New", monospace',
                                        color: '#1a3a5a',
                                        letterSpacing: '0.12em',
                                        textShadow: 'none',
                                        imageRendering: 'pixelated',
                                    }, children: "START CREATING" })] })] }) })] }));
}
