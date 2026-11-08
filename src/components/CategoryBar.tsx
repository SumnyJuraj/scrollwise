import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid } from 'lucide-react';
import type { CategoryId } from '../types/fact';
import { CATEGORIES } from '../data/categories';

interface CategoryBarProps {
  activeCategory: CategoryId;
  onSelectCategory: (categoryId: CategoryId) => void;
  onOpenExplore?: () => void;
}

export const CategoryBar: React.FC<CategoryBarProps> = ({
  activeCategory,
  onSelectCategory,
  onOpenExplore,
}) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const activeBtnRef = useRef<HTMLButtonElement>(null);

  // Auto-scroll active pill into view when activeCategory changes
  useEffect(() => {
    if (activeBtnRef.current) {
      activeBtnRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'center',
      });
    }
  }, [activeCategory]);

  return (
    <div className="fixed top-14 left-0 right-0 z-30 flex justify-center px-3 sm:px-4 py-2 pointer-events-none">
      <div
        ref={scrollContainerRef}
        className="flex items-center gap-1.5 overflow-x-auto no-scrollbar max-w-full px-2 py-1 pointer-events-auto"
      >
        {/* Explore all topics grid modal trigger */}
        {onOpenExplore && (
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onOpenExplore}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-700/70 shadow-sm backdrop-blur-md shrink-0 transition-colors"
            title="Browse all 18 topics"
          >
            <LayoutGrid className="w-3.5 h-3.5 text-zinc-400" />
            <span className="hidden xs:inline">Browse</span>
          </motion.button>
        )}

        {/* Category Pills */}
        {CATEGORIES.map((cat) => {
          const isActive = activeCategory === cat.id;

          return (
            <motion.button
              key={cat.id}
              ref={isActive ? activeBtnRef : undefined}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSelectCategory(cat.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors duration-150 border shrink-0 ${
                isActive
                  ? 'bg-zinc-100 text-zinc-950 border-white font-semibold shadow-sm'
                  : 'bg-zinc-900/85 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border-zinc-800/80 backdrop-blur-sm'
              }`}
            >
              <span className="text-xs">{cat.icon}</span>
              <span>{cat.label}</span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};
