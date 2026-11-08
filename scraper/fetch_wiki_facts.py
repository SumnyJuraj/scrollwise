"""
ScrollWise - Wikipedia & Encyclopedia Fact Scraper / Enricher
Downloads encyclopedic summaries directly from the official Wikipedia REST API,
formats them into crisp 15-second cards, and stores them in structured JSON.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

USER_AGENT = "ScrollWiseFactApp/1.0 (contact: jurko@personal.app) Python/urllib"

CATEGORIES_MAP = {
    "space": {
        "label": "Space",
        "icon": "🪐",
        "accentColor": "#818cf8",
        "articles": [
            ("TON 618", "The largest black hole weighs as much as 66 billion Suns", "Total Mass", "66 Billion Suns"),
            ("Olympus Mons", "The tallest volcano in the Solar System towers on Mars", "Summit Height", "21.9 km"),
            ("Neutron star", "A teaspoon of neutron star weighs a billion tons", "Core Density", "10¹⁷ kg/m³"),
            ("James Webb Space Telescope", "The telescope observing the earliest newborn galaxies", "Orbital Distance", "1.5 million km from Earth"),
            ("Voyager 1", "The farthest human-made object traveling in interstellar space", "Distance from Earth", "24+ billion km"),
        ]
    },
    "construction": {
        "label": "Engineering",
        "icon": "🏗️",
        "accentColor": "#fbbf24",
        "articles": [
            ("Burj Khalifa", "The tallest skyscraper on Earth with its own microclimate", "Total Height", "828 meters"),
            ("Gotthard Base Tunnel", "The longest and deepest transit railway tunnel in the world", "Route Length", "57.1 km under the Alps"),
            ("Millau Viaduct", "The highest cable-stayed bridge, structurally taller than the Eiffel Tower", "Mast Height", "343 meters"),
            ("Panama Canal", "The engineering marvel linking the Atlantic and Pacific oceans", "Detour Saved", "13,000 km"),
            ("Great Wall of China", "The most extensive defensive architectural project in history", "Total Length", "21,196 km"),
            ("Hoover Dam", "The massive concrete dam that required decades of internal cooling", "Concrete Volume", "2.48 million m³"),
        ]
    },
    "nature": {
        "label": "Nature",
        "icon": "🌿",
        "accentColor": "#34d399",
        "articles": [
            ("Tardigrade", "The near-indestructible micro-animal able to survive outer space", "Thermal Survival", "-272°C to +150°C"),
            ("Pando (tree)", "The heaviest known living organism: an entire clonal forest from one root", "Organism Mass", "6,000 tons"),
            ("Turritopsis dohrnii", "The biologically immortal jellyfish capable of reverting to youth", "Superpower", "Biological immortality"),
            ("Blue whale", "The largest creature ever known, with an automobile-sized heart", "Heart Weight", "approx. 180 kg"),
        ]
    },
    "tech": {
        "label": "Technology",
        "icon": "⚡",
        "accentColor": "#38bdf8",
        "articles": [
            ("Apollo Guidance Computer", "The pioneering computer that guided astronauts to the Moon", "Working RAM", "Only 4 kilobytes"),
            ("Submarine communications cable", "Over 99% of global internet traffic flows through ocean seabed cables", "Subsea Network", "1.4 million km"),
            ("Quantum computing", "Next-gen processors computing across quantum superposition states", "Basic Unit", "Qubits instead of bits"),
        ]
    },
    "history": {
        "label": "History",
        "icon": "🏛️",
        "accentColor": "#f59e0b",
        "articles": [
            ("Antikythera mechanism", "The oldest known analog computer built in ancient Greece", "Artifact Age", "Over 2,100 years"),
            ("Library of Alexandria", "The legendary classical sanctuary of ancient world knowledge", "Scrolls Held", "Up to 400,000"),
            ("Rosetta Stone", "The archaeological key that unlocked Egyptian hieroglyphics", "Discovery Year", "1799 AD"),
        ]
    },
    "biology": {
        "label": "Biology & Brain",
        "icon": "🧬",
        "accentColor": "#f472b6",
        "articles": [
            ("DNA", "Unraveled DNA from one human body would stretch to Pluto and back", "Total Strand Length", "Over 20 billion km"),
            ("Human brain", "Your brain generates enough electricity to power a low-watt LED bulb", "Power Consumption", "approx. 20 Watts"),
            ("Axolotl", "The amphibian that completely regenerates lost limbs, heart, and brain tissue", "Regeneration", "100% scar-free regrowth"),
        ]
    },
    "ocean": {
        "label": "Deep Ocean",
        "icon": "🌊",
        "accentColor": "#60a5fa",
        "articles": [
            ("Mariana Trench", "The deepest oceanic trench on Earth where water pressure crushes steel", "Maximum Depth", "10,994 meters"),
            ("Bioluminescence", "Living organisms illuminating the pitch-black ocean depths with chemical light", "Prevalence", "76% of deep-sea species"),
        ]
    }
}


def fetch_wiki_summary(title: str):
    """Fetches official abstract and thumbnail from the Wikipedia REST API."""
    encoded_title = urllib.parse.quote(title.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return data
    except Exception as e:
        print(f"Error fetching '{title}': {e}")
    return None


def clean_snippet(extract: str, max_chars: int = 240) -> str:
    """Formats extract into a punchy 15-second read (approx 2 sentences)."""
    sentences = re.split(r"(?<=[.!?])\s+", extract)
    result = ""
    for s in sentences:
        if len(result) + len(s) < max_chars:
            result += (" " if result else "") + s
        else:
            break
    if not result and sentences:
        result = sentences[0][:max_chars] + "..."
    return result


def main():
    print("🚀 Running ScrollWise Wikipedia Fact Scraper (English)...")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "src", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "scraped_facts.json")

    facts = []

    for cat_id, cat_info in CATEGORIES_MAP.items():
        print(f"\n📂 Processing category: {cat_info['label']} ({cat_id})")
        for item in cat_info["articles"]:
            wiki_title = item[0]
            hook = item[1]
            stat_label = item[2]
            stat_value = item[3]

            data = fetch_wiki_summary(wiki_title)
            if not data:
                continue

            extract = data.get("extract", "")
            snippet = clean_snippet(extract)
            wiki_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{wiki_title}")
            image_url = ""
            if "thumbnail" in data and "source" in data["thumbnail"]:
                image_url = data["thumbnail"]["source"]

            card_id = f"fact_{cat_id}_{re.sub(r'[^a-zA-Z0-9]', '_', wiki_title.lower())}"

            fact_card = {
                "id": card_id,
                "category": cat_id,
                "categoryLabel": cat_info["label"],
                "categoryIcon": cat_info["icon"],
                "accentColor": cat_info["accentColor"],
                "readTimeSeconds": 12,
                "hookTitle": hook,
                "snippet": snippet,
                "keyStat": {
                    "label": stat_label,
                    "value": stat_value
                },
                "image": {
                    "url": image_url,
                    "alt": wiki_title,
                    "style": "illustration",
                    "credit": "Wikimedia Commons / Wikipedia"
                },
                "source": {
                    "title": data.get("title", wiki_title),
                    "url": wiki_url,
                    "extract": extract[:350] + "..." if len(extract) > 350 else extract
                },
                "tags": [cat_info["label"].lower(), wiki_title.lower()],
                "likesCount": 142 + (hash(wiki_title) % 500),
                "verified": True
            }

            facts.append(fact_card)
            print(f"  ✓ {wiki_title} -> {fact_card['hookTitle']}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Successfully compiled {len(facts)} English facts into: {output_file}")


if __name__ == "__main__":
    main()
