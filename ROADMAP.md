# 🗺️ ScrollWise - Projektová Roadmapa & Sledovanie Úloh

Tento súbor slúži ako živý prehľad úloh a stavu vývoja projektu **ScrollWise**.  
Pri každom dokončenom kroku sa stav aktualizuje z `[ ] TO DO` na `[x] DONE`.

---

## 📌 Aktuálny Stav Projektu

| Fáza | Názov Fázy | Stav |
| :--- | :--- | :--- |
| **Fáza 1** | Inicializácia projektu, stack & dizajn systém | ✅ DOKONČENÉ |
| **Fáza 2** | Reels Feed & Snap-Scroll Engine | ✅ DOKONČENÉ |
| **Fáza 3** | Interaktívne Kartičky & Pravý Akčný Bar | ✅ DOKONČENÉ |
| **Fáza 4** | Wikipedia Scraper & Bohatá Databáza Faktov | ✅ DOKONČENÉ |
| **Fáza 5** | Kategórie, Filtrovanie & Knižnica Uložených Faktov | ✅ DOKONČENÉ |
| **Fáza 6** | Micro-interactions, Streak & Návykový Polish | ✅ DOKONČENÉ |
| **Fáza 7** | Dokumentácia, Skripty & Pripravenosť | ✅ DOKONČENÉ |

---

## 📋 Detailný Zoznam Úloh

### 🏗️ Fáza 1: Inicializácia projektu, stack & dizajn systém
- [x] Vytvorenie špecifikácie projektu `PROJECT_SPEC.md`
- [x] Vytvorenie roadmapy a trackera `ROADMAP.md`
- [x] Inicializácia React 19 + TypeScript + Vite prostredia
- [x] Inštalácia kľúčových závislostí:
  - `tailwindcss` v4 + `@tailwindcss/vite`
  - `lucide-react` (pre moderné ikony a fav icons)
  - `framer-motion` (pre plynulé gestá, swiping a card prechody)
  - `canvas-confetti` (pre oslavné animácie pri lajkoch/streaku)
- [x] Nastavenie čistého minimalistického dizajnu (decentný matný grafitový podklad, prirodzená typografia, odstránený krikľavý AI fialový neón)
- [x] Kompletná lokalizácia celej aplikácie, faktov, scrapera a UI do angličtiny (English)

### 📱 Fáza 2: Reels Feed & Snap-Scroll Engine
- [x] Vytvorenie hlavného kontajnera s vertikálnym snap-scrollom (`snap-y snap-mandatory` v `ReelFeed.tsx`)
- [x] Podpora dotykových gest (swipe hore/dole) a klávesnice (šípky hore/dole, medzerník, PageDown/Up)
- [x] Detekcia aktívnej kartičky a virtuálny index (zobrazenie len viditeľnej kartičky a blízkych susedov pre maximálny výkon)
- [x] Responzívny viewport: mobilný Reels formát centrovaný na desktope s desktop šípkami a indikátorom `X / Y`

### 🎨 Fáza 3: Interaktívne Kartičky & Pravý Akčný Bar
- [x] Komponent `FactCardItem`:
  - **Text umiestnený hore** (veľký hook nadpis, 2-3 vetový fakt, kľúčová metrika `keyStat`, tagy)
  - **Obrázok dole flexibilne vypĺňajúci celú zostávajúcu plochu** (`flex-1 w-full min-h-[200px]`), aby pod textom nezostávalo žiadne prázdne miesto
  - Odstránená rušivá spodná načítavacia lišta pre čistý a nerušený zážitok
  - Kategória s neutrálnou fav ikonou (`Space 🪐`, `Engineering 🏗️`, `Biology 🧬` atď.)
  - Čas čítania (`12s read`) a odznak overenia Wikipédie
- [x] Komponent `ActionBar` (vertikálny panel napravo v štýle Instagram Reels / TikTok):
  - ❤️ **Like tlačidlo**: animácia srdiečka + dynamické počítadlo + perzistencia
  - 🔖 **Bookmark / Uloženie**: ukladanie do lokálnej knižnice
  - 🌐 **Wikipedia preklik**: priame tlačidlo otvárajúce in-app zdrojový modal
  - 🔊 **Predčítanie (TTS)**: hlasové prečítanie faktu cez Web Speech API
  - ↗️ **Zdieľanie**: natívne Web Share API + clipboard fallback s toastom

