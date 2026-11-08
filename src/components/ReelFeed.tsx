import React, { useRef, useState, useEffect } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';
import type { FactCard, CategoryId } from '../types/fact';
import { FactCardItem } from './FactCardItem';
import { playSwipeSound } from '../utils/sound';
import { recordFactRead } from '../utils/storage';

interface ReelFeedProps {
  facts: FactCard[];
  activeCategory: CategoryId;
  likedIds: string[];
  savedIds: string[];
  onToggleLike: (id: string) => void;
  onToggleSave: (id: string) => void;
  onOpenWikiModal: (fact: FactCard) => void;
  onFactRead: (totalRead: number, streak: number) => void;
}

export const ReelFeed: React.FC<ReelFeedProps> = ({
  facts,
  activeCategory,
  likedIds,
  savedIds,
  onToggleLike,
  onToggleSave,
  onOpenWikiModal,
  onFactRead,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  // Reset scroll position to top ONLY when activeCategory actually changes
  useEffect(() => {
    setActiveIndex(0);
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, [activeCategory]);

  // Track fact reads for streak
  useEffect(() => {
    const currentFact = facts[activeIndex];
    if (currentFact) {
      const stats = recordFactRead(currentFact.id);
      onFactRead(stats.totalRead, stats.streak);
    }
  }, [activeIndex, activeCategory, onFactRead]);

  // Track scroll position to update active card
  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, clientHeight } = containerRef.current;
    const index = Math.round(scrollTop / clientHeight);
    if (index !== activeIndex && index >= 0 && index < facts.length) {
      setActiveIndex(index);
      playSwipeSound();
    }
  };

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['ArrowDown', 'PageDown', ' '].includes(e.key)) {
        e.preventDefault();
        scrollToIndex(activeIndex + 1);
      } else if (['ArrowUp', 'PageUp'].includes(e.key)) {
        e.preventDefault();
        scrollToIndex(activeIndex - 1);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeIndex, facts.length]);

  const scrollToIndex = (index: number) => {
    if (!containerRef.current || index < 0 || index >= facts.length) return;
    containerRef.current.scrollTo({
      top: index * containerRef.current.clientHeight,
      behavior: 'smooth',
    });
  };

  if (facts.length === 0) {
    return (
      <div className="w-full h-screen flex flex-col items-center justify-center text-center p-6 text-zinc-400">
        <p className="text-base font-semibold text-zinc-200 mb-1">No facts in this category</p>
        <p className="text-xs text-zinc-500">Select another topic from the bar above.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#0c0d11]">
      {/* MAIN SNAP REEL FEED CONTAINER */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="w-full h-full overflow-y-scroll snap-y snap-mandatory no-scrollbar scroll-smooth"
      >
        {facts.map((fact, index) => {
          const isNear = Math.abs(index - activeIndex) <= 2;
          const isActive = index === activeIndex;

          return (
            <div
              key={fact.id}
              className="w-full h-screen snap-start snap-always flex flex-col items-center justify-center pt-24 pb-6 px-3 sm:px-4"
            >
              {isNear && (
                <FactCardItem
                  fact={fact}
                  isActive={isActive}
                  isLiked={likedIds.includes(fact.id)}
                  isSaved={savedIds.includes(fact.id)}
                  onToggleLike={onToggleLike}
                  onToggleSave={onToggleSave}
                  onOpenWikiModal={onOpenWikiModal}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* DESKTOP NAV ARROWS */}
      <div className="hidden md:flex fixed right-8 top-1/2 -translate-y-1/2 flex-col gap-2 z-30 pointer-events-none">
        <button
          onClick={() => scrollToIndex(activeIndex - 1)}
          disabled={activeIndex === 0}
          className="p-2.5 rounded-full bg-zinc-900/90 hover:bg-zinc-800 disabled:opacity-20 text-zinc-300 hover:text-white border border-zinc-800 transition-all pointer-events-auto"
          title="Previous fact (Up arrow)"
        >
          <ChevronUp className="w-4 h-4" />
        </button>

        <button
          onClick={() => scrollToIndex(activeIndex + 1)}
          disabled={activeIndex === facts.length - 1}
          className="p-2.5 rounded-full bg-zinc-900/90 hover:bg-zinc-800 disabled:opacity-20 text-zinc-300 hover:text-white border border-zinc-800 transition-all pointer-events-auto"
          title="Next fact (Down arrow / Space)"
        >
          <ChevronDown className="w-4 h-4" />
        </button>
      </div>

      {/* COUNTER PILL */}
      <div className="fixed bottom-3.5 left-1/2 -translate-x-1/2 z-30 pointer-events-none">
        <div className="px-3 py-1 rounded-full bg-zinc-900/90 border border-zinc-800 text-[11px] font-medium text-zinc-400 shadow-sm">
          {activeIndex + 1} of {facts.length}
        </div>
      </div>
    </div>
  );
};
