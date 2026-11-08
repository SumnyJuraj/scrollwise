export type CategoryId =
  | 'all'
  | 'space'
  | 'science'
  | 'math'
  | 'philosophy'
  | 'construction'
  | 'nature'
  | 'ocean'
  | 'biology'
  | 'history'
  | 'geography'
  | 'tech'
  | 'art'
  | 'cinema'
  | 'music'
  | 'literature'
  | 'culinary'
  | 'fitness'
  | 'records';

export interface CategoryMeta {
  id: CategoryId;
  label: string;
  icon: string;
  color: string;
  gradient: string;
  description: string;
}

export interface FactSource {
  title: string;
  url: string;
  extract?: string;
  language?: string;
}

export interface FactImage {
  url: string;
  alt: string;
  style: 'illustration' | 'vector' | 'photo' | 'graphic';
  caption?: string;
  credit?: string;
}

export interface FactCard {
  id: string;
  category: CategoryId;
  categoryLabel: string;
  categoryIcon: string;
  accentColor: string;
  readTimeSeconds: number; // e.g. 10 - 15 seconds
  hookTitle: string; // Catchy punchline / hook
  snippet: string; // 2-3 sentences explaining the fact
  keyStat?: {
    label: string;
    value: string;
  };
  image: FactImage;
  source: FactSource;
  tags: string[];
  likesCount: number;
  verified: boolean;
}
