"""The design system the LLM art-directs from.

Instead of recoloring one template, the model composes a full design spec by
choosing from vetted, premium primitives along several axes:
  - layout       : a genuinely different page structure/treatment
  - font_pairing : a hand-picked display+body type system (loaded per page)
  - shape        : the corner-radius language
plus a personalized palette. Every primitive is curated to look good, so the
combinatorial output is varied AND reliably premium.
"""

# --- type systems (display + body + the exact Google Fonts URL to load) -------
FONT_PAIRINGS = {
    "editorial-serif": {
        "display": "Fraunces", "body": "Newsreader",
        "url": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,900&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap",
        "note": "characterful high-contrast serif + literary body. Refined, magazine.",
    },
    "quiet-luxe": {
        "display": "Cormorant Garamond", "body": "Jost",
        "url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@300;400;500&display=swap",
        "note": "airy high-fashion serif + clean geometric body. Expensive, restrained.",
    },
    "modern-grotesk": {
        "display": "Bricolage Grotesque", "body": "Jost",
        "url": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Jost:wght@400;500&display=swap",
        "note": "bold characterful sans + clean body. Modern, confident, friendly.",
    },
    "heavy-impact": {
        "display": "Archivo Black", "body": "Archivo",
        "url": "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@400;500;600&display=swap",
        "note": "ultra-heavy grotesque + workhorse body. Loud, bold, street.",
    },
    "condensed-utility": {
        "display": "Oswald", "body": "Barlow",
        "url": "https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Barlow:wght@400;600&display=swap",
        "note": "tall condensed display + utilitarian body. Sporty, industrial, sharp.",
    },
    "warm-humanist": {
        "display": "DM Serif Display", "body": "Mulish",
        "url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Mulish:wght@400;600&display=swap",
        "note": "soft warm serif + humanist body. Approachable, crafted, organic.",
    },
}

# --- layouts (genuinely different page structures) ----------------------------
LAYOUTS = {
    "editorial": "Magazine. Left-aligned, asymmetric, big serif display, generous "
                 "whitespace, hairline rules, tidy gallery grid. Refined and grown-up.",
    "bold": "High-energy. Huge centered headline, saturated color-blocked sections, "
            "big confident gallery, chunky buttons. Loud and memorable.",
    "moody": "Cinematic and dark. Full-bleed feel, dramatic contrast, image-forward "
             "with a large feature shot, restrained text. Premium and intense.",
}

# --- shape language -----------------------------------------------------------
SHAPES = {"sharp": "2px", "rounded": "16px", "soft": "30px"}

DEFAULT_PALETTE = {"bg": "#f6f1e7", "ink": "#1d1b18", "accent": "#b5482e", "accent2": "#7d8466", "soft": "#cdbfa6"}


def font_ids():
    return list(FONT_PAIRINGS.keys())


def layout_ids():
    return list(LAYOUTS.keys())


def shape_ids():
    return list(SHAPES.keys())


def get_fonts(pairing_id):
    return FONT_PAIRINGS.get(pairing_id, FONT_PAIRINGS["modern-grotesk"])


def get_radius(shape_id):
    return SHAPES.get(shape_id, SHAPES["rounded"])


def catalog_text():
    """Human-readable menu of the kit for the art-director prompt."""
    fonts = "\n".join(f"  - {k}: {v['note']}" for k, v in FONT_PAIRINGS.items())
    lays = "\n".join(f"  - {k}: {v}" for k, v in LAYOUTS.items())
    shapes = ", ".join(f"{k}" for k in SHAPES)
    return (
        f"LAYOUTS (choose one structure that fits them):\n{lays}\n\n"
        f"FONT_PAIRINGS (choose one type system):\n{fonts}\n\n"
        f"SHAPE (corner language): {shapes}"
    )
