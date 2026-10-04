import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';
export function ConstellationLoading({ statusText }) {
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 });
    const [sparkles, setSparkles] = useState([]);
    const [nextId, setNextId] = useState(0);
    // Track cursor position
    useEffect(() => {
        const handleMouseMove = (e) => {
            setCursorPos({ x: e.clientX, y: e.clientY });
            // Add sparkle trail
            if (Math.random() > 0.7) {
                setSparkles(prev => [...prev, { id: nextId, x: e.clientX, y: e.clientY }]);
                setNextId(prev => prev + 1);
            }
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, [nextId]);
    // Clean up old sparkles
    useEffect(() => {
        if (sparkles.length > 10) {
            setSparkles(prev => prev.slice(-10));
        }
    }, [sparkles]);
    // Constellation points that will drift and connect
    const constellationPoints = [
        { x: 75, y: 60, driftX: [-10, 10], driftY: [-5, 5] },
        { x: 188, y: 90, driftX: [-8, 12], driftY: [-10, 8] },
        { x: 135, y: 165, driftX: [-12, 8], driftY: [-6, 10] },
        { x: 240, y: 150, driftX: [-10, 10], driftY: [-8, 8] },
        { x: 210, y: 240, driftX: [-6, 14], driftY: [-12, 6] },
        { x: 90, y: 210, driftX: [-14, 6], driftY: [-8, 12] },
    ];
    return (_jsxs(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 0.6 }, style: {
            position: 'fixed',
            inset: 0,
            background: 'radial-gradient(circle at center, rgb(10, 20, 50) 0%, rgb(5, 10, 30) 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            overflow: 'hidden',
        }, children: [sparkles.map(sparkle => (_jsx(motion.div, { initial: { opacity: 1, scale: 1 }, animate: {
                    opacity: 0,
                    scale: 0,
                    y: sparkle.y - 30,
                }, exit: { opacity: 0 }, transition: { duration: 0.8 }, onAnimationComplete: () => {
                    setSparkles(prev => prev.filter(s => s.id !== sparkle.id));
                }, style: {
                    position: 'absolute',
                    left: sparkle.x,
                    top: sparkle.y,
                    width: '4px',
                    height: '4px',
                    background: '#00e5e5',
                    borderRadius: '50%',
                    boxShadow: '0 0 8px #00e5e5',
                    pointerEvents: 'none',
                } }, sparkle.id))), _jsx(motion.p, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.6, delay: 0.3 }, style: {
                    fontFamily: '"Press Start 2P", "Courier New", monospace',
                    fontSize: 'clamp(0.9rem, 1.8vw, 1.2rem)',
                    color: '#00e5e5',
                    letterSpacing: '0.1em',
                    textAlign: 'center',
                    marginTop: '120px',
                    marginBottom: '50px',
                    textShadow: '0 0 20px rgba(0, 229, 229, 0.5)',
                    position: 'relative',
                    zIndex: 10,
                }, children: statusText || 'Forging your world<br />among the stars...' }, statusText), _jsxs("div", { style: {
                    position: 'relative',
                    width: '300px',
                    height: '300px',
                }, children: [constellationPoints.map((point, i) => (_jsx(motion.div, { initial: { opacity: 0, scale: 0 }, animate: {
                            opacity: [0.6, 1, 0.6],
                            scale: [0, 1.2, 1],
                            x: point.driftX,
                            y: point.driftY,
                        }, transition: {
                            opacity: {
                                duration: 2,
                                repeat: Infinity,
                                delay: i * 0.3,
                                ease: 'easeInOut',
                            },
                            scale: {
                                duration: 0.6,
                                delay: i * 0.15,
                            },
                            x: {
                                duration: 6,
                                repeat: Infinity,
                                repeatType: 'reverse',
                                ease: 'easeInOut',
                                delay: i * 0.5,
                            },
                            y: {
                                duration: 5,
                                repeat: Infinity,
                                repeatType: 'reverse',
                                ease: 'easeInOut',
                                delay: i * 0.4,
                            }
                        }, style: {
                            position: 'absolute',
                            left: `${point.x}px`,
                            top: `${point.y}px`,
                            width: '10px',
                            height: '10px',
                            background: '#00e5e5',
                            borderRadius: '50%',
                            boxShadow: '0 0 20px #00e5e5, 0 0 10px #00f5f5',
                        } }, i))), _jsxs("svg", { style: {
                            position: 'absolute',
                            inset: 0,
                            width: '100%',
                            height: '100%',
                            overflow: 'visible',
                        }, children: [[
                                { from: 0, to: 1 },
                                { from: 1, to: 2 },
                                { from: 2, to: 3 },
                                { from: 3, to: 4 },
                                { from: 4, to: 5 },
                                { from: 5, to: 0 },
                            ].map((connection, i) => (_jsx(motion.line, { x1: constellationPoints[connection.from].x, y1: constellationPoints[connection.from].y, x2: constellationPoints[connection.to].x, y2: constellationPoints[connection.to].y, stroke: "url(#lineGradient)", strokeWidth: "2", strokeDasharray: "5,5", initial: { pathLength: 0, opacity: 0 }, animate: {
                                    pathLength: [0, 1, 1, 0],
                                    opacity: [0, 1, 1, 0],
                                }, transition: {
                                    duration: 6,
                                    repeat: Infinity,
                                    delay: i * 0.8,
                                    ease: 'easeInOut',
                                }, style: {
                                    filter: 'drop-shadow(0 0 6px #00e5e5)',
                                } }, i))), _jsx("defs", { children: _jsxs("linearGradient", { id: "lineGradient", x1: "0%", y1: "0%", x2: "100%", y2: "0%", children: [_jsx("stop", { offset: "0%", stopColor: "rgba(0, 229, 229, 0.2)" }), _jsx("stop", { offset: "50%", stopColor: "rgba(0, 229, 229, 0.9)" }), _jsx("stop", { offset: "100%", stopColor: "rgba(0, 229, 229, 0.2)" })] }) })] }), _jsx(motion.div, { animate: {
                            opacity: [0.1, 0.3, 0.1],
                            scale: [1, 1.05, 1],
                        }, transition: {
                            duration: 4,
                            repeat: Infinity,
                            ease: 'easeInOut',
                        }, style: {
                            position: 'absolute',
                            inset: '-50px',
                            background: 'radial-gradient(circle at center, rgba(0, 229, 229, 0.15) 0%, transparent 70%)',
                            pointerEvents: 'none',
                        } })] }), _jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { delay: 0.6 }, style: {
                    position: 'absolute',
                    bottom: '60px',
                    display: 'flex',
                    gap: '12px',
                }, children: [0, 1, 2].map((i) => (_jsx(motion.div, { animate: {
                        opacity: [0.3, 1, 0.3],
                        scale: [0.8, 1.2, 0.8],
                    }, transition: {
                        duration: 1.2,
                        repeat: Infinity,
                        delay: i * 0.3,
                        ease: 'easeInOut',
                    }, style: {
                        width: '8px',
                        height: '8px',
                        background: '#00e5e5',
                        borderRadius: '50%',
                        boxShadow: '0 0 12px #00e5e5',
                    } }, i))) })] }));
}
