# 🌟 ScrollWise – 15s Micro-Learning Reels

> **ScrollWise** je moderná aplikácia na štýl Instagram Reels / TikTok, zameraná na rýchle (max 15-sekundové) vzdelávanie prostredníctvom pútavých kartičiek s faktami zo všetkých encyklopedických oblastí – od stavebných divov sveta až po hlbiny vesmíru a kvantovú fyziku – s priamym preklikom na Wikipédiu.

---

## 🚀 Rýchle spustenie aplikácie

V koreňovom priečinku projektu spustite vývojový server:

```bash
npm run dev
```

Aplikácia sa okamžite spustí na lokálnej adrese (napr. `http://localhost:5173/`). Otvorte ju v prehliadači na počítači alebo v mobilnom emulátore (alebo priamo cez mobil v lokálnej sieti).

Pre vytvorenie optimalizovaného produkčného balíčka:
```bash
npm run build
```

---

## 🕷️ Spustenie Wikipedia Scrapera

ScrollWise má pokročilý streamovací scraper, ktorý cez oficiálne **Wikipedia REST API** vyhľadáva, kontroluje prítomnosť fotografií a ukladá fakty do SQLite databázy a JSON feedu:

```bash
# 1. Interaktívny výber témy z konzolového menu:
npm run scrape:category

# 2. Rýchly zber konkrétnej kategórie (napr. matematika, film, filozofia, jedlo):
python scraper/clean_mass_scraper.py --category math --count 50
python scraper/clean_mass_scraper.py --category cinema --count 50
python scraper/clean_mass_scraper.py --category philosophy --count 50

# 3. Masívny zber 1 000+ faktov naprieč všetkými 18 kategóriami:
npm run scrape:1000

# 4. Rýchly re-export SQLite databázy do JSON pre frontend:
npm run scrape:export
```

Tento skript stiahne encyklopedické dáta, overí fotografiu a uloží ich do `database/scrollwise.db` a `src/data/scraped_facts.json`, odkiaľ ich aplikácia okamžite premieta do feedu.

---

## 📱 Kľúčové Funkcie & Dizajn

1. **Reels Snap-Scroll Feed**:
   - Plynulé vertikálne posúvanie (swipe hore/dole na mobile, šípky alebo medzerník na klávesnici, scrollovanie kolieskom myši na PC).
   - Každá obrazovka je samostatná vizuálna kartička s matným grafitovým dizajnom (`#14151a`), textom hore a fotografiou dynamicky vyplňujúcou spodnú plochu.
   - Nerušené, čisté rozhranie bez AI purpurových neónov a bez rušivých loading barov.

2. **Pravý Akčný Panel (Action Bar)**:
   - ❤️ **Like**: Srdiečko s animáciou a počítadlom + možnosť **dvojkliku (double-tap)** na kartičku so srdiečkovým efektom ako na Instagrame.
   - 🔖 **Uložiť (Bookmark)**: Uloženie faktu do vlastnej offline knižnice na neskôr.
   - 🌐 **Wikipédia Zdroj (W)**: Otvorí in-app náhľad s oficiálnym sumárom a priamym odkazom na celý článok na Wikipédii.
   - 🔊 **Predčítanie hlasom (TTS)**: Prečítanie faktu pomocou hlasovej syntézy prehliadača.
   - ↗️ **Zdieľanie**: Natívne zdieľanie alebo skopírovanie faktu do schránky.

