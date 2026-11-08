"""
Re-classifies every fact already stored in database/scrollwise.db using the
content-based classifier (scraper/classifier.py).

    python scraper/reclassify_db.py            # dry run, prints a report
    python scraper/reclassify_db.py --apply    # writes changes + re-exports JSON

For facts currently in "records" whose stored snippet has no record claim, the
full Wikipedia summary is re-fetched: if the record sentence exists there, the
snippet is rewritten around it; otherwise the fact is moved to its best
matching category (or removed if no category fits).
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classifier import classify, find_record_sentence, build_record_snippet, build_record_hook  # noqa: E402
from clean_mass_scraper import CATEGORY_CONFIG, export_and_report  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE, "database", "scrollwise.db")
JSON_PATH = os.path.join(BASE, "src", "data", "scraped_facts.json")
JSON_BACKUP = os.path.join(BASE, "database", "facts_1000.json")
USER_AGENT = "ScrollWiseBot/2.3 (contact: jurko@scrollwise.app) Python/urllib"


def fetch_extract(wiki_url: str) -> str:
    title = urllib.parse.unquote(wiki_url.rsplit("/wiki/", 1)[-1])
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title)
    try:
        time.sleep(0.05)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data.get("extract", ""), data.get("description", "")
    except Exception:
        return "", ""


def split_title(stored_title: str):
    name, _, desc = stored_title.partition(": ")
    return name.strip(), desc.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, topic, title, text, wiki_url FROM facts")
    rows = cur.fetchall()

    moves = Counter()
    examples = defaultdict(list)
    updates = []   # (new_topic, new_text, id)
    deletes = []

    for fid, topic, stored_title, text, wiki_url in rows:
        name, desc = split_title(stored_title)
        new_text = text
        result = classify(name, desc, text, source_cat=topic)

        # Current record whose snippet lacks the claim -> look at the full summary
        if topic == "records" and result["category"] != "records":
            full, wdesc = fetch_extract(wiki_url)
            if full and find_record_sentence(full):
                new_text = build_record_snippet(name, full)
                result = {"category": "records", "reason": "record found in full summary"}
            elif full:
                result = classify(name, desc or wdesc, full, source_cat=None)

        new_cat = result["category"]
        if new_cat is None:
            deletes.append(fid)
            moves[(topic, "DELETED")] += 1
            if len(examples[(topic, "DELETED")]) < 4:
                examples[(topic, "DELETED")].append(stored_title)
        else:
            new_title = stored_title
            if new_cat == "records":
                rec_found = find_record_sentence(new_text)
                if rec_found:
                    new_title = build_record_hook(name, rec_found[1])
            elif topic == "records" and new_cat != "records":
                new_title = f"{name}: {desc.capitalize()}" if desc else name

            if new_cat != topic or new_text != text or new_title != stored_title:
                updates.append((new_cat, new_title, new_text, fid))
                if new_cat != topic:
                    moves[(topic, new_cat)] += 1
                    if len(examples[(topic, new_cat)]) < 4:
                        examples[(topic, new_cat)].append(stored_title)

    print(f"Total facts checked: {len(rows)}")
    print(f"Facts to move: {sum(v for k, v in moves.items() if k[1] != 'DELETED')}")
    print(f"Facts to delete (no confident category): {len(deletes)}\n")
    for (src, dst), n in moves.most_common():
        print(f"  {src:>12} -> {dst:<12} {n:4}   e.g. {' | '.join(examples[(src, dst)][:3])}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to write changes.")
        return

    for new_cat, new_title, new_text, fid in updates:
        cfg = CATEGORY_CONFIG[new_cat]
        new_id = re.sub(r"^fact_[a-z]+_", f"fact_{new_cat}_", fid)
        cur.execute("SELECT 1 FROM facts WHERE id = ? AND id != ?", (new_id, fid))
        if cur.fetchone():
            new_id = fid
        cur.execute(
            "UPDATE facts SET id=?, topic=?, topic_label=?, topic_icon=?, accent_color=?, title=?, text=? WHERE id=?",
            (new_id, new_cat, cfg["label"], cfg["icon"], cfg["accent"], new_title, new_text, fid),
        )
    for fid in deletes:
        cur.execute("DELETE FROM facts WHERE id = ?", (fid,))
    conn.commit()
    export_and_report(conn, DB_PATH, JSON_PATH, JSON_BACKUP)


if __name__ == "__main__":
    main()
