"""
ScrollWise - Content-based fact classifier.

The old scraper assigned a category purely from the Wikipedia category tree an
article was crawled from. Those trees drift badly (Extreme_points_of_Earth ->
Extreme points of Moldova -> some village), so the category was often wrong.

This module decides the category from the CONTENT of the fact instead:

1. World Records - strict pattern detector. A fact is a world record only if
   one sentence makes an explicit GLOBAL superlative claim:
     "world's tallest", "largest ... in the world", "deepest ... on Earth",
     "fastest ... ever recorded", "Guinness World Record", "holds the record".
   Weakened claims are rejected: "one of the largest", "second-deepest",
   "largest in the country / in Europe".
   A detected record always wins over every other category.

2. All other categories - weighted scoring:
     * Wikipedia short description ("Species of fish", "1975 single by Queen",
       "Painting by Claude Monet") -> strongest signal (+6)
     * the "X is a ..." type phrase of the first sentence -> (+4)
     * topic keywords in title (+2 each) and text (+1 each), capped
     * negative keywords (-3 each)
     * the crawl source category only gives a small tie-break prior (+2)
   The best scoring category wins; if nothing scores high enough the fact is
   rejected instead of being dumped into a wrong category.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# 1. WORLD RECORD DETECTION
# ---------------------------------------------------------------------------

SUPERLATIVES = (
    r"largest|biggest|smallest|tallest|shortest|longest|highest|lowest|deepest|"
    r"shallowest|fastest|slowest|heaviest|lightest|oldest|youngest|hottest|"
    r"coldest|wettest|driest|brightest|darkest|densest|strongest|loudest|rarest|"
    r"widest|richest|deadliest|costliest|busiest|largest-ever|longest-lived|"
    r"longest-living|best-selling|highest-grossing|most\s+\w+|least\s+\w+"
)

GLOBAL_SCOPE = (
    r"in\s+the\s+world|on\s+earth|on\s+the\s+planet|ever\s+recorded|ever\s+built|"
    r"ever\s+measured|ever\s+found|ever\s+discovered|in\s+recorded\s+history|"
    r"in\s+history|of\s+all\s+time|known\s+to\s+science|in\s+the\s+solar\s+system|"
    r"in\s+the\s+(?:known|observable)\s+universe|in\s+the\s+universe|"
    r"to\s+have\s+ever\s+(?:lived|existed)|that\s+has\s+ever\s+(?:lived|existed)"
)

RECORD_PATTERNS = [
    # "world's tallest", "the world's most visited", "world's first"
    re.compile(rf"\bworld'?s\s+(?:{SUPERLATIVES}|first|only)\b", re.I),
    # "largest ... in the world", "deepest point on Earth", "fastest ever recorded"
    re.compile(rf"\b(?:{SUPERLATIVES})\b[^.;]{{0,70}}?\b(?:{GLOBAL_SCOPE})\b", re.I),
    # "the largest known star", "the fastest-spinning pulsar known"
    re.compile(rf"\b(?:{SUPERLATIVES})(?:-[a-z]+)?(?:\s+[\w-]+){{0,2}}\s+known\b", re.I),
    # world firsts: "the first person to walk on the Moon"
    re.compile(r"\bthe\s+first\s+(?:person|human|man|woman|people|humans|human-made\s+object|"
               r"spacecraft|artificial\s+satellite|crewed\s+\w+)\s+(?:ever\s+)?to\b", re.I),
    re.compile(r"\bguinness\s+(?:world\s+)?records?\b", re.I),
    re.compile(r"\bworld\s+records?\b", re.I),
    re.compile(r"\b(?:holds?|held|set|sets|broke|breaks|established)\s+(?:the|a|an)\s+"
               r"(?:new\s+|current\s+|all-time\s+|world\s+|absolute\s+)*record\b", re.I),
]

# A claim is NOT a record if it is weakened, historical-only, or regional
RECORD_WEAKENERS = [
    # "one of the largest", "among the tallest"
    re.compile(rf"\b(?:one\s+of\s+the|among\s+the|some\s+of\s+the)\s+(?:world'?s\s+)?"
               rf"(?:\w+\s+){{0,2}}(?:{SUPERLATIVES})\b", re.I),
    # "second-largest", "third deepest", "2nd highest"
    re.compile(rf"\b(?:second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
               rf"\d+(?:st|nd|rd|th))[\s-]+(?:{SUPERLATIVES})\b", re.I),
    # "formerly the tallest", "was once the largest", "until 2010 the tallest", "when completed... was the largest"
    re.compile(rf"\b(?:formerly|once|previously|until\s+\d{{4}}|when\s+completed)\s+(?:the\s+)?"
               rf"(?:world'?s\s+)?(?:{SUPERLATIVES})\b", re.I),
    # "was the largest", "were the largest", "had been the largest"
    re.compile(rf"\b(?:was|were|had\s+been)\s+(?:the\s+)?(?:world'?s\s+)?(?:\w+\s+){{0,2}}(?:{SUPERLATIVES})\b", re.I),
    # Regional-only superlatives (not world records): "tallest in Europe", "largest in the United States"
    re.compile(rf"\b(?:{SUPERLATIVES})\b[^.;]{{0,60}}?\b(?:in\s+(?:Europe|Asia|Africa|North\s+America|South\s+America|"
               rf"the\s+United\s+States|the\s+US|the\s+UK|Britain|England|Scotland|France|Germany|Japan|China|"
               rf"Russia|Australia|Canada|India|Italy|Spain|Poland|Greece|Scandinavia))\b", re.I),
    re.compile(r"\b(?:not|never)\s+(?:the\s+)?(?:world'?s\s+)?(?:" + SUPERLATIVES + r")\b", re.I),
]

# The record is about a person's private life, a vinyl "record", a record label...
RECORD_FALSE_FRIENDS = re.compile(
    r"\brecord\s+(?:label|company|producer|store|shop|deal|player|chart|sales)\b|"
    r"\brecords\s+(?:label|inc|ltd)\b|\bon\s+record\b|\bcriminal\s+record\b|"
    r"\b(?:epic|columbia|atlantic|capitol|island|virgin|def\s+jam|warner|sony|emi|"
    r"parlophone|motown|decca|polydor|geffen|interscope|elektra|rca)\s+records\b",
    re.I,
)


def split_sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", (text or "").strip()) if len(s.strip()) > 15]


def is_record_sentence(sentence: str) -> bool:
    """True only if the sentence makes an explicit, unweakened, global record claim."""
    cleaned = RECORD_FALSE_FRIENDS.sub(" ", sentence)
    if not any(p.search(cleaned) for p in RECORD_PATTERNS):
        return False
    if any(w.search(cleaned) for w in RECORD_WEAKENERS):
        # A weakened claim is only acceptable if another, unweakened
        # "world's X" / "Guinness" claim exists in the same sentence.
        strong_only = re.search(r"\bguinness\b|\bworld\s+record\b|\bholds?\s+the\s+(?:world\s+)?record\b",
                                cleaned, re.I)
        if not strong_only:
            return False
    return True


def find_record_sentence(text: str) -> Optional[tuple]:
    """Returns (index, sentence) of the first sentence carrying a world record claim."""
    for i, s in enumerate(split_sentences(text)):
        if is_record_sentence(s):
            return i, s
    return None


def build_record_snippet(title: str, text: str, max_chars: int = 240) -> str:
    """Snippet centred on the record sentence, with a context sentence if it fits."""
    sentences = split_sentences(text)
    found = find_record_sentence(text)
    if not found:
        return ""
    idx, rec = found
    if idx > 0:
        intro = sentences[0]
        # Record sentence starts with a pronoun or doesn't name the subject -> add intro
        needs_context = re.match(r"^(it|its|this|they|their|he|she|his|her|the\s+\w+)\b", rec, re.I) \
            or title.split(":")[0].lower()[:12] not in rec.lower()
        if needs_context and len(intro) + len(rec) + 1 <= max_chars:
            return f"{intro} {rec}"
    if len(rec) > max_chars:
        return rec[: max_chars - 3].rsplit(" ", 1)[0] + "..."
    if idx == 0 and len(sentences) > 1 and len(rec) + len(sentences[1]) + 1 <= max_chars:
        return f"{rec} {sentences[1]}"
    return rec


def build_record_hook(name: str, sentence: str) -> str:
    """
    Extracts a punchy world-record hook title, e.g.:
    "Statue of Unity: World's tallest statue"
    "Neil Armstrong: First person to walk on the Moon"
    "Colosseum: Largest ancient amphitheatre on Earth"
    """
    cleaned_name = name.split(":")[0].strip()
    
    m_worlds = re.search(
        r"\b(world'?s\s+(?:[a-z]+-)?(?:largest|smallest|tallest|fastest|deepest|heaviest|lightest|oldest|highest|lowest|longest|busiest|deadliest|costliest|first|only)(?:\s+[\w-]+){1,4})\b",
        sentence,
        re.I,
    )
    if m_worlds:
        return f"{cleaned_name}: {m_worlds.group(1).strip().capitalize()}"

    m_in_world = re.search(
        r"\b(?:the\s+)?((?:[a-z]+-)?(?:largest|smallest|tallest|fastest|deepest|heaviest|lightest|oldest|highest|lowest|longest|busiest|deadliest|costliest)(?:\s+[\w-]+){1,4})\s+(?:in\s+the\s+world|on\s+earth|ever\s+built|ever\s+recorded|in\s+history)\b",
        sentence,
        re.I,
    )
    if m_in_world:
        return f"{cleaned_name}: {m_in_world.group(1).strip().capitalize()} on Earth"

    m_first = re.search(
        r"\bthe\s+first\s+([\w\s-]+?\s+to\s+[\w\s-]+?)(?=[,.;]|\s+in\s+|\s+during\s+)",
        sentence,
        re.I,
    )
    if m_first:
        claim = m_first.group(0).strip().replace("the first", "First")
        return f"{cleaned_name}: {claim[:55]}"

    if re.search(r"\bguinness\b", sentence, re.I):
        return f"{cleaned_name}: Guinness World Record"

    return f"{cleaned_name}: World Record"


# ---------------------------------------------------------------------------
# 2. TOPIC PROFILES FOR THE OTHER 17 CATEGORIES
# ---------------------------------------------------------------------------
# "type" patterns are matched against the Wikipedia short description and the
# "X is a/an ..." part of the first sentence. "kw" are word-prefix keywords.

PROFILES = {
    "space": {
        "type": [r"\bgalax", r"\bstar\b", r"\bstars\b", r"\bnebula", r"\bconstellation", r"\bplanet",
                 r"\bmoon of\b", r"\bnatural satellite", r"\basteroid", r"\bcomet", r"\bexoplanet",
                 r"\bspace probe", r"\bspacecraft", r"\bspace telescope", r"\bquasar", r"\bpulsar",
                 r"\bblack hole", r"\bsupernova", r"\bstar cluster", r"\bcrater on (?:the moon|mars|mercury)",
                 r"\bobservatory", r"\bastronom", r"\bspace station", r"\bspace mission", r"\brover\b",
                 r"\bastronaut", r"\bcosmonaut", r"\bspaceflight", r"\blaunch vehicle"],
        "kw": ["astronom", "orbit", "light-year", "solar system", "nasa", "telescope", "cosmic", "galax",
               "nebula", "planet", "lunar", "interstellar", "astronaut", "cosmonaut", "spaceflight",
               "constellation", "parsec", "magnitude", "mars", "jupiter", "saturn"],
        "neg": [],
    },
    "science": {
        "type": [r"\bchemical element", r"\bchemical compound", r"\bmineral\b", r"\bphysical phenomen",
                 r"\bconcept in physics", r"\bsubatomic particle", r"\belementary particle", r"\bunit of\b",
                 r"\blaw of\b", r"\bchemical reaction", r"\bisotope", r"\bstate of matter", r"\boptical phenomen",
                 r"\bphysical (?:quantity|property|law|constant)", r"\bthermodynamic"],
        "kw": ["physics", "chemical", "chemistry", "molecule", "atom", "electron", "proton", "neutron",
               "quantum", "thermodynamic", "radiation", "wavelength", "crystal", "mineral", "compound",
               "isotope", "laser", "electromagnet", "magnetic field", "particle", "photon", "oxidation"],
        "neg": [],
    },
    "math": {
        "type": [r"\bmathemat", r"\btheorem", r"\bconstant\b", r"\bcurve\b", r"\bpolyhedr", r"\bpolygon",
                 r"\bfractal", r"\bconjecture", r"\bgeometric", r"\bnumber\b", r"\bsequence\b", r"\bsurface\b",
                 r"\bparadox in (?:mathematics|probability|logic)"],
        "kw": ["theorem", "equation", "mathemat", "geometry", "algebra", "integer", "prime number",
               "polynomial", "topolog", "fractal", "proof", "calculus", "polyhedr", "symmetr", "vertices",
               "infinite", "probability", "axiom"],
        "neg": [],
    },
    "philosophy": {
        "type": [r"\bphilosoph", r"\bthought experiment", r"\bethical", r"\bschool of thought",
                 r"\bparadox\b", r"\bmetaphysic", r"\bepistemolog", r"\bstoic", r"\bdoctrine", r"\bargument\b"],
        "kw": ["philosoph", "ethics", "ethical", "metaphysic", "epistemolog", "stoic", "existential",
               "morality", "moral", "consciousness", "plato", "aristotle", "kant", "socrates", "nietzsche",
               "virtue", "free will", "reason", "argument"],
        "neg": [],
    },
    "construction": {
        "type": [r"\bbridge", r"\bskyscraper", r"\bbuilding\b", r"\btower\b", r"\bdam\b", r"\btunnel",
                 r"\bcastle", r"\bcathedral", r"\bchurch", r"\blighthouse", r"\bfortif", r"\bstadium",
                 r"\bviaduct", r"\bcanal\b", r"\bpalace", r"\bminster", r"\bbasilica", r"\barena\b",
                 r"\bstructure\b", r"\baqueduct"],
        "kw": ["construct", "architect", "engineer", "concrete", "steel", "span", "storey", "floors",
               "bridge", "skyscraper", "dam", "tunnel", "completed in", "designed by", "built in", "girder",
               "suspension", "cable-stayed", "masonry", "gothic", "facade", "façade"],
        "neg": [],
    },
    "nature": {
        "type": [r"\bspecies of (?:\w+ )?(?:plant|bird|mammal|insect|reptile|amphibian|tree|fung|flowering plant|"
                 r"butterfl|moth|beetle|spider|snake|lizard|frog|ant|bee|wasp|cat|bear|deer|primate|rodent|bat|orchid|grass|shrub|moss)",
                 r"\bgenus of (?:\w+ )?(?:plant|bird|mammal|insect|reptile|amphibian|tree|fung|flowering plant|dinosaur|butterfl|moth|beetle)",
                 r"\bvolcano", r"\bwaterfall", r"\bnational park", r"\bdinosaur", r"\bextinct", r"\bforest\b",
                 r"\bfamily of (?:plant|bird|mammal|insect)", r"\bsubspecies", r"\bbreed of"],
        "kw": ["species", "habitat", "forest", "wildlife", "predator", "prey", "plant", "flower", "tree",
               "bird", "mammal", "reptile", "insect", "fungus", "fungi", "dinosaur", "volcan", "endangered",
               "ecosystem", "native to", "pollinat", "nocturnal", "herbivor", "carnivor", "iucn"],
        "neg": ["marine", "deep-sea", "ocean"],
    },
    "ocean": {
        "type": [r"\bspecies of (?:[\w-]+ )?(?:fish|shark|ray|crab|squid|octopus|jellyfish|coral|whale|dolphin|"
                 r"crustacean|mollus|cephalopod|sea|marine|shrimp|eel|anglerfish|lobster|starfish|urchin|seal|turtle)",
                 r"\bgenus of (?:[\w-]+ )?(?:fish|shark|ray|crab|squid|octopus|jellyfish|coral|crustacean|mollus|marine|shrimp)",
                 r"\bfamily of (?:[\w-]+ )?(?:fish|shark|crustacean|mollus|marine)", r"\bfish(?:es)?\b",
                 r"\bmesopelagic", r"\bbathypelagic", r"\bdeep-sea",
                 r"\boceanic trench", r"\bsea\b", r"\bocean\b", r"\breef", r"\bsubmarine", r"\bsubmersible",
                 r"\bmarine\b", r"\bseamount", r"\bhydrothermal", r"\bocean current", r"\bgulf\b"],
        "kw": ["ocean", "marine", "sea ", "seas", "deep-sea", "reef", "coral", "fish", "shark", "whale",
               "abyssal", "seafloor", "seabed", "trench", "underwater", "pelagic", "submarine", "submersible",
               "bioluminesc", "tide", "plankton", "diving"],
        "neg": [],
    },
    "biology": {
        "type": [r"\bprotein", r"\benzyme", r"\bgene\b", r"\bcell\b", r"\bmuscle", r"\bbone\b", r"\borgan\b",
                 r"\bnerve", r"\bdisease", r"\bhormone", r"\banatom", r"\bbacteri", r"\bvirus", r"\btissue",
                 r"\bneuro", r"\bbrain", r"\breceptor", r"\bmetabolite", r"\bpathway", r"\bimmun"],
        "kw": ["cell", "protein", "enzyme", "gene", "dna", "rna", "neuron", "brain", "muscle", "organ",
               "tissue", "immune", "anatom", "hormone", "bacteri", "metabol", "receptor", "blood",
               "evolution", "chromosome", "nervous system", "cortex", "mitochond"],
        "neg": [],
    },
    "history": {
        "type": [r"\barchaeological site", r"\bancient (?:city|town|settlement|kingdom|temple)", r"\bmonument",
                 r"\bmemorial", r"\bbattle\b", r"\bempire\b", r"\bdynasty", r"\bkingdom\b", r"\bruins?\b",
                 r"\bhistoric site", r"\bshipwreck", r"\bwar\b", r"\btemple\b", r"\bpyramid", r"\btomb",
                 r"\bancient\b", r"\bmedieval", r"\bweapon", r"\bcivili[sz]ation", r"\bhistoric"],
        "kw": ["ancient", "century", "empire", "dynasty", "archaeolog", "ruins", "medieval", "roman",
               "egypt", "pharaoh", "war", "king", "emperor", "civili", "excavat", " bc", "bce", "conquer",
               "kingdom", "temple", "tomb"],
        "neg": [],
    },
    "geography": {
        "type": [r"\briver\b", r"\blake\b", r"\bmountain", r"\bisland", r"\bdesert", r"\bcanyon", r"\bglacier",
                 r"\bcave\b", r"\bpeninsula", r"\bplateau", r"\bfjord", r"\bvalley", r"\bcape\b", r"\bstrait",
                 r"\bbay\b", r"\bpeak\b", r"\bmassif", r"\bcaldera", r"\bdepression\b", r"\bsalt flat",
                 r"\barchipelago", r"\bgeyser", r"\bhot spring", r"\bwaterfall"],
        "kw": ["river", "lake", "mountain", "island", "desert", "canyon", "glacier", "cave", "elevation",
               "km2", "sq mi", "peninsula", "plateau", "basin", "terrain", "coast", "summit", "above sea level",
               "below sea level", "tributary", "range", "geolog"],
        "neg": [],
    },
    "tech": {
        "type": [r"\bcomputer", r"\bmicroprocessor", r"\bsoftware", r"\brobot", r"\bvehicle", r"\bcar\b",
                 r"\bsports car", r"\baircraft", r"\bairliner", r"\blocomotive", r"\belectric", r"\bdevice",
                 r"\binvention", r"\bprogramming language", r"\bengine\b", r"\btrain\b", r"\bmaglev",
                 r"\bsupercomputer", r"\bparticle accelerator", r"\bsemiconductor", r"\bradar", r"\bdisplay",
                 r"\btechnolog", r"\bnuclear weapon", r"\blaunch vehicle", r"\brocket\b", r"\bairship"],
        "kw": ["computer", "processor", "software", "transistor", "robot", "engine", "electric", "vehicle",
               "aircraft", "locomotive", "invent", "patent", "digital", "chip", "battery", "network",
               "device", "prototype", "horsepower", "km/h", "mph", "manufactur", "silicon"],
        "neg": [],
    },
    "art": {
        "type": [r"\bpainting", r"\bsculpture", r"\bstatue", r"\bmural", r"\bfresco", r"\bartist\b",
                 r"\bpainter", r"\bsculptor", r"\bartwork", r"\bart movement", r"\btapestry", r"\bmosaic",
                 r"\bportrait", r"\bwork of art", r"\bpublic art", r"\bfountain"],
        "kw": ["painting", "painted", "canvas", "sculpture", "sculpt", "artist", "museum", "gallery",
               "fresco", "oil on", "portrait", "renaissance", "baroque", "impressionis", "louvre", "bronze",
               "marble", "masterpiece", "exhibit"],
        "neg": [],
    },
    "cinema": {
        "type": [r"\bfilm\b", r"\bmovie", r"\bfilm director", r"\banimation studio", r"\bcinematograph",
                 r"\bspecial effect", r"\bvisual effect", r"\btelevision series", r"\bfilm technique",
                 r"\bfilm genre", r"\bfilmmak", r"\bfilm studio", r"\bphotographic process"],
        "kw": ["film", "cinema", "director", "screenplay", "box office", "hollywood", "animation",
               "academy award", "oscar", "camera", "scene", "studio", "premiere", "starring", "filmed"],
        "neg": [],
    },
    "music": {
        "type": [r"\bsingle by\b", r"\bsong by\b", r"\bsong (?:written|recorded)", r"\balbum by\b",
                 r"\brock band", r"\bband\b", r"\bmusical instrument", r"\bcomposer", r"\bsinger",
                 r"\bmusician", r"\bmusic genre", r"\bduo\b", r"\bmusic group", r"\b(?:string|wind|percussion|keyboard|brass) instrument",
                 r"\bsynthesi[sz]er", r"\bsong\b", r"\bopera\b", r"\bsymphon"],
        "kw": ["band", "song", "album", "guitar", "bass", "drum", "vocal", "singer", "lyric", "single",
               "chart", "composer", "instrument", "orchestra", "symphon", "melod", "rock", "music",
               "billboard", "concert", "tour", "frontman"],
        "neg": [],
    },
    "literature": {
        "type": [r"\bnovel\b", r"\bpoem\b", r"\bbook\b", r"\bepic\b", r"\bmanuscript", r"\bplay by\b",
                 r"\bshort story", r"\bliterary", r"\bwriter\b", r"\bpoet\b", r"\bnovelist", r"\bpoetry",
                 r"\bliterature", r"\bplaywright", r"\bnovella", r"\bfairy tale", r"\bmyth"],
        "kw": ["novel", "poem", "poet", "author", "book", "published", "literary", "manuscript", "epic",
               "chapter", "fiction", "writer", "prose", "verse", "playwright", "narrat", "saga", "library"],
        "neg": ["video game"],
    },
    "culinary": {
        "type": [r"\bdish\b", r"\bfood\b", r"\bcheese", r"\bspice", r"\bherb\b", r"\bsauce", r"\bsoup",
                 r"\bbread", r"\bpastr", r"\bbeverage", r"\bcuisine", r"\bcooking", r"\bfruit\b", r"\bcondiment",
                 r"\bdrink\b", r"\bdessert", r"\bcake\b", r"\bsweet\b", r"\bnut\b", r"\bfermented"],
        "kw": ["dish", "cuisine", "cooked", "cooking", "recipe", "flavo", "ingredient", "food", "eaten",
               "spice", "sauce", "baked", "fried", "cheese", "culinary", "taste", "dough", "ferment", "edible"],
        "neg": [],
    },
    "fitness": {
        "type": [r"\bexercise", r"\bsport\b", r"\bathletic", r"\bmartial art", r"\btraining", r"\bolympic",
                 r"\btrack and field", r"\bgymnastic", r"\bweight training", r"\bcalisthenic", r"\brace\b",
                 r"\bdance\b", r"\bteam sport"],
        "kw": ["exercise", "training", "muscle", "athlete", "sport", "workout", "strength", "running",
               "endurance", "olympic", "fitness", "aerobic", "weightlift", "gymnast", "stretch", "cardio",
               "physical activity", "squat", "sprint"],
        "neg": [],
    },
}

_COMPILED = {
    cat: {
        "type": [re.compile(p, re.I) for p in prof["type"]],
        "kw": [re.compile(r"\b" + re.escape(k), re.I) for k in prof["kw"]],
        "neg": [re.compile(r"\b" + re.escape(k), re.I) for k in prof["neg"]],
    }
    for cat, prof in PROFILES.items()
}

TYPE_PHRASE = re.compile(r"\b(?:is|was|are|were)\s+(?:an?|the)\s+([^.,;]{3,90})", re.I)


def _type_phrase(first_sentence: str) -> str:
    m = TYPE_PHRASE.search(first_sentence or "")
    return m.group(1) if m else ""


def score_categories(title: str, description: str, text: str) -> dict:
    title = title or ""
    description = description or ""
    text = text or ""
    first = split_sentences(text)[0] if split_sentences(text) else text
    phrase = _type_phrase(first)

    scores = {}
    for cat, prof in _COMPILED.items():
        s = 0
        if description and any(p.search(description) for p in prof["type"]):
            s += 6
        if phrase and any(p.search(phrase) for p in prof["type"]):
            s += 4
        kw_score = 0
        for k in prof["kw"]:
            if k.search(title):
                kw_score += 2
            elif k.search(text):
                kw_score += 1
        s += min(kw_score, 6)
        for n in prof["neg"]:
            if n.search(text) or n.search(description):
                s -= 3
        scores[cat] = s
    return scores


# ---------------------------------------------------------------------------
# 3. PUBLIC API
# ---------------------------------------------------------------------------

SOURCE_PRIOR = 2      # small bonus for the category the article was crawled from
MIN_SCORE = 5         # below this we reject the fact rather than guess


def classify(title: str, description: str, text: str, source_cat: Optional[str] = None) -> dict:
    """
    Returns {"category": str|None, "score": int, "reason": str, "scores": dict}.
    category None means: no confident category -> do not publish this fact.
    """
    if find_record_sentence(text):
        return {"category": "records", "score": 100, "reason": "explicit global record claim", "scores": {}}

    scores = score_categories(title, description, text)
    if source_cat in scores:
        scores[source_cat] += SOURCE_PRIOR

    best_cat, best = max(scores.items(), key=lambda kv: kv[1])
    if best < MIN_SCORE:
        return {"category": None, "score": best, "reason": "no confident category", "scores": scores}
    return {"category": best_cat, "score": best, "reason": "content score", "scores": scores}