3. **18 Tematických Kategórií & Topic Explorer**:
   - 🪐 **Space**: Supermasívne čierne diery, hmloviny, mesiace a vesmírne sondy
   - 🧪 **Science & Physics**: Časticová fyzika, optika, chemické prvky a termodynamika
   - 📐 **Mathematics**: Matematické paradoxy, fraktály, konštanty a čísla
   - 🏛️ **Philosophy**: Myšlienkové experimenty, stoicizmus, etika a antickí filozofi
   - 🏗️ **Engineering**: Visuté mosty, mrakodrapy, gotické katedrály a megastavby
   - 🌿 **Nature**: Dinosauri, mäsožravce, dravé vtáky a prírodné divy
   - 🌊 **Deep Ocean**: Abyssalné priekopy, hlbokomorské ryby, hlavonožce a koralové útesy
   - 🧬 **Biology & Brain**: Ľudský mozog, neuroanatómia, DNA a genetika
   - 📜 **History**: Sedem divov sveta, staroveký Egypt, Rím a archeologické vykopávky
   - 🗺️ **Geography**: Extrémne body Zeme, kaňony, ľadovce, púšte a sopky
   - ⚡ **Technology**: Superpočítače, urýchľovače častíc, mikroprocesory a robotika
   - 🎨 **Art & Design**: Renesančné maľby, Louvre, antické sochy a impresionizmus
   - 🎬 **Cinema & Film**: Kinematografia, praktické filmové efekty a ikonické techniky
   - 🎵 **Music & Sound**: Hudobné nástroje, analógové syntetizátory, akustika a skladatelia
   - 📚 **Books & Literature**: Staroveké rukopisy, epické básne a svetová klasika
   - 🍳 **Food & Cooking**: Kulinárska veda, fermentované jedlá, exotické koreniny a syry
   - 🏃 **Fitness & Sport**: Biomechanika, svalová fyziológia, vytrvalosť a silový tréning
   - 🏆 **World Records**: Planétne superlatívy, najvyššie stavby a extrémne rekordy

4. **Návykové a herné prvky (Micro-interactions)**:
   - 🔥 **Denný streak & počítadlo**: Počítadlo objavených faktov v reálnom čase.
   - 🔊 **Web Audio syntetizátor**: Príjemné kliknutia a cinknutia pri lajku a swipovaní (možno kedykoľvek stlmiť v hornom paneli).
   - 📚 **Knižnica uložených faktov**: Rýchly prístup k uloženým faktom cez hornú záložku.

---

## 🗂️ Štruktúra Projektu

```
scrollovanie/
├── PROJECT_SPEC.md              # Kompletná technická a dizajn špecifikácia
├── ROADMAP.md                   # Živý tracker úloh s [x] DONE a [ ] TO DO
├── README.md                    # Tento návod na použitie
├── scraper/
│   └── fetch_wiki_facts.py      # Wikipedia REST API scraper a parser
├── src/
│   ├── types/
│   │   └── fact.ts              # Dátové typy pre FactCard a CategoryMeta
│   ├── data/
│   │   ├── categories.ts        # Metadáta kategórií, ikony a farebné témy
│   │   ├── facts.ts             # Ručne kurátorská databáza overených faktov
│   │   ├── factsRepository.ts   # Zjednocujúci repozitár spájajúci dáta s fallbackmi
│   │   └── scraped_facts.json   # Výstup zo scrapera
│   ├── components/
│   │   ├── ReelFeed.tsx         # Vertikálny snap-scroll engine
│   │   ├── FactCardItem.tsx     # Komponent jednotlivej Reels kartičky
│   │   ├── ActionBar.tsx        # Pravý akčný panel (Like, Save, Wiki, Audio, Share)
│   │   ├── CategoryBar.tsx      # Horizontálny prepínač tém
│   │   ├── TopBar.tsx           # Horná lišta so streakom, zvukom a knižnicou
│   │   ├── WikipediaModal.tsx   # In-app náhľad článku Wikipédie
│   │   └── SavedDrawer.tsx      # Zoznam uložených faktov používateľa
│   ├── utils/
│   │   ├── storage.ts           # Správa lokálnej pamäte (Likes, Saves, Streak)
│   │   ├── sound.ts             # Web Audio syntetizátor UI zvukov
│   │   └── speech.ts            # Web Speech API predčítanie
│   ├── App.tsx                  # Hlavná aplikácia
│   ├── index.css                # Tailwind CSS v4 a glassmorphism štýly
│   └── main.tsx                 # Vstupný bod
```
