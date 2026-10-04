import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { motion } from 'motion/react';
export function AsteriaTitle() {
    return (_jsxs(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, transition: { duration: 1.4, delay: 0.3 }, className: "relative", children: [_jsx("div", { className: "absolute inset-0 -z-10", style: {
                    background: `
            radial-gradient(ellipse at 50% 50%, rgba(190, 180, 220, 0.12) 0%, transparent 50%)
          `,
                    filter: 'blur(30px)',
                    transform: 'scale(1.8)',
                } }), _jsx("h1", { style: {
                    fontSize: 'clamp(2.1rem, 6.4vw, 4.1rem)',
                    fontFamily: '"Press Start 2P", "Courier New", monospace',
                    color: '#f8ecd7',
                    letterSpacing: '0.15em',
                    fontWeight: '400',
                    textShadow: '4px 4px 0px #000000',
                    imageRendering: 'pixelated',
                    textTransform: 'uppercase',
                    lineHeight: '1.2',
                }, children: "ASTERIA" })] }));
}
