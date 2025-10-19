import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { LandingPage } from './components/LandingPage';
import { CreativeToolPage } from './components/CreativeToolPage';
import EditPage from './components/EditPage';
import { ConstellationLoading } from './components/ConstellationLoading';

export default function App() {
  const [currentPage, setCurrentPage] = useState<'landing' | 'create' | 'edit'>('landing');
  const [showLoadingTransition, setShowLoadingTransition] = useState(false);

  const handleRefineWorld = () => {
    setShowLoadingTransition(true);
    setTimeout(() => {
      setShowLoadingTransition(false);
    }, 3000);
  };

  const handleNewProject = () => setCurrentPage('create');
  const handleSaveProject = () => setCurrentPage('landing');

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
            <CreativeToolPage onGenerate={() => setCurrentPage('edit')} />
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
            <EditPage
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
