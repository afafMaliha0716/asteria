import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { LandingPage } from './components/LandingPage';
import { CreativeToolPage } from './components/CreativeToolPage';
import EditPage from './components/EditPage';
import { ConstellationLoading } from './components/ConstellationLoading';

// Define a type for the generation result
export interface GenerationResult {
  message: string;
  title: string;
  description: string;
  python_script: string;
  executable_file: string;
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<'landing' | 'create' | 'edit'>('landing');
  const [showLoadingTransition, setShowLoadingTransition] = useState(false);
  // Add state to hold the result from the creative tool page
  const [generationResult, setGenerationResult] = useState<GenerationResult | null>(null);

  const handleRefineWorld = () => {
    setShowLoadingTransition(true);
    setTimeout(() => {
      setShowLoadingTransition(false);
    }, 3000);
  };

  const handleNewProject = () => setCurrentPage('create');
  const handleSaveProject = () => setCurrentPage('landing');

  // This function will now receive the result and update the state
  const handleGenerationComplete = (result: GenerationResult) => {
    setGenerationResult(result);
    setCurrentPage('edit');
  };

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden" style={{ imageRendering: 'pixelated' }}>
      <AnimatePresence mode="wait">
        {currentPage === 'landing' && (
          <motion.div
            key="landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.0, ease: [0.65, 0, 0.35, 1] }}
            className="absolute inset-0 overflow-y-auto"
          >
            <LandingPage onStart={() => setCurrentPage('create')} />
          </motion.div>
        )}

        {currentPage === 'create' && (
          <motion.div
            key="create"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.0, ease: [0.65, 0, 0.35, 1] }}
            className="absolute inset-0 overflow-y-auto"
          >
            {/* Pass the new handler function to CreativeToolPage */}
            <CreativeToolPage onGenerate={handleGenerationComplete} />
          </motion.div>
        )}

        {currentPage === 'edit' && !showLoadingTransition && (
          <motion.div
            key="edit"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.0, ease: [0.65, 0, 0.35, 1] }}
            className="absolute inset-0"
          >
            {/* Pass the result down to EditPage */}
            <EditPage
              result={generationResult}
              onRefineWorld={handleRefineWorld}
              onNewProject={handleNewProject}
              onSaveProject={handleSaveProject}
            />
          </motion.div>
        )}

        {showLoadingTransition && <ConstellationLoading key="refine-loading" />}
      </AnimatePresence>
    </div>
  );
}