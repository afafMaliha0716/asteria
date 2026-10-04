import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';
export function ButtonSparkles({ show }) {
    const [sparkles, setSparkles] = useState([]);
    useEffect(() => {
        if (show) {
            // Generate sparkle particles
            const newSparkles = [];
            for (let i = 0; i < 8; i++) {
                newSparkles.push({
                    id: i,
                    x: (Math.random() - 0.5) * 120,
                    y: (Math.random() - 0.5) * 80,
                    delay: i * 0.05,
                });
            }
            setSparkles(newSparkles);
        }
    }, [show]);
    if (!show)
        return null;
    return (_jsx("div", { className: "absolute inset-0 pointer-events-none", children: sparkles.map((sparkle) => (_jsx(motion.div, { className: "absolute top-1/2 left-1/2", initial: {
                x: 0,
                y: 0,
                opacity: 1,
                scale: 1,
            }, animate: {
                x: sparkle.x,
                y: sparkle.y,
                opacity: 0,
                scale: 0.3,
            }, transition: {
                duration: 1,
                delay: sparkle.delay,
                ease: "easeOut",
            }, children: _jsxs("svg", { width: "8", height: "8", viewBox: "0 0 8 8", fill: "none", children: [_jsx("rect", { x: "3", y: "0", width: "2", height: "8", fill: "#f8ecd7" }), _jsx("rect", { x: "0", y: "3", width: "8", height: "2", fill: "#f8ecd7" })] }) }, sparkle.id))) }));
}
