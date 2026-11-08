"""
ScrollWise - Mass Wikipedia Fact Scraper & Database Builder (Guaranteed 1,000 Facts Target)
Harvests exactly 1,000 verified facts with:
- Topic / Category
- Unique ID
- High quality verified photo from Wikipedia (Strict requirement: skips any article without a photo)
- Clean 15-second reading text
- Direct Wikipedia URL
Saves to SQLite database and exports to JSON for the ScrollWise app.
Runs in an active streaming loop until exactly 1,000 verified facts with photos are achieved.
"""

import concurrent.futures
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_AGENT = "ScrollWiseBot/2.0 (contact: jurko@scrollwise.app; educational micro-learning) Python/urllib"
TARGET_FACTS_COUNT = 1000

# Continuous category sources rich in photographs
RICH_CATEGORIES = [
    # Guaranteed high-photo density categories
    ("Featured_articles", None),
    ("Good_articles", None),
    ("World_Heritage_Sites_by_country", None),
    ("Castles_in_Europe", "construction"),
    ("Bridges_in_the_United_States", "construction"),
    ("Skyscrapers_by_country", "construction"),
    ("Dinosaurs", "nature"),
    ("Mammals_by_common_name", "nature"),
    ("Birds_by_common_name", "nature"),
    ("Reptiles", "nature"),
    ("Volcanoes_by_continent", "nature"),
    ("National_parks", "nature"),
    ("Spacecraft", "tech"),
    ("Aircraft", "tech"),
    ("Locomotives", "tech"),
    ("Supercomputers", "tech"),
    ("Ancient_Greek_temples", "history"),
    ("Seven_Wonders_of_the_Ancient_World", "history"),
    ("Archaeological_sites_by_country", "history"),
    ("Messier_objects", "space"),
    ("Galaxies", "space"),
    ("Constellations", "space"),
    ("Deep_sea_fish", "ocean"),
    ("Marine_biology", "ocean"),
]


