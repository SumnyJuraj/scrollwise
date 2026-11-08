# 🌟 ScrollWise - Technická Špecifikácia & Dizajn Systém

> **ScrollWise** – Micro-learning aplikácia s nekonečným vertikálnym feedom faktov vo forme moderných kartičiek (Reels / TikTok štýl), zameraná na rýchle 15-sekundové vzdelávanie z každej encyklopedickej oblasti s preklikom na Wikipédiu.

---

## 1. Základná Vízia a Koncept

- **Formát**: Vertikálny reels/TikTok feed so snap-scrollom (`snap-y snap-mandatory`), kde každá obrazovka je samostatná vizuálna kartička s faktom.
- **Dĺžka obsahu**: Maximálne 15 sekúnd čítania (stručný úderný hook + 2-3 vysvetľujúce vety + zvýraznená kľúčová štatistika).
- **Tematická pestrosť**: Fakty z každej oblasti:
  - 🪐 **Space & Astronomy** (`space`)
  - 🧪 **Science & Physics** (`science`)
  - 📐 **Mathematics & Paradoxes** (`math`)
  - 🏛️ **Philosophy & Thought Experiments** (`philosophy`)
  - 🏗️ **Engineering & Mega-Structures** (`construction`)
  - 🌿 **Nature & Wildlife** (`nature`)
  - 🌊 **Deep Ocean & Abyssal Wonders** (`ocean`)
  - 🧬 **Biology & Neuroscience** (`biology`)
  - 📜 **History & Ancient Civilizations** (`history`)
  - 🗺️ **Geography & Earth Superlatives** (`geography`)
  - ⚡ **Technology & Inventions** (`tech`)
  - 🎨 **Art & Sculpture** (`art`)
  - 🎬 **Cinema & Practical Effects** (`cinema`)
  - 🎵 **Music & Acoustic Science** (`music`)
  - 📚 **Books & Classical Literature** (`literature`)
  - 🍳 **Food Science & Culinary Arts** (`culinary`)
  - 🏃 **Fitness & Exercise Physiology** (`fitness`)
  - 🏆 **World Records & Extreme Feats** (`records`)
- **Odkaz na zdroj**: Každý fakt pochádza z overiteľného článku na Wikipédii / encyklopédii a obsahuje priamy interaktívny preklik a in-app náhľad.
- **Jazyk**: Celá aplikácia, texty, dáta a scraper sú plne v angličtine (English).
- **Vizuálny štýl**: Čistý, minimalistický, príjemný a "ľudský" dizajn (odstránené krikľavé AI fialové neónové podsvietenia a prehnané tiene). Elegantný matný grafitový/zinc podklad (`#14151a`), decentné 1px orámovania a prirodzená typografia.

---

## 2. UI / UX Dizajn Systém ("Card Reels")

### 2.1 Anatómia Kartičky (Fact Card)
Každá kartička je centrovaná v mobilnom / reels viewport ráme:
1. **Horná lišta (Header)**:
   - Kategória s neutrálnou fav ikonou (napr. `Space 🪐`) v decentnom pill boxe.
   - Čas čítania (napr. `12s read`) a odznak overeného článku.
2. **Obsahové jadro (Body - Hore)**:
   - **Hook Headline**: Úderný, čistý nadpis v angličtine.
   - **Fact Story**: 2-3 ľahko stráviteľné vety kontextu.
   - **Key Metric Pill**: Decentný box so štatistikou (napr. `Total Mass: 66 Billion Suns`).
   - **Tags**: Tématické hashtagy (`#astronomy`, `#records`).
3. **Pravý akčný panel (Floating Action Bar)**:
   - ❤️ **Like**: Srdiečko s haptickou animáciou a počítadlom.
   - 🔖 **Save**: Uloženie do osobnej knižnice.
   - 🌐 **Wiki**: Priamy in-app sumár Wikipédie a odkaz na celý článok.
   - 🔊 **Voice**: Predčítanie faktu anglickým hlasom (Web Speech API).
   - ↗️ **Share**: Zdieľanie alebo skopírovanie faktu.
4. **Vizuál (Dole - Flexibilné vyplnenie plochy)**:
   - Obrázok / ilustrácia umiestnená v spodnej časti kartičky, ktorá **automaticky a prirodzene vyplní všetku zostávajúcu plochu** (`flex-1 w-full min-h-[200px]`), takže pod textom nezostáva žiadne prázdne miesto.
   - Elegantný popisok s názvom v spodnej lište obrázku.
   - *Bez rušivého spodného loading baru.*
