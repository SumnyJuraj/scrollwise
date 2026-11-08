import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, BookOpen, Sparkles, CheckCircle2 } from 'lucide-react';
import type { FactCard } from '../types/fact';

interface WikipediaModalProps {
  fact: FactCard | null;
  onClose: () => void;
}

export const WikipediaModal: React.FC<WikipediaModalProps> = ({ fact, onClose }) => {
  if (!fact) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80 backdrop-blur-sm">
        {/* Backdrop click to close */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0"
        />

        {/* Modal Sheet Content */}
        <motion.div
          initial={{ y: '100%', opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: '100%', opacity: 0 }}
          transition={{ type: 'spring', damping: 26, stiffness: 260 }}
          className="relative z-10 w-full max-w-lg bg-[#14151b] border-t sm:border border-zinc-800 rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl text-left overflow-hidden max-h-[85vh] flex flex-col"
        >
          {/* Top handle bar for mobile feel */}
          <div className="w-10 h-1 bg-zinc-700 rounded-full mx-auto mb-4 sm:hidden" />

          {/* Header */}
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-zinc-800 border border-zinc-700/80 flex items-center justify-center shadow-sm">
                <span className="font-serif font-black text-xl text-zinc-100">W</span>
              </div>
              <div>
                <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-semibold uppercase tracking-wider">
                  <BookOpen className="w-3.5 h-3.5" />
                  <span>Wikipedia Reference</span>
                </div>
                <h3 className="text-lg font-bold text-zinc-100 leading-snug">
                  {fact.source.title}
                </h3>
              </div>
            </div>

            <button
              onClick={onClose}
              className="p-1.5 rounded-full bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-100 transition-colors border border-zinc-700/60"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Thumbnail */}
          {fact.image.url && (
            <div className="relative w-full h-36 rounded-xl overflow-hidden mb-4 border border-zinc-800">
              <img
                src={fact.image.url}
                alt={fact.image.alt}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#14151b] via-transparent to-transparent" />
              <div className="absolute bottom-2 left-3 text-xs text-zinc-300 font-medium">
                {fact.categoryIcon} {fact.categoryLabel}
              </div>
            </div>
          )}

          {/* Extract / Summary */}
          <div className="flex-1 overflow-y-auto no-scrollbar space-y-3 mb-5 pr-1">
            <div className="p-3 rounded-xl bg-zinc-900 border border-zinc-800">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-300 mb-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Quick Insight</span>
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed font-normal">
                {fact.hookTitle}
              </p>
            </div>

            <div className="text-xs sm:text-sm text-zinc-300 leading-relaxed space-y-2">
              <p>
                {fact.source.extract || fact.snippet}
              </p>
            </div>

            {fact.keyStat && (
              <div className="flex items-center gap-2 p-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>
                  <strong className="text-zinc-200">{fact.keyStat.label}:</strong> {fact.keyStat.value}
                </span>
              </div>
            )}
          </div>

          {/* Primary Action Button: Open Wikipedia */}
          <div className="pt-2">
            <a
              href={fact.source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-xl bg-zinc-100 hover:bg-white text-zinc-950 font-semibold text-sm transition-all shadow-md active:scale-[0.99]"
            >
              <span>Read Full Article on Wikipedia</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
