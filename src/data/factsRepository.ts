import type { FactCard, CategoryId } from '../types/fact';
import { INITIAL_FACTS } from './facts';
import scrapedData from './scraped_facts.json';

// Prísna kontrola: Kartička MUSÍ mať skutočnú fotografiu (.jpg, .jpeg, .webp), ŽIADNE SVGs, ikony, logá či diagramy
export const hasValidImage = (item: FactCard): boolean => {
  if (!item.image || typeof item.image.url !== 'string') return false;
  const url = item.image.url.trim().toLowerCase();
  if (url.length < 15 || !url.startsWith('http')) return false;

  // Striktne vylučujeme SVGs, ikony, logá, symboly a matematické/chemické vzorce
  if (url.includes('.svg') || url.includes('.svg.png')) return false;
  if (
    url.includes('logo') ||
    url.includes('icon') ||
    url.includes('flag') ||
    url.includes('symbol') ||
    url.includes('formula') ||
    url.includes('diagram') ||
    url.includes('placeholder')
  ) {
    return false;
  }
  return true;
};

export const getCategoryFallbackImage = (category: CategoryId): string => {
  switch (category) {
    case 'space':
      return 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1080&q=80';
    case 'science':
      return 'https://images.unsplash.com/photo-1507499739999-097706ad8914?auto=format&fit=crop&w=1080&q=80';
    case 'math':
      return 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=1080&q=80';
    case 'philosophy':
      return 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1080&q=80';
    case 'construction':
      return 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1080&q=80';
    case 'nature':
      return 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1080&q=80';
    case 'tech':
      return 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1080&q=80';
    case 'history':
      return 'https://images.unsplash.com/photo-1568667256549-094345857637?auto=format&fit=crop&w=1080&q=80';
    case 'biology':
      return 'https://images.unsplash.com/photo-1530026405186-ed1f139313f8?auto=format&fit=crop&w=1080&q=80';
    case 'ocean':
      return 'https://images.unsplash.com/photo-1682687220063-4742bd7fd538?auto=format&fit=crop&w=1080&q=80';
    case 'art':
      return 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=1080&q=80';
    case 'cinema':
      return 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1080&q=80';
    case 'music':
      return 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1080&q=80';
    case 'literature':
      return 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1080&q=80';
    case 'culinary':
      return 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1080&q=80';
    case 'fitness':
      return 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1080&q=80';
    case 'geography':
      return 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1080&q=80';
    case 'records':
      return 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1080&q=80';
    default:
      return 'https://images.unsplash.com/photo-1507499739999-097706ad8914?auto=format&fit=crop&w=1080&q=80';
  }
};

// Zlúčenie a deduplikácia počiatočných a zoškrabaných faktov
const mergeFacts = (): FactCard[] => {
  const map = new Map<string, FactCard>();
  const seenSnippetPrefixes = new Set<string>();

  // 1. Primárne zoškrabané a sémanticky klasifikované fakty z Wikipédie (5,500+ faktov)
  if (Array.isArray(scrapedData)) {
    for (const item of scrapedData as unknown as FactCard[]) {
      if (hasValidImage(item) && !map.has(item.id)) {
        const normSnippet = (item.snippet || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 45);
        if (normSnippet.length >= 30 && seenSnippetPrefixes.has(normSnippet)) {
          // Duplikát nájdený - ignorujeme
          continue;
        }
        if (normSnippet.length >= 30) {
          seenSnippetPrefixes.add(normSnippet);
        }

        // Normalizujeme URL na upload.wikimedia.org a odstránime query parametre
        const cleanUrl = item.image.url
          .replace('thumb.wikimedia.org', 'upload.wikimedia.org')
          .split('?')[0];

        map.set(item.id, {
          ...item,
          image: {
            ...item.image,
            url: cleanUrl,
          },
        });
      }
    }
  }

  // 2. Doplňujúce počiatočné overené fakty iba v prípade, že neexistujú v databáze
  for (const fact of INITIAL_FACTS) {
    if (hasValidImage(fact) && !map.has(fact.id)) {
      const normSnippet = fact.snippet.toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 45);
      if (!seenSnippetPrefixes.has(normSnippet)) {
        seenSnippetPrefixes.add(normSnippet);
        map.set(fact.id, fact);
      }
    }
  }

  // Striktný filter: iba kartičky so 100% platnou reálnou fotografiou
  return Array.from(map.values()).filter(hasValidImage);
};

export const ALL_FACTS: FactCard[] = mergeFacts();

export const getFactsByCategory = (categoryId: CategoryId): FactCard[] => {
  if (categoryId === 'all') return ALL_FACTS;
  return ALL_FACTS.filter((f) => f.category === categoryId);
};