5. **Spodná navigácia / Ovládanie**:
   - Filtrovanie podľa kategórií (pill carousel).
   - Tlačidlo pre zoznam uložených faktov (Saved collection).
   - Tlačidlo pre generovanie / náhodný skok.

---

## 3. Dátový Model (Data Schema)

```typescript
interface FactCard {
  id: string;                    // Unikátny identifikátor (napr. "fact_space_ton618")
  category: CategoryId;          // "space" | "construction" | "biology" | "history" | "tech" | "nature"
  categoryLabel: string;         // "Vesmír", "Staviteľstvo"...
  categoryIcon: string;          // Emoji alebo Lucide icon názov
  categoryColor: string;         // Hex alebo Tailwind farba (napr. "#8B5CF6")
  readTimeSeconds: number;       // napr. 12 (max 15s)
  title: string;                 // Chytľavý nadpis
  snippet: string;               // 2-3 vety vysvetlenia
  keyStat?: {
    label: string;               // "Hmotnosť", "Výška", "Dátum"...
    value: string;               // "66 miliárd Sĺnc"
  };
  image: {
    url: string;                 // URL ilustrácie / obrázku
    alt: string;                 // Popis
    style: 'illustration' | 'photo' | 'graphic';
    sourceAttribution?: string;  // Pôvod obrázku (Wikimedia / Unsplash)
  };
  source: {
    title: string;               // Názov článku na Wikipédii
    url: string;                 // Link na článok (napr. https://sk.wikipedia.org/wiki/TON_618)
    extract?: string;            // Krátky encyklopedický sumár pre modal náhľad
  };
  tags: string[];                // ["čierne diery", "astrofyzika", "rekordy"]
  likesCount: number;
}
```

---

## 4. Architektúra & Scraper Pipeline

### 4.1 Frontend Stack
- **Framework**: React 19 + TypeScript + Vite (rýchly štart, bleskový hot-reload).
- **Styling**: Tailwind CSS + Custom glassmorphism, gradienty, fluid animations.
- **Gestá a Swiping**: Framer Motion / Touch drag hooks s podporou vertikálneho snap scrollu, swipe gest na mobile a klávesnice (šípky hore/dole) na desktope.
- **Ikony**: Lucide React.
- **Audio / Sfx**: Web Audio API / Subtle sound effects pre like a swipe (vypínateľné).
- **Persistence**: LocalStorage (pre Likes, Uložené fakty, Prečítané fakty, Dark/Light preference).

### 4.2 Scraper & Content Engine
- **Zdrojové API**:
  1. **Wikipedia REST API** (`/api/rest_v1/page/summary/{title}`): Získanie oficiálneho abstraktu, titulného obrázku a odkazu.
  2. **Wikipédia "Vedeli ste, že..." (Did you know)** a tematické portály (Vesmír, Stavebníctvo, Technika, Príroda).
  3. **Wikimedia Commons API**: Získanie verejných doménových ilustrácií a grafík.
- **Spracovanie (Parser/Summarizer)**:
  - Formátovanie textu do údernej 15-sekundovej štruktúry: Hook nadpis + 2 vety kontextu + kľúčová metrika.
  - Kategorizácia a priradenie vizuálov/ilustrácií.
- **Dátové úložisko**:
  - `database/scrollwise.db` – Relačná SQLite databáza uchovávajúca 1 000 overených faktov s fotografiami (veľkosť: **0.71 MB**, priemer cca 750 bajtov na fakt).
  - `src/data/scraped_facts.json` – JSON export pre bleskové načítanie do React klientskeho feedu (veľkosť: **1.35 MB**).
  - `scraper/mass_wiki_scraper.py` – Viacvláknový streamovací scraper na zber 1 000+ faktov s prísnou kontrolou existencie fotografií a ochranou proti rate-limitu (`npm run scrape:1000`).
  - **Škálovateľnosť**:
    - 10 000 faktov  -> cca 7.1 MB (SQLite)
    - 50 000 faktov  -> cca 35.7 MB (SQLite)
    - 100 000 faktov -> cca 71.5 MB (SQLite)
