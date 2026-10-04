import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { LandingPage } from './components/LandingPage';
import { CreativeToolPage } from './components/CreativeToolPage';
import EditPage from './components/EditPage';
import { ConstellationLoading } from './components/ConstellationLoading';
export default function App() {
    const [currentPage, setCurrentPage] = useState('landing');
    const [showLoadingTransition, setShowLoadingTransition] = useState(false);
    // Add state to hold the result from the creative tool page
    const [generationResult, setGenerationResult] = useState(null);
    const handleRefineWorld = () => {
        setShowLoadingTransition(true);
        setTimeout(() => {
            setShowLoadingTransition(false);
        }, 3000);
    };
    const handleNewProject = () => setCurrentPage('create');
    const handleSaveProject = () => setCurrentPage('landing');
    // This function will now receive the result and update the state
    const handleGenerationComplete = (result) => {
        setGenerationResult(result);
        setCurrentPage('edit');
    };
    return (_jsx("div", { className: "relative min-h-screen w-full overflow-x-hidden", style: { imageRendering: 'pixelated' }, children: _jsxs(AnimatePresence, { mode: "wait", children: [currentPage === 'landing' && (_jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 1.0, ease: [0.65, 0, 0.35, 1] }, className: "absolute inset-0 overflow-y-auto", children: _jsx(LandingPage, { onStart: () => setCurrentPage('create') }) }, "landing")), currentPage === 'create' && (_jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 1.0, ease: [0.65, 0, 0.35, 1] }, className: "absolute inset-0 overflow-y-auto", children: _jsx(CreativeToolPage, { onGenerate: handleGenerationComplete }) }, "create")), currentPage === 'edit' && !showLoadingTransition && (_jsx(motion.div, { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 }, transition: { duration: 1.0, ease: [0.65, 0, 0.35, 1] }, className: "absolute inset-0", children: _jsx(EditPage, { result: generationResult, onRefineWorld: handleRefineWorld, onNewProject: handleNewProject, onSaveProject: handleSaveProject }) }, "edit")), showLoadingTransition && _jsx(ConstellationLoading, {}, "refine-loading")] }) }));
}
