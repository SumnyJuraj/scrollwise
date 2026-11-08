import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, CheckCircle2, Sparkles, Heart } from 'lucide-react';
import type { FactCard } from '../types/fact';
import { ActionBar } from './ActionBar';
import { playLikeSound } from '../utils/sound';
import { getCategoryFallbackImage } from '../data/factsRepository';

interface FactCardItemProps {
  fact: FactCard;
  isActive: boolean;
  isLiked: boolean;
  isSaved: boolean;
  onToggleLike: (id: string) => void;
  onToggleSave: (id: string) => void;
  onOpenWikiModal: (fact: FactCard) => void;
}

export const FactCardItem: React.FC<FactCardItemProps> = ({
  fact,
  isActive,
  isLiked,
  isSaved,
  onToggleLike,
  onToggleSave,
  onOpenWikiModal,
}) => {
  const [showHeartBurst, setShowHeartBurst] = useState(false);
  const [imgSrc, setImgSrc] = useState(fact.image.url);

  useEffect(() => {
    setImgSrc(fact.image.url);
  }, [fact.image.url]);

  // Guaranteed genuine photograph - reject SVGs or icons and immediately use category photography
  const displayImgSrc =
    !imgSrc ||
    imgSrc.includes('.svg') ||
    imgSrc.includes('logo') ||
    imgSrc.includes('icon') ||
    imgSrc.includes('flag') ||
    imgSrc.includes('symbol')
      ? getCategoryFallbackImage(fact.category)
      : imgSrc;

  // Double-tap to like gesture
  const handleDoubleTap = () => {
    if (!isLiked) {
      onToggleLike(fact.id);
    }
    playLikeSound();
    setShowHeartBurst(true);
    setTimeout(() => setShowHeartBurst(false), 800);
  };

  return (
    <div
      className="relative w-full h-full flex flex-col items-center justify-center select-none"
      onDoubleClick={handleDoubleTap}
    >
      {/* MAIN CARD - Clean, refined, non-AI aesthetic */}
      <motion.div
        initial={{ opacity: 0.9, scale: 0.98 }}
        animate={{ opacity: 1, scale: isActive ? 1 : 0.97 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="relative w-full max-w-[430px] h-full max-h-[720px] rounded-3xl overflow-hidden flex flex-col justify-between shadow-2xl bg-[#14151a] border border-zinc-800/80 p-4 sm:p-5"
      >
        {/* 1. TOP HEADER BAR */}
        <div className="relative z-10 flex items-center justify-between pb-3.5 border-b border-zinc-800/60 shrink-0">
          {/* Category Pill */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-800/70 border border-zinc-700/50 text-zinc-200">
            <span className="text-sm">{fact.categoryIcon}</span>
            <span className="text-xs font-semibold tracking-wide">
              {fact.categoryLabel}
            </span>
          </div>

          {/* Read time & Verified Pill */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-[11px] font-medium">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              <span>{fact.readTimeSeconds}s read</span>
            </div>

            <div
              className="p-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
              title="Verified Wikipedia source"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>

        {/* 2. CARD BODY: TEXT AT THE TOP + ACTION BAR ON RIGHT */}
        <div className="relative z-10 flex items-start justify-between gap-4 pt-4 shrink-0">
          {/* TEXT AREA */}
          <div className="flex-1 min-w-0 text-left">
            {/* Hook Headline */}
            <h2 className="text-lg sm:text-xl font-bold text-zinc-100 leading-snug tracking-tight mb-2.5">
              {fact.hookTitle}
            </h2>

            {/* 15-second concise story */}
            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed font-normal mb-3">
              {fact.snippet}
            </p>

            {/* Key Metric Pill */}
            {fact.keyStat && (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900/90 border border-zinc-700/60 mb-2.5 w-fit">
                <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] uppercase font-semibold text-zinc-400 tracking-wider">
                    {fact.keyStat.label}:
                  </span>
                  <span className="text-xs font-bold text-zinc-100 tracking-wide">
                    {fact.keyStat.value}
                  </span>
                </div>
              </div>
            )}


          </div>

          {/* RIGHT FLOATING ACTION BAR */}
          <div className="shrink-0">
            <ActionBar
              fact={fact}
              isLiked={isLiked}
              isSaved={isSaved}
              onToggleLike={onToggleLike}
              onToggleSave={onToggleSave}
              onOpenWikiModal={onOpenWikiModal}
            />
          </div>
        </div>

        {/* 3. IMAGE AT THE BOTTOM - EXPANDS TO FILL ALL REMAINING SPACE */}
        <div className="relative z-10 flex-1 min-h-[200px] w-full rounded-2xl overflow-hidden border border-zinc-800 group shadow-inner mt-4 bg-zinc-900">
          <img
            src={displayImgSrc}
            alt={fact.image.alt}
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={() => {
              setImgSrc(getCategoryFallbackImage(fact.category));
            }}
            className="w-full h-full object-cover object-center transform transition-transform duration-700 group-hover:scale-105"
          />
          {/* Subtle bottom gradient overlay for caption contrast */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent pointer-events-none" />

          {/* Image caption badge */}
          <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between text-[11px] text-zinc-300 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-xl border border-white/10">
            <span className="truncate font-medium">
              {fact.image.caption || fact.image.alt}
            </span>
            <span className="text-xs ml-2 shrink-0 opacity-80">
              {fact.categoryIcon}
            </span>
          </div>
        </div>
      </motion.div>

      {/* DOUBLE TAP HEART BURST ANIMATION */}
      <AnimatePresence>
        {showHeartBurst && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [0, 1.25, 1], opacity: [0, 1, 0] }}
            exit={{ scale: 1.4, opacity: 0 }}
            transition={{ duration: 0.75, ease: 'easeOut' }}
            className="absolute inset-0 flex items-center justify-center pointer-events-none z-50"
          >
            <div className="p-5 rounded-full bg-red-500/20 backdrop-blur-xl border border-red-500/40 shadow-xl">
              <Heart className="w-20 h-20 fill-red-500 text-red-500 drop-shadow-lg" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
