import React from 'react';
import { Sparkles, Flame, Bookmark, Volume2, VolumeX } from 'lucide-react';

interface TopBarProps {
  savedCount: number;
  streakCount: number;
  totalReadCount: number;
  soundEnabled: boolean;
  onToggleSound: () => void;
  onOpenSaved: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({
  savedCount,
  streakCount,
  totalReadCount,
  soundEnabled,
  onToggleSound,
  onOpenSaved,
}) => {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 px-4 py-3 flex items-center justify-between pointer-events-none">
      {/* Left side: ScrollWise Brand */}
      <div className="flex items-center gap-2.5 pointer-events-auto">
        <div className="w-8 h-8 rounded-xl bg-zinc-800 border border-zinc-700/80 flex items-center justify-center text-zinc-100 shadow-sm">
          <Sparkles className="w-4 h-4 text-amber-400" />
        </div>
        <div className="flex flex-col text-left">
          <span className="font-bold text-sm tracking-tight text-zinc-100">
            Scroll<span className="text-zinc-400 font-medium">Wise</span>
          </span>
          <span className="text-[9px] uppercase tracking-wider text-zinc-400 font-medium -mt-0.5">
            15s Feed
          </span>
        </div>
      </div>

      {/* Right side: Streak, Audio, Library */}
      <div className="flex items-center gap-2 pointer-events-auto">
        {/* Streak Counter Pill */}
        <div
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-zinc-900/90 border border-zinc-800 text-zinc-300 text-xs font-semibold shadow-sm"
          title={`You have discovered ${totalReadCount} facts! Daily streak: ${streakCount} day${streakCount > 1 ? 's' : ''}`}
        >
          <Flame className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
          <span>{totalReadCount} read</span>
        </div>

        {/* Audio Toggle */}
        <button
          onClick={onToggleSound}
          className="p-2 rounded-full bg-zinc-900/90 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          title={soundEnabled ? 'Mute sound effects' : 'Enable sound effects'}
        >
          {soundEnabled ? (
            <Volume2 className="w-4 h-4" />
          ) : (
            <VolumeX className="w-4 h-4 text-zinc-600" />
          )}
        </button>

        {/* Saved Facts Library */}
        <button
          onClick={onOpenSaved}
          className="relative p-2 rounded-full bg-zinc-900/90 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          title="Open saved facts"
        >
          <Bookmark className="w-4 h-4 text-amber-400" />
          {savedCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-400 text-zinc-950 font-bold text-[9px] flex items-center justify-center">
              {savedCount}
            </span>
          )}
        </button>
      </div>
    </header>
  );
};
