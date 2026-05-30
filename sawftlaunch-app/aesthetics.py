"""The crayon box — SawftLaunch's curated aesthetic library (v1).

Each aesthetic is a structured "recipe". The AI brain (Step C) chooses ONE that
best fits the maker, then personalizes the palette + tagline. The renderer
(Step D) turns the chosen recipe + personalization into a styled page.

`effect` names map to a visual treatment implemented in the renderer/CSS.
`base_palette` is a tasteful default the brain may keep or re-tint.
"""

AESTHETICS = {
    "cybersigilism": {
        "name": "Cybersigilism",
        "description": (
            "Spiky, occult-techno line work. Thin tribal-glyph strokes, deep void "
            "backgrounds, one electric accent. Feels underground, future-mystic, sharp."
        ),
        "vibe_keywords": [
            "edgy", "futuristic", "underground", "mystical", "techno", "rave",
            "dark", "alt", "y2k", "tattoo", "occult", "glitch",
        ],
        "fonts": {
            "display": "Orbitron",
            "body": "Rajdhani",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800&family=Rajdhani:wght@400;600&display=swap",
        },
        "base_palette": {"bg": "#07070a", "ink": "#e9e9f2", "accent": "#9dff3c", "accent2": "#5b2bff", "soft": "#1a1a24"},
        "effect": "sigil-lines",
    },
    "pasifika": {
        "name": "Pasifika",
        "description": (
            "Polynesian art heritage. Bold tapa-cloth geometric motifs, ocean-and-earth "
            "tones, warm and rooted. Feels human, storied, made by hand."
        ),
        "vibe_keywords": [
            "island", "ocean", "heritage", "cultural", "warm", "natural", "earthy",
            "community", "craft", "tribal", "tropical", "storytelling",
        ],
        "fonts": {
            "display": "DM Serif Display",
            "body": "Mulish",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Mulish:wght@400;600&display=swap",
        },
        "base_palette": {"bg": "#1c2b2d", "ink": "#f4ece0", "accent": "#e1873b", "accent2": "#3f8f86", "soft": "#2c4042"},
        "effect": "tapa-pattern",
    },
    "vaporwave": {
        "name": "Vaporwave",
        "description": (
            "Neon-on-night nostalgia. Sunset gradients, chrome, retro-future glow. "
            "Feels dreamy, cinematic, a little melancholic."
        ),
        "vibe_keywords": [
            "retro", "neon", "80s", "synthwave", "dreamy", "nostalgic", "aesthetic",
            "music", "vibe", "gradient", "sunset", "cinematic",
        ],
        "fonts": {
            "display": "Orbitron",
            "body": "Jost",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Jost:wght@300;400;500&display=swap",
        },
        "base_palette": {"bg": "#160a2b", "ink": "#fdeafb", "accent": "#ff4fd8", "accent2": "#36e7ff", "soft": "#3a1f63"},
        "effect": "neon-grid",
    },
    "editorial-luxe": {
        "name": "Editorial Luxe",
        "description": (
            "Quiet, expensive, considered. High-contrast serif, airy spacing, ivory and "
            "ink with a restrained metallic accent. Feels grown-up and premium."
        ),
        "vibe_keywords": [
            "luxury", "elegant", "premium", "minimal", "fashion", "editorial",
            "refined", "classic", "sophisticated", "clean", "calm", "timeless",
        ],
        "fonts": {
            "display": "Cormorant Garamond",
            "body": "Jost",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Jost:wght@300;400;500&display=swap",
        },
        "base_palette": {"bg": "#f7f4ee", "ink": "#15140f", "accent": "#9a7b3f", "accent2": "#3a3a38", "soft": "#e4dccb"},
        "effect": "fine-rules",
    },
}


def aesthetic_ids():
    return list(AESTHETICS.keys())


def get_aesthetic(aesthetic_id):
    return AESTHETICS.get(aesthetic_id)
