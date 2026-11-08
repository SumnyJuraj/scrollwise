import { useState, useEffect, useMemo, useCallback } from 'react';
import type { CategoryId, FactCard } from './types/fact';
import { ALL_FACTS, getFactsByCategory } from './data/factsRepository';
import { ReelFeed } from './components/ReelFeed';
import { TopBar } from './components/TopBar';
import { CategoryBar } from './components/CategoryBar';
import { CategoryModal } from './components/CategoryModal';
import { WikipediaModal } from './components/WikipediaModal';
import { SavedDrawer } from './components/SavedDrawer';
import {
  getLikedFactIds,
  toggleLikedFactId,
  getSavedFactIds,
  toggleSavedFactId,
  getSoundPreference,
  setSoundPreference,
} from './utils/storage';

export function App() {
  const [activeCategory, setActiveCategory] = useState<CategoryId>('all');
  const [likedIds, setLikedIds] = useState<string[]>([]);
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [soundEnabled, setSoundEnabledState] = useState<boolean>(true);
  const [selectedWikiFact, setSelectedWikiFact] = useState<FactCard | null>(null);
  const [isSavedDrawerOpen, setIsSavedDrawerOpen] = useState(false);
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [streakCount, setStreakCount] = useState(1);
  const [totalReadCount, setTotalReadCount] = useState(0);

  // Inicializácia z LocalStorage
  useEffect(() => {
    setLikedIds(getLikedFactIds());
    setSavedIds(getSavedFactIds());
    setSoundEnabledState(getSoundPreference());
  }, []);

  const handleToggleLike = useCallback((factId: string) => {
    const { allLiked } = toggleLikedFactId(factId);
    setLikedIds(allLiked);
  }, []);

  const handleToggleSave = useCallback((factId: string) => {
    const { allSaved } = toggleSavedFactId(factId);
    setSavedIds(allSaved);
  }, []);

  const handleToggleSound = useCallback(() => {
    setSoundEnabledState((prev) => {
      const newState = !prev;
      setSoundPreference(newState);
      return newState;
    });
  }, []);

  const handleFactRead = useCallback((totalRead: number, streak: number) => {
    setTotalReadCount((prev) => (prev !== totalRead ? totalRead : prev));
    setStreakCount((prev) => (prev !== streak ? streak : prev));
  }, []);

  // Filtrované fakty podľa kategórie - stabilná pamäť bez zbytočného prekresľovania
  const currentFacts = useMemo(() => getFactsByCategory(activeCategory), [activeCategory]);

  // Uložené kartičky pre SavedDrawer
  const savedFactObjects = useMemo(
    () => ALL_FACTS.filter((f) => savedIds.includes(f.id)),
    [savedIds]
  );

  // Počty faktov pre jednotlivé kategórie
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: ALL_FACTS.length };
    for (const f of ALL_FACTS) {
      counts[f.category] = (counts[f.category] || 0) + 1;
    }
    return counts;
  }, []);

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#090a0f] text-white">
      {/* 1. HORNÝ PANEL (TopBar) */}
      <TopBar
        savedCount={savedIds.length}
        streakCount={streakCount}
        totalReadCount={totalReadCount}
        soundEnabled={soundEnabled}
        onToggleSound={handleToggleSound}
        onOpenSaved={() => setIsSavedDrawerOpen(true)}
      />

      {/* 2. PREPÍNAČ KATEGÓRIÍ (CategoryBar) */}
      <CategoryBar
        activeCategory={activeCategory}
        onSelectCategory={setActiveCategory}
        onOpenExplore={() => setIsCategoryModalOpen(true)}
      />

      {/* 3. REELS FEED S VERTIKÁLNYM SNAP-SCROLLOM */}
      <ReelFeed
        facts={currentFacts}
        activeCategory={activeCategory}
        likedIds={likedIds}
        savedIds={savedIds}
        onToggleLike={handleToggleLike}
        onToggleSave={handleToggleSave}
        onOpenWikiModal={setSelectedWikiFact}
        onFactRead={handleFactRead}
      />

      {/* 4. MODAL PRE PREHĽAD VŠETKÝCH KATEGÓRIÍ */}
      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        activeCategory={activeCategory}
        onSelectCategory={setActiveCategory}
        categoryCounts={categoryCounts}
      />

      {/* 5. MODAL PRE WIKIPÉDIA ZDROJ */}
      <WikipediaModal
        fact={selectedWikiFact}
        onClose={() => setSelectedWikiFact(null)}
      />

      {/* 6. BOČNÝ DRAWER PRE ULOŽENÉ FAKTY */}
      <SavedDrawer
        isOpen={isSavedDrawerOpen}
        onClose={() => setIsSavedDrawerOpen(false)}
        savedFacts={savedFactObjects}
        onRemoveSaved={handleToggleSave}
        onSelectFact={(fact) => {
          setSelectedWikiFact(fact);
        }}
      />
    </div>
  );
}

export default App;