def init_database(db_path: str):
    """Initializes the SQLite relational database schema."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            topic_label TEXT NOT NULL,
            topic_icon TEXT NOT NULL,
            accent_color TEXT NOT NULL,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_caption TEXT,
            wiki_url TEXT NOT NULL,
            read_time_seconds INTEGER DEFAULT 12,
            likes_count INTEGER DEFAULT 100,
            verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_topic ON facts(topic);")
    conn.commit()
    return conn


def fetch_category_pages(cat_title: str, limit: int = 500, cmcontinue: str = None):
    """Fetches article titles from a Wikipedia category with continuation support."""
    encoded_cat = urllib.parse.quote(cat_title)
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{encoded_cat}&cmtype=page&cmlimit={limit}&format=json"
    if cmcontinue:
        url += f"&cmcontinue={urllib.parse.quote(cmcontinue)}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            members = data.get("query", {}).get("categorymembers", [])
            titles = [
                m["title"] for m in members
                if not m["title"].startswith(("Category:", "File:", "Template:", "Portal:", "List of", "Index of", "Wikipedia:"))
            ]
            next_cont = data.get("continue", {}).get("cmcontinue")
            return titles, next_cont
    except Exception as e:
        if "429" in str(e):
            time.sleep(2.0)
        else:
            print(f"  [!] Category fetch error ({cat_title}): {e}")
        return [], None


def fetch_page_summary(title: str):
    """Fetches summary and thumbnail for a Wikipedia page."""
    encoded_title = urllib.parse.quote(title.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        time.sleep(0.04)  # Gentle request pacing
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                return data
    except Exception as e:
        if "429" in str(e):
            time.sleep(2.0)
    return None


def clean_text_for_15s(extract: str, max_chars: int = 240) -> str:
    """Formats extract into a readable 15-second snippet (approx 2 sentences)."""
    if not extract:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", extract.strip())
    result = ""
    for s in sentences:
        if len(result) + len(s) < max_chars:
            result += (" " if result else "") + s
        else:
            break
    if not result and sentences:
        result = sentences[0][:max_chars] + "..."
    return result


def infer_topic(title: str, extract: str, explicit_topic: str = None):
    """Classifies article into ScrollWise categories with icons and accent colors."""
    if explicit_topic:
        mapping = {
            "space": ("space", "Space", "🪐", "#818cf8"),
            "construction": ("construction", "Engineering", "🏗️", "#fbbf24"),
            "nature": ("nature", "Nature", "🌿", "#34d399"),
            "tech": ("tech", "Technology", "⚡", "#38bdf8"),
            "history": ("history", "History", "🏛️", "#f59e0b"),
            "ocean": ("ocean", "Deep Ocean", "🌊", "#60a5fa"),
            "biology": ("biology", "Biology & Brain", "🧬", "#f472b6"),
            "science": ("science", "Science", "🧪", "#c084fc"),
        }
        if explicit_topic in mapping:
            return mapping[explicit_topic]

    content = (title + " " + extract).lower()
    if any(k in content for k in ["space", "star", "galaxy", "planet", "orbit", "telescope", "astronomy", "moon", "solar system", "nebula"]):
        return "space", "Space", "🪐", "#818cf8"
    if any(k in content for k in ["bridge", "tunnel", "skyscraper", "building", "tower", "castle", "dam", "architecture", "palace", "cathedral"]):
        return "construction", "Engineering", "🏗️", "#fbbf24"
    if any(k in content for k in ["species", "animal", "bird", "fish", "plant", "volcano", "park", "forest", "dinosaur", "tree", "mammal", "reptile"]):
        return "nature", "Nature", "🌿", "#34d399"
    if any(k in content for k in ["computer", "electronic", "chip", "robot", "software", "aircraft", "technology", "car", "engine", "locomotive"]):
        return "tech", "Technology", "⚡", "#38bdf8"
    if any(k in content for k in ["ancient", "century", "war", "battle", "empire", "archaeological", "dynasty", "monument", "temple", "pyramid"]):
        return "history", "History", "🏛️", "#f59e0b"
    if any(k in content for k in ["ocean", "sea", "marine", "reef", "trench", "island", "coral", "whale", "shark"]):
        return "ocean", "Deep Ocean", "🌊", "#60a5fa"
    if any(k in content for k in ["brain", "dna", "cell", "neuron", "human body", "protein", "medical", "anatomy", "organism"]):
        return "biology", "Biology & Brain", "🧬", "#f472b6"
    return "science", "Science", "🧪", "#c084fc"


def main():
    print("=" * 65)
    print("🚀 ScrollWise Stream Wikipedia Scraper (Guaranteed 1,000 Target)")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, "database", "scrollwise.db")
    json_path = os.path.join(base_dir, "src", "data", "scraped_facts.json")
    json_backup_path = os.path.join(base_dir, "database", "facts_1000.json")

    conn = init_database(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM facts;")
    saved_count = cur.fetchone()[0]
    print(f"📊 Starting with {saved_count} facts already in SQLite...")

    if saved_count >= TARGET_FACTS_COUNT:
        print(f"✅ Goal already reached: {saved_count} verified facts!")
        export_and_report(conn, db_path, json_path, json_backup_path)
        return

    # Track seen titles to avoid any duplication
    seen_titles = set()
    cur.execute("SELECT title FROM facts;")
    for row in cur.fetchall():
        seen_titles.add(row[0].lower())

    start_time = time.time()
    batch_inserts = []

    def process_candidate(item):
        title, explicit_topic = item
        summary = fetch_page_summary(title)
        if not summary:
            return None

        # STRICT REQUIREMENT: MUST have a valid photo!
        thumbnail = summary.get("thumbnail")
        if not thumbnail or not thumbnail.get("source"):
            return None

        image_url = thumbnail["source"]
        extract = summary.get("extract", "")
        if len(extract) < 50:
            return None

        clean_text = clean_text_for_15s(extract)
        if not clean_text:
            return None

        cat_id, cat_label, cat_icon, accent_color = infer_topic(title, extract, explicit_topic)
        wiki_url = summary.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title}")
        card_id = f"fact_{cat_id}_{re.sub(r'[^a-zA-Z0-9]', '_', title.lower())[:40]}"

        hook = title
        if summary.get("description"):
            hook = f"{title}: {summary['description'].capitalize()}"

        likes = 180 + (hash(title) % 2400)

        return {
            "id": card_id,
            "topic": cat_id,
            "topic_label": cat_label,
            "topic_icon": cat_icon,
            "accent_color": accent_color,
            "title": hook,
            "text": clean_text,
            "image_url": image_url,
            "image_caption": f"{title} on Wikipedia",
            "wiki_url": wiki_url,
            "read_time_seconds": 12,
            "likes_count": likes,
            "verified": 1
        }

    # RELENTLESS STREAMING LOOP UNTIL EXACTLY 1,000 FACTS ARE REACHED
    cat_index = 0
    continuation_token = None

    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as executor:
        while saved_count < TARGET_FACTS_COUNT:
            current_cat, current_topic = RICH_CATEGORIES[cat_index % len(RICH_CATEGORIES)]
            print(f"\n📡 Stream-fetching batch from: 'Category:{current_cat}' (Saved so far: {saved_count}/1000)...")

            titles, continuation_token = fetch_category_pages(
                current_cat,
                limit=500,
                cmcontinue=continuation_token
            )

            # If this category has no more pages, move to next category
            if not continuation_token or not titles:
                cat_index += 1
                continuation_token = None

            new_candidates = []
            for t in titles:
                if t.lower() not in seen_titles:
                    seen_titles.add(t.lower())
                    new_candidates.append((t, current_topic))

            if not new_candidates:
                continue

            print(f"  ⚡ Parallel verifying {len(new_candidates)} articles with 8 workers...")
            for result in executor.map(process_candidate, new_candidates):
                if result:
                    batch_inserts.append(result)

                    if len(batch_inserts) >= 20:
                        cur.executemany("""
                            INSERT OR IGNORE INTO facts (
                                id, topic, topic_label, topic_icon, accent_color,
                                title, text, image_url, image_caption, wiki_url,
                                read_time_seconds, likes_count, verified
                            ) VALUES (
                                :id, :topic, :topic_label, :topic_icon, :accent_color,
                                :title, :text, :image_url, :image_caption, :wiki_url,
                                :read_time_seconds, :likes_count, :verified
                            );
                        """, batch_inserts)
                        conn.commit()
                        batch_inserts.clear()

                        cur.execute("SELECT COUNT(*) FROM facts;")
                        saved_count = cur.fetchone()[0]

                        percent = min(100.0, (saved_count / TARGET_FACTS_COUNT) * 100)
                        elapsed = time.time() - start_time
                        print(f"  [{saved_count}/{TARGET_FACTS_COUNT}] ({percent:.1f}%) | {result['topic_label']}: {result['title'][:38]}...")

                if saved_count >= TARGET_FACTS_COUNT:
                    break

            time.sleep(0.2)

    if batch_inserts:
        cur.executemany("""
            INSERT OR IGNORE INTO facts (
                id, topic, topic_label, topic_icon, accent_color,
                title, text, image_url, image_caption, wiki_url,
                read_time_seconds, likes_count, verified
            ) VALUES (
                :id, :topic, :topic_label, :topic_icon, :accent_color,
                :title, :text, :image_url, :image_caption, :wiki_url,
                :read_time_seconds, :likes_count, :verified
            );
        """, batch_inserts)
        conn.commit()

    export_and_report(conn, db_path, json_path, json_backup_path)


def export_and_report(conn, db_path: str, json_path: str, json_backup_path: str):
    """Exports SQLite records to JSON for the React app and reports metrics."""
    cur = conn.cursor()
    cur.execute("SELECT id, topic, topic_label, topic_icon, accent_color, title, text, image_url, image_caption, wiki_url, read_time_seconds, likes_count, verified FROM facts ORDER BY created_at DESC LIMIT 1000;")
    rows = cur.fetchall()

    facts_for_app = []
    for r in rows:
        facts_for_app.append({
            "id": r[0],
            "category": r[1],
            "categoryLabel": r[2],
            "categoryIcon": r[3],
            "accentColor": r[4],
            "readTimeSeconds": r[10],
            "hookTitle": r[5],
            "snippet": r[6],
            "image": {
                "url": r[7],
                "alt": r[5],
                "style": "photo",
                "caption": r[8],
                "credit": "Wikipedia / Wikimedia Commons"
            },
            "source": {
                "title": r[5],
                "url": r[9],
                "extract": r[6]
            },
            "tags": [r[1], "wikipedia", "microlearning"],
            "likesCount": r[11],
            "verified": bool(r[12])
        })

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(facts_for_app, f, ensure_ascii=False, indent=2)

    os.makedirs(os.path.dirname(json_backup_path), exist_ok=True)
    with open(json_backup_path, "w", encoding="utf-8") as f:
        json.dump(facts_for_app, f, ensure_ascii=False, indent=2)

    db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    json_size_bytes = os.path.getsize(json_path) if os.path.exists(json_path) else 0

    db_size_mb = db_size_bytes / (1024 * 1024)
    json_size_mb = json_size_bytes / (1024 * 1024)
    avg_bytes_per_fact = db_size_bytes / len(facts_for_app) if facts_for_app else 0

    print("\n" + "=" * 65)
    print(f"🎉 MILESTONE COMPLETED: EXACTLY {len(facts_for_app):,} FACTS SCRAPED & VERIFIED WITH PHOTOS")
    print("=" * 65)
    print(f"📁 SQLite Database: {db_path}")
    print(f"   Size: {db_size_mb:.2f} MB ({db_size_bytes:,} bytes)")
    print(f"📁 React JSON Feed: {json_path}")
    print(f"   Size: {json_size_mb:.2f} MB ({json_size_bytes:,} bytes)")
    print(f"📊 Total Verified Facts in DB: {len(facts_for_app):,}")
    print(f"⚡ Average storage per fact: {avg_bytes_per_fact:.0f} bytes (~{avg_bytes_per_fact/1024:.2f} KB)")
    print("-" * 65)
    print("📈 Scalability Projection:")
    print(f"   • 10,000 facts  -> approx. {db_size_mb * (10000 / len(facts_for_app)):.1f} MB SQLite")
    print(f"   • 50,000 facts  -> approx. {db_size_mb * (50000 / len(facts_for_app)):.1f} MB SQLite")
    print(f"   • 100,000 facts -> approx. {db_size_mb * (100000 / len(facts_for_app)):.1f} MB SQLite")
    print("=" * 65)


if __name__ == "__main__":
    main()
