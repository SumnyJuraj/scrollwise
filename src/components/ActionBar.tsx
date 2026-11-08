import React, { useState } from 'react';
import { Heart, Bookmark, ExternalLink, Share2, Check } from 'lucide-react';
import { motion } from 'framer-motion';
import type { FactCard } from '../types/fact';
import { playLikeSound, playSaveSound } from '../utils/sound';

interface ActionBarProps {
  fact: FactCard;
  isLiked: boolean;
  isSaved: boolean;
  onToggleLike: (factId: string) => void;
  onToggleSave: (factId: string) => void;
  onOpenWikiModal: (fact: FactCard) => void;
}

export const ActionBar: React.FC<ActionBarProps> = ({
  fact,
  isLiked,
  isSaved,
  onToggleLike,
  onToggleSave,
  onOpenWikiModal,
}) => {
  const [copied, setCopied] = useState(false);

  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    playLikeSound();
    onToggleLike(fact.id);
  };

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    playSaveSound();
    onToggleSave(fact.id);
  };

  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const shareText = `🧠 ScrollWise Fact:\n${fact.hookTitle}\n\nRead more: ${fact.source.url}`;
    try {
      if (navigator.share) {
        await navigator.share({
          title: fact.hookTitle,
          text: shareText,
          url: fact.source.url,
        });
      } else {
        await navigator.clipboard.writeText(shareText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // User cancelled share
    }
  };

  const displayLikes = fact.likesCount + (isLiked ? 1 : 0);

  return (
    <div className="flex flex-col items-center gap-3.5 py-1">
      {/* 1. LIKE BUTTON */}
      <div className="flex flex-col items-center">
        <motion.button
          whileTap={{ scale: 0.8 }}
          whileHover={{ scale: 1.08 }}
          onClick={handleLike}
          className={`p-2.5 rounded-full transition-all duration-200 border ${
            isLiked
              ? 'bg-rose-500/20 text-rose-400 border-rose-500/40 shadow-sm'
              : 'bg-zinc-800/80 text-zinc-300 hover:text-white hover:bg-zinc-700/80 border-zinc-700/60'
          }`}
          title={isLiked ? 'Liked' : 'Like'}
        >
          <Heart
            className={`w-5 h-5 transition-colors ${
              isLiked ? 'fill-rose-400 text-rose-400' : 'text-zinc-200'
            }`}
          />
        </motion.button>
        <span className="text-[10px] font-semibold text-zinc-400 mt-1">
          {displayLikes > 999 ? `${(displayLikes / 1000).toFixed(1)}k` : displayLikes}
        </span>
      </div>

      {/* 2. SAVE / BOOKMARK BUTTON */}
      <div className="flex flex-col items-center">
        <motion.button
          whileTap={{ scale: 0.8 }}
          whileHover={{ scale: 1.08 }}
          onClick={handleSave}
          className={`p-2.5 rounded-full transition-all duration-200 border ${
            isSaved
              ? 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-sm'
              : 'bg-zinc-800/80 text-zinc-300 hover:text-white hover:bg-zinc-700/80 border-zinc-700/60'
          }`}
          title={isSaved ? 'Saved to library' : 'Save fact'}
        >
          <Bookmark
            className={`w-5 h-5 transition-colors ${
              isSaved ? 'fill-amber-400 text-amber-400' : 'text-zinc-200'
            }`}
          />
        </motion.button>
        <span className="text-[10px] font-medium text-zinc-400 mt-1">
          {isSaved ? 'Saved' : 'Save'}
        </span>
      </div>

      {/* 3. WIKIPEDIA MODAL TRIGGER */}
      <div className="flex flex-col items-center">
        <motion.button
          whileTap={{ scale: 0.8 }}
          whileHover={{ scale: 1.08 }}
          onClick={(e) => {
            e.stopPropagation();
            onOpenWikiModal(fact);
          }}
          className="p-2.5 rounded-full bg-zinc-800/80 hover:bg-zinc-700/80 text-zinc-300 hover:text-white border border-zinc-700/60 transition-colors"
          title="Wikipedia article summary"
        >
          <div className="relative flex items-center justify-center w-5 h-5">
            <span className="font-serif font-black text-sm text-zinc-200">W</span>
            <ExternalLink className="w-2.5 h-2.5 absolute -top-0.5 -right-1 text-zinc-400" />
          </div>
        </motion.button>
        <span className="text-[10px] font-medium text-zinc-400 mt-1">Wiki</span>
      </div>

      {/* 4. SHARE BUTTON */}
      <div className="flex flex-col items-center">
        <motion.button
          whileTap={{ scale: 0.8 }}
          whileHover={{ scale: 1.08 }}
          onClick={handleShare}
          className="p-2.5 rounded-full bg-zinc-800/80 text-zinc-300 hover:text-white hover:bg-zinc-700/80 border border-zinc-700/60 transition-colors"
          title="Share fact"
        >
          {copied ? (
            <Check className="w-5 h-5 text-emerald-400" />
          ) : (
            <Share2 className="w-5 h-5" />
          )}
        </motion.button>
        <span className="text-[10px] font-medium text-zinc-400 mt-1">
          {copied ? 'Copied' : 'Share'}
        </span>
      </div>
    </div>
  );
};
