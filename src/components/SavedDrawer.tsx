import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Bookmark, Trash2 } from 'lucide-react';
import type { FactCard } from '../types/fact';

interface SavedDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  savedFacts: FactCard[];
  onRemoveSaved: (id: string) => void;
  onSelectFact: (fact: FactCard) => void;
}

export const SavedDrawer: React.FC<SavedDrawerProps> = ({
  isOpen,
  onClose,
  savedFacts,
  onRemoveSaved,
  onSelectFact,
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end bg-black/75 backdrop-blur-sm">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0"
        />

        {/* Drawer panel */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 26, stiffness: 240 }}
          className="relative z-10 w-full max-w-md bg-[#13141a] border-l border-zinc-800 h-full flex flex-col p-5 shadow-2xl text-left"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-amber-400/10 text-amber-400 border border-amber-400/20">
                <Bookmark className="w-4 h-4 fill-amber-400" />
              </div>
              <div>
                <h3 className="text-base font-bold text-zinc-100">Saved Facts</h3>
                <p className="text-xs text-zinc-500">
                  {savedFacts.length} {savedFacts.length === 1 ? 'fact' : 'facts'} in personal library
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-full bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 transition-colors border border-zinc-700/60"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* List of saved facts */}
          <div className="flex-1 overflow-y-auto no-scrollbar py-4 space-y-2.5">
            {savedFacts.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-zinc-500 space-y-2.5">
                <Bookmark className="w-10 h-10 text-zinc-700 stroke-1" />
                <p className="text-sm font-medium text-zinc-400">No saved facts yet.</p>
                <p className="text-xs text-zinc-500 max-w-xs">
                  Tap the bookmark icon on any card to save interesting facts for later review.
                </p>
              </div>
            ) : (
              savedFacts.map((fact) => (
                <div
                  key={fact.id}
                  onClick={() => {
                    onSelectFact(fact);
                    onClose();
                  }}
                  className="group relative p-3 rounded-2xl bg-zinc-900/80 hover:bg-zinc-800/80 border border-zinc-800/80 transition-all cursor-pointer flex gap-3 items-center"
                >
                  {/* Thumbnail */}
                  <div className="w-14 h-14 rounded-xl overflow-hidden shrink-0 border border-zinc-800 relative">
                    <img
                      src={fact.image.url}
                      alt={fact.image.alt}
                      className="w-full h-full object-cover"
                    />
                    <span className="absolute bottom-0.5 right-0.5 text-[9px]">
                      {fact.categoryIcon}
                    </span>
                  </div>

                  {/* Fact info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                        {fact.categoryLabel}
                      </span>
                      <span className="text-zinc-600 text-[10px]">• {fact.readTimeSeconds}s</span>
                    </div>
                    <h4 className="text-xs font-semibold text-zinc-200 line-clamp-2 leading-snug group-hover:text-white transition-colors">
                      {fact.hookTitle}
                    </h4>
                  </div>

                  {/* Remove button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveSaved(fact.id);
                    }}
                    className="p-1.5 rounded-lg bg-zinc-800/50 hover:bg-rose-500/10 text-zinc-500 hover:text-rose-400 transition-colors"
                    title="Remove from saved"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
