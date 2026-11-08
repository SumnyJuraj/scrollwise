import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, Check } from 'lucide-react';
import type { CategoryId } from '../types/fact';
import { CATEGORIES } from '../data/categories';

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeCategory: CategoryId;
  onSelectCategory: (categoryId: CategoryId) => void;
  categoryCounts?: Record<string, number>;
}

export const CategoryModal: React.FC<CategoryModalProps> = ({
  isOpen,
  onClose,
  activeCategory,
  onSelectCategory,
  categoryCounts = {},
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  const filteredCategories = CATEGORIES.filter(
    (c) =>
      c.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/80 backdrop-blur-md"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 16 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-2xl max-h-[85vh] bg-[#14151a] border border-zinc-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden text-zinc-100"
        >
          {/* Header */}
          <div className="px-6 pt-6 pb-4 border-b border-zinc-800/80 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-zinc-100">Browse Topics</h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                Choose any knowledge domain to explore bite-sized facts
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white border border-zinc-800 transition-colors"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Search Input */}
          <div className="px-6 pt-4 pb-2">
            <div className="relative">
              <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search topics (e.g., Cinema, Philosophy, Math)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-zinc-900/90 text-sm text-zinc-200 placeholder-zinc-500 pl-10 pr-4 py-2.5 rounded-xl border border-zinc-800 focus:outline-none focus:border-zinc-500 transition-colors"
              />
            </div>
          </div>

          {/* Categories Grid */}
          <div className="p-6 overflow-y-auto no-scrollbar grid grid-cols-1 sm:grid-cols-2 gap-3">
            {filteredCategories.map((cat) => {
              const isActive = activeCategory === cat.id;
              const count = categoryCounts[cat.id];

              return (
                <button
                  key={cat.id}
                  onClick={() => {
                    onSelectCategory(cat.id);
                    onClose();
                  }}
                  className={`text-left p-3.5 rounded-2xl border transition-all flex items-start gap-3.5 group relative ${
                    isActive
                      ? 'bg-zinc-800/90 border-zinc-400 shadow-sm'
                      : 'bg-zinc-900/60 hover:bg-zinc-900 border-zinc-800/80 hover:border-zinc-700'
                  }`}
                >
                  {/* Category Icon */}
                  <div className="w-10 h-10 rounded-xl bg-zinc-800/80 border border-zinc-700/60 flex items-center justify-center text-xl shrink-0 group-hover:scale-105 transition-transform">
                    {cat.icon}
                  </div>

                  {/* Title & Description */}
                  <div className="flex-1 min-w-0 pr-6">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm text-zinc-100 truncate">
                        {cat.label}
                      </span>
                      {count !== undefined && count > 0 && (
                        <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50">
                          {count}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-zinc-400 line-clamp-2 mt-1 leading-relaxed">
                      {cat.description}
                    </p>
                  </div>

                  {/* Active Indicator */}
                  {isActive && (
                    <div className="absolute top-3.5 right-3.5 w-5 h-5 rounded-full bg-zinc-100 text-zinc-950 flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Footer */}
          <div className="px-6 py-3 bg-zinc-900/40 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-500">
            <span>{CATEGORIES.length} Topics Available</span>
            <button
              onClick={() => {
                onSelectCategory('all');
                onClose();
              }}
              className="text-zinc-400 hover:text-white underline underline-offset-2"
            >
              Reset to All Topics
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