### 🕷️ Fáza 4: Wikipedia Scraper & Bohatá Databáza Faktov
- [x] Návrh dátovej schémy v `src/types/fact.ts`
- [x] Vytvorenie základného skriptu `scraper/fetch_wiki_facts.py` (`npm run scrape`)
- [x] **Masívny Wikipedia Scraper pre 1 000 faktov** (`scraper/mass_wiki_scraper.py` / `npm run scrape:1000`):
  - Viacvláknový streamovací zber s ochranou proti rate-limitu
  - Prísne pravidlo: uložené **iba články s overenou fotkou z Wikipédie**
  - **Vysoko-precízne tematické filtrovanie**: Veda obsahuje výlučne reálnu fyziku, chemické prvky a materiálové javy (odstránené akékoľvek nevedecké články, šport a pop-kultúra)
  - Vytvorenie relačnej SQLite databázy `database/scrollwise.db` (veľkosť: **0.70 MB**)
  - Export 1 000 čistých faktov priamo do React aplikácie `src/data/scraped_facts.json` (veľkosť: **1.34 MB**)
  - Analýza škálovateľnosti: priemer cca 750 bajtov na fakt (~7 MB pre 10 000 faktov; ~71 MB pre 100 000 faktov)
- [x] Zjednotený repozitár `src/data/factsRepository.ts` načítavajúci celú databázu 1 000 faktov pre Reels feed

### 🗂️ Fáza 5: Kategórie, Filtrovanie & Knižnica Uložených Faktov
- [x] Rozšírenie na 18 plnohodnotných kategórií poznania (Matematika, Filozofia, Umenie, Filmy a Seriály, Hudba, Knihy a Literatúra, Varenie a Gastronómia, Cvičenie a Šport, Svetové Rekordy, Geografia, Vesmír, Veda, Staviteľstvo, Príroda, Oceány, Biológia, História, Technológie)
- [x] Horizontálny pill carousel `CategoryBar.tsx` s automatickým plynulým scrollom aktívneho pilulkového tlačidla do stredu
- [x] **CategoryModal (`CategoryModal.tsx`)**: interaktívny prehliadač všetkých 18 tém s vyhľadávaním, popismi, počítadlami faktov a rýchlym výberom
- [x] **Interaktívny a modulárny scraper (`scraper/clean_mass_scraper.py`)**:
  - Výber kategórie cez CLI prepínače: `--category <id>`, `--count <n>`, `--reset`, `--interactive`
  - Vlastné mapovanie oficiálnych Wikipedia kategórií pre každú z 18 tém
  - Kontextovo citlivý blacklist odstraňujúci bulvár a nezmysly pri zachovaní filmov a umenia v príslušných témach
- [x] Bočný panel `SavedDrawer.tsx` pre **Uložené fakty (Saved / Bookmarks)** s možnosťou prekliknutia a mazania
- [x] In-App Wikipedia Reader Modal `WikipediaModal.tsx` (rýchly kontext a preklik na plný článok bez opustenia feedu)

### ✨ Fáza 6: Micro-interactions, Streak & Návykový Polish
- [x] Denný streak a počítadlo prečítaných faktov (napr. *"🔥 12 faktov dnes"*)
- [x] Jemné syntetizované zvukové efekty cez Web Audio API pre like, save a swipe (`src/utils/sound.ts`)
- [x] Dvojklik (double-tap) na kartičku spúšťajúci burst srdiečka ako na Instagrame
- [x] Čistý, nerušený zážitok z čítania (odstránená rušivá spodná načítavacia lišta podľa spätnej väzby)

### 🚀 Fáza 7: Dokumentácia, Skripty & Pripravenosť
- [x] Aktualizácia `package.json` o skript `"scrape": "python scraper/fetch_wiki_facts.py"`
- [x] Úspešný TypeScript a produkčný Vite build (`npm run build` bez akýchkoľvek chýb)
- [x] Vytvorenie detailného `README.md` s inštrukciami na spustenie a obsluhu
