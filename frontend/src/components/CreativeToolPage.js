import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { CosmicBackground } from "./CosmicBackground";
import { PixelStars } from "./PixelStars";
import { PixelMoon } from "./PixelMoon";
import { PixelShootingStar } from "./PixelShootingStar";
import { DynamicSlider } from "./DynamicSlider";
import { ConstellationLoading } from "./ConstellationLoading";
import { Image, Sparkles } from "lucide-react";
import { API_BASE } from "../config";
export function CreativeToolPage({ onGenerate } = {}) {
    const [stage, setStage] = useState('input');
    const [worldDescription, setWorldDescription] = useState('');
    const [uploadedImage, setUploadedImage] = useState(null);
    const [showImageModal, setShowImageModal] = useState(false);
    const [imageDescription, setImageDescription] = useState('');
    const [imageCategory, setImageCategory] = useState('Main Character');
    const [customCategory, setCustomCategory] = useState('');
    const [gameMode, setGameMode] = useState('single');
    const [isFocused, setIsFocused] = useState(false);
    const fileInputRef = useRef(null);
    // Slider values
    const [horrorLevel, setHorrorLevel] = useState(3);
    const [puzzleComplexity, setPuzzleComplexity] = useState(5);
    const [ageGroup, setAgeGroup] = useState(7);
    const [speedChaos, setSpeedChaos] = useState(4);
    const [taskId, setTaskId] = useState(null);
    const [loadingStatus, setLoadingStatus] = useState('Initiating sequence...');
    // This effect will start polling when a task ID is received
    useEffect(() => {
        if (!taskId)
            return;
        const intervalId = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE}/api/generate/status/${taskId}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch status');
                }
                const data = await response.json();
                // Update loading status message based on backend status
                switch (data.status) {
                    case 'IN_PROGRESS':
                        setLoadingStatus('Generating game world...<br/>AI is thinking...');
                        break;
                    case 'PACKAGING':
                        setLoadingStatus('Packaging your game...<br/>Creating executable...');
                        break;
                    case 'PENDING':
                        setLoadingStatus('Waiting in the queue...');
                        break;
                }
                if (data.status === 'SUCCESS') {
                    clearInterval(intervalId);
                    console.log('Generation successful!', data.result);
                    // 1. Pass the successful result up to the parent component (App.tsx)
                    if (onGenerate) {
                        onGenerate(data.result);
                    }
                    // 2. CRITICAL FIX: Tell CreativeToolPage to stop showing the loading screen.
                    // This allows the parent component to render the EditPage with the new result prop.
                    setStage('sliders'); // Or 'input', whichever state naturally follows 'loading'
                    // 3. Clear the task ID 
                    setTaskId(null);
                }
                else if (data.status === 'FAILURE') {
                    clearInterval(intervalId);
                    console.error('Generation failed:', data.result.error);
                    setStage('sliders');
                    setTaskId(null);
                }
            }
            catch (error) {
                console.error('Error polling for status:', error);
                clearInterval(intervalId);
                setStage('sliders');
                setTaskId(null);
            }
        }, 3000); // Poll every 3 seconds
        return () => clearInterval(intervalId);
    }, [taskId, onGenerate]);
    const handleImageUpload = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setUploadedImage(reader.result);
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
    const handleStartGenerating = async () => {
        setStage('loading');
        const generationData = {
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
        };
        try {
            // 1. Call the new 'start' endpoint
            const response = await fetch(`${API_BASE}/api/generate/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(generationData),
            });
            if (!response.ok) {
                throw new Error('Failed to start generation');
            }
            const { task_id } = await response.json();
            // 2. Set the task ID in the state, which will trigger the useEffect to start polling
            setTaskId(task_id);
        }
        catch (error) {
            console.error("There was a problem starting the generation:", error);
            setStage('sliders'); // Go back to the previous screen on error
        }
    };
    return (_jsxs("div", { className: "relative min-h-screen", children: [_jsx(CosmicBackground, {}), _jsx(PixelStars, {}), _jsx(PixelShootingStar, {}), _jsx(PixelMoon, {}), _jsx("div", { className: "relative z-10 px-6 py-12 pb-20", children: _jsxs(motion.div, { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.8, delay: 0.8 }, className: "w-full max-w-2xl mx-auto", children: [_jsx(motion.h1, { initial: { opacity: 0, y: -20 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.6, delay: 0.8 }, style: {
                                fontFamily: '"Press Start 2P", "Courier New", monospace',
                                color: '#f8ecd7',
                                fontSize: 'clamp(1rem, 2.5vw, 1.4rem)',
                                textAlign: 'center',
                                marginBottom: '2rem',
                                letterSpacing: '0.1em',
                                textShadow: '3px 3px 0px #000000',
                                imageRendering: 'pixelated',
                            }, children: stage === 'input' ? 'DESCRIBE YOUR WORLD' : 'CUSTOMIZE SETTINGS' }), _jsxs(AnimatePresence, { mode: "wait", children: [stage === 'input' && (_jsxs(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0, y: -20 }, transition: { duration: 0.4 }, children: [_jsxs(motion.div, { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.4, delay: 1.2 }, className: "relative", children: [_jsxs(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.32, delay: 1.2 }, style: {
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
                                                    }, children: [_jsx("textarea", { value: worldDescription, onChange: (e) => setWorldDescription(e.target.value), onFocus: () => setIsFocused(true), onBlur: () => setIsFocused(false), placeholder: "A mystical forest where time stands still...", rows: 4, style: {
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
                                                            }, className: "placeholder:text-[#8a9ac7] placeholder:opacity-60" }), _jsxs(motion.button, { whileHover: { scale: 1.1, opacity: 1 }, whileTap: { scale: 0.95 }, onClick: () => fileInputRef.current?.click(), style: {
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
                                                            }, className: "group", children: [_jsx(Image, { size: 20, style: {
                                                                        color: '#00e5e5',
                                                                        opacity: 0.8,
                                                                    }, className: "group-hover:opacity-100 transition-opacity" }), _jsx("span", { style: {
                                                                        fontFamily: '"Courier New", Courier, monospace',
                                                                        fontSize: '0.75rem',
                                                                        color: '#00e5e5',
                                                                        opacity: 0.8,
                                                                    }, className: "group-hover:opacity-100 transition-opacity", children: "Upload Image" }), _jsx(motion.div, { initial: { opacity: 0, y: 0 }, whileHover: { opacity: [0, 1, 0], y: -20 }, transition: { duration: 0.8 }, style: {
                                                                        position: 'absolute',
                                                                        top: '-10px',
                                                                        right: '10px',
                                                                    }, children: _jsx(Sparkles, { size: 12, style: { color: '#00e5e5' } }) })] }), _jsx("input", { ref: fileInputRef, type: "file", accept: "image/*", onChange: handleImageUpload, className: "hidden" }), uploadedImage && (_jsx(motion.div, { initial: { opacity: 0, scale: 0.8 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.3 }, style: {
                                                                position: 'absolute',
                                                                bottom: '16px',
                                                                left: '140px',
                                                                width: '40px',
                                                                height: '40px',
                                                                border: '2px solid #00e5e5',
                                                                borderRadius: '4px',
                                                                overflow: 'hidden',
                                                                imageRendering: 'pixelated',
                                                            }, children: _jsx("img", { src: uploadedImage, alt: "Uploaded", style: { width: '100%', height: '100%', objectFit: 'cover' } }) }))] }), _jsx(AnimatePresence, { children: showImageModal && (_jsxs(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 20 }, transition: { duration: 0.25 }, style: {
                                                            marginTop: '16px',
                                                            padding: '20px',
                                                            background: 'rgba(26, 42, 90, 0.8)',
                                                            boxShadow: `
                            0 0 0 2px #1a4a6a,
                            0 0 0 3px #0a2a4a,
                            0 0 0 4px #00e5e5,
                            0 0 12px rgba(0, 229, 229, 0.3)
                          `,
                                                        }, children: [_jsxs(motion.div, { initial: { opacity: 0, x: -20 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.2 }, className: "mb-4", children: [_jsx("label", { style: {
                                                                            fontFamily: '"Press Start 2P", "Courier New", monospace',
                                                                            fontSize: 'clamp(0.6rem, 1.1vw, 0.75rem)',
                                                                            color: '#00e5e5',
                                                                            letterSpacing: '0.08em',
                                                                            display: 'block',
                                                                            marginBottom: '12px',
                                                                        }, children: "Describe this image:" }), _jsx("input", { type: "text", value: imageDescription, onChange: (e) => setImageDescription(e.target.value), placeholder: "A brave knight in silver armor...", style: {
                                                                            width: '100%',
                                                                            padding: '12px',
                                                                            background: 'rgba(10, 20, 50, 0.6)',
                                                                            border: '2px solid #1a4a6a',
                                                                            borderRadius: '0',
                                                                            color: '#f8ecd7',
                                                                            fontFamily: '"Courier New", Courier, monospace',
                                                                            fontSize: '0.95rem',
                                                                            outline: 'none',
                                                                        }, className: "placeholder:text-[#8a9ac7] placeholder:opacity-60" })] }), _jsxs(motion.div, { initial: { opacity: 0, x: 20 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.2, delay: 0.2 }, children: [_jsx("label", { style: {
                                                                            fontFamily: '"Press Start 2P", "Courier New", monospace',
                                                                            fontSize: 'clamp(0.6rem, 1.1vw, 0.75rem)',
                                                                            color: '#00e5e5',
                                                                            letterSpacing: '0.08em',
                                                                            display: 'block',
                                                                            marginBottom: '12px',
                                                                        }, children: "Used as:" }), _jsxs("select", { value: imageCategory, onChange: (e) => setImageCategory(e.target.value), style: {
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
                                                                        }, children: [_jsx("option", { value: "Main Character", children: "Main Character" }), _jsx("option", { value: "Enemy", children: "Enemy" }), _jsx("option", { value: "Environment", children: "Environment" }), _jsx("option", { value: "Other", children: "Other" })] })] }), imageCategory === 'Other' && (_jsx(motion.div, { initial: { opacity: 0, height: 0 }, animate: { opacity: 1, height: 'auto' }, exit: { opacity: 0, height: 0 }, transition: { duration: 0.2 }, className: "mt-3", children: _jsx("input", { type: "text", value: customCategory, onChange: (e) => setCustomCategory(e.target.value), placeholder: "Enter custom category...", style: {
                                                                        width: '100%',
                                                                        padding: '12px',
                                                                        background: 'rgba(10, 20, 50, 0.6)',
                                                                        border: '2px solid #1a4a6a',
                                                                        borderRadius: '0',
                                                                        color: '#f8ecd7',
                                                                        fontFamily: '"Courier New", Courier, monospace',
                                                                        fontSize: '0.9rem',
                                                                        outline: 'none',
                                                                    }, className: "placeholder:text-[#8a9ac7] placeholder:opacity-60" }) })), _jsx("button", { onClick: () => setShowImageModal(false), style: {
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
                                                                }, className: "hover:bg-[rgba(0,229,229,0.3)] transition-colors", children: "DONE" })] })) })] }), _jsx(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.5, delay: 1.4 }, className: "mt-6 flex justify-center", children: _jsxs("div", { style: {
                                                    padding: '4px',
                                                    background: 'rgba(26, 42, 90, 0.6)',
                                                    boxShadow: `
                        0 0 0 2px #1a4a6a,
                        0 0 0 3px #0a2a4a,
                        inset 0 2px 6px rgba(0, 0, 0, 0.4)
                      `,
                                                    display: 'inline-flex',
                                                    gap: '4px',
                                                }, children: [_jsx(motion.button, { whileHover: { scale: 1.05 }, whileTap: { scale: 0.95 }, onClick: () => setGameMode('single'), style: {
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
                                                        }, children: "SINGLE PLAYER" }), _jsx(motion.button, { whileHover: { scale: 1.05 }, whileTap: { scale: 0.95 }, onClick: () => setGameMode('multiplayer'), style: {
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
                                                        }, children: "MULTIPLAYER" })] }) }), _jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.6, delay: 1.6 }, className: "flex justify-center mt-8 mb-12", children: _jsxs(motion.button, { whileHover: { scale: 1.02 }, whileTap: { scale: 0.98, y: 2 }, onClick: handleGenerateSliders, disabled: !worldDescription.trim(), style: {
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
                                                }, children: [_jsx(motion.div, { animate: {
                                                            opacity: [0.3, 0.6, 0.3],
                                                            scale: [1, 1.1, 1],
                                                        }, transition: {
                                                            duration: 2,
                                                            repeat: Infinity,
                                                            ease: 'easeInOut',
                                                        }, style: {
                                                            position: 'absolute',
                                                            inset: '-10px',
                                                            background: 'radial-gradient(circle, rgba(0, 229, 229, 0.3) 0%, transparent 70%)',
                                                            pointerEvents: 'none',
                                                        } }), _jsx("span", { className: "relative z-10", children: "GENERATE BASE SETTINGS" })] }) })] }, "input-stage")), stage === 'sliders' && (_jsxs(motion.div, { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -20 }, transition: { duration: 0.5 }, children: [_jsxs(motion.div, { style: {
                                                padding: '24px',
                                                background: 'rgba(26, 42, 90, 0.5)',
                                                boxShadow: `
                      0 0 0 2px #1a4a6a,
                      0 0 0 3px #0a2a4a,
                      0 0 0 4px #2a5a7a,
                      inset 0 2px 8px rgba(0, 0, 0, 0.4)
                    `,
                                                marginBottom: '24px',
                                            }, children: [_jsx(DynamicSlider, { label: "Horror Level", min: 0, max: 10, value: horrorLevel, onChange: setHorrorLevel, delay: 0.2 }), _jsx(DynamicSlider, { label: "Puzzle Complexity", min: 0, max: 10, value: puzzleComplexity, onChange: setPuzzleComplexity, delay: 0.4 }), _jsx(DynamicSlider, { label: "Age Group", min: 3, max: 18, value: ageGroup, onChange: setAgeGroup, delay: 0.6 }), _jsx(DynamicSlider, { label: "Speed / Chaos", min: 0, max: 10, value: speedChaos, onChange: setSpeedChaos, delay: 0.8 })] }), _jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, transition: { duration: 0.6, delay: 1.2 }, className: "flex justify-center mt-8 mb-12", children: _jsxs(motion.button, { whileHover: { scale: 1.02 }, whileTap: { scale: 0.98, y: 2 }, onClick: handleStartGenerating, style: {
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
                                                }, children: [_jsx(motion.div, { animate: {
                                                            opacity: [0.3, 0.6, 0.3],
                                                            scale: [1, 1.1, 1],
                                                        }, transition: {
                                                            duration: 2,
                                                            repeat: Infinity,
                                                            ease: 'easeInOut',
                                                        }, style: {
                                                            position: 'absolute',
                                                            inset: '-10px',
                                                            background: 'radial-gradient(circle, rgba(0, 229, 229, 0.3) 0%, transparent 70%)',
                                                            pointerEvents: 'none',
                                                        } }), _jsx("span", { className: "relative z-10", children: "START GENERATING" })] }) })] }, "sliders-stage"))] })] }) }), _jsx(AnimatePresence, { children: stage === 'loading' && _jsx(ConstellationLoading, { statusText: loadingStatus }) })] }));
}
