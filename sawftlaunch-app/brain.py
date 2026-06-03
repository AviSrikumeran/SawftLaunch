"""The brain — the art director.

Given a barber's photos + answers, Claude (Opus 4.7, vision) composes a full
design spec from the curated design system (design.py): a layout, a type system,
a shape language, a personalized palette — plus the portfolio copy. Output is
schema-validated so every choice is one the renderer knows how to make look good.
"""

import re
from enum import Enum

import anthropic
from pydantic import BaseModel

import design

MODEL = "claude-opus-4-7"

# Constrain each design axis to ids that actually exist (hyphens -> underscores
# in the enum member name, real id stays as the value).
Layout = Enum("Layout", {x.replace("-", "_"): x for x in design.layout_ids()}, type=str)
FontPairing = Enum("FontPairing", {x.replace("-", "_"): x for x in design.font_ids()}, type=str)
Shape = Enum("Shape", {x.replace("-", "_"): x for x in design.shape_ids()}, type=str)

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class Palette(BaseModel):
    bg: str
    ink: str
    accent: str
    accent2: str
    soft: str


class DesignDNA(BaseModel):
    """The deconstruction — what the engine 'read' out of the inspiration."""
    palette_seen: list[str]   # hex colors actually present in the inspo
    type_character: str       # how the typography feels (e.g. "tall condensed, industrial")
    composition: str          # layout / structure / spacing principles observed
    mood: list[str]           # 3-5 mood keywords
    what_works: str           # the 'why' — what makes the inspiration land


class Identity(BaseModel):
    dna: DesignDNA
    layout: Layout
    font_pairing: FontPairing
    shape: Shape
    brand_name: str
    eyebrow: str
    tagline: str
    bio: str
    specialties: list[str]
    palette: Palette


SYSTEM = (
    "You are SawftLaunch's DESIGN ENGINE. SawftLaunch builds premium PORTFOLIO pages "
    "for barbers and other solo, appointment-based pros (hair stylists, tattoo "
    "artists, estheticians) so they look distinct and premium, escape the "
    "'everyone looks the same on Instagram, it's a price war' trap, and raise their prices.\n\n"
    "The images you're given are INSPIRATION the user loves (designs, shops, looks) — "
    "NOT their own work. Do TWO things:\n\n"
    "PART 1 — DECONSTRUCT the inspiration into its design DNA (be specific, like a "
    "design critic):\n"
    "   - palette_seen: the actual hex colors present across the inspo.\n"
    "   - type_character: how the typography feels (weight, contrast, serif/sans, attitude).\n"
    "   - composition: the layout/structure/spacing principles at play.\n"
    "   - mood: 3-5 mood keywords.\n"
    "   - what_works: the 'why' — what actually makes this inspiration land.\n\n"
    "PART 2 — RECONSTRUCT something ORIGINAL for THIS person from that DNA (never a "
    "copy — channel the feeling, don't clone the source). Compose:\n"
    "   - layout — the structure that best channels the DNA.\n"
    "   - font_pairing — the type system closest in spirit to type_character.\n"
    "   - shape — corner language (sharp/rounded/soft) matching the mood.\n"
    "   - palette — 5 cohesive hex colors (bg, ink, accent, accent2, soft) derived from "
    "palette_seen but tuned for a usable page. CRITICAL: ink must read clearly on bg "
    "(strong contrast); tasteful, not garish.\n\n"
    "Then write their portfolio copy — confident, premium, specific, never generic:\n"
    "   - brand_name (use the name they gave; else invent a strong one)\n"
    "   - eyebrow: 2-4 words (e.g. 'Master Barber · Brooklyn')\n"
    "   - tagline: ONE evocative sentence, ~12 words max\n"
    "   - bio: 2-3 sentences, warm + confident, on why their chair is different. No cliches.\n"
    "   - specialties: 3-5 short tags (e.g. 'Skin fades', 'Beard sculpting').\n\n"
    "If no inspiration images are given, infer a fitting DNA from what they do. "
    "Pair layout, fonts, shape and palette into ONE coherent feeling. Your kit:\n\n"
    f"{design.catalog_text()}"
)


def _safe_palette(model_palette, base_palette):
    out = {}
    mp = model_palette.model_dump()
    for key, base_val in base_palette.items():
        val = mp.get(key, "")
        out[key] = val if isinstance(val, str) and _HEX_RE.match(val) else base_val
    return out


def generate_identity(images=None, answers=None):
    """Compose a personalized design spec + portfolio copy. Returns a dict."""
    images = images or []
    answers = answers or {}

    content = []
    for media_type, b64 in images:
        content.append(
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}
        )
    answer_text = "\n".join(f"- {k}: {v}" for k, v in answers.items() if v) or "(no answers provided)"
    content.append(
        {"type": "text", "text": f"The images above are their INSPIRATION (if any). About them:\n{answer_text}\n\nDeconstruct the inspiration, then forge their original page."}
    )

    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": content}],
        output_format=Identity,
    )

    iden = response.parsed_output
    dna = iden.dna
    return {
        "dna": {
            "palette_seen": [c for c in dna.palette_seen if _HEX_RE.match(c)][:6],
            "type_character": dna.type_character.strip(),
            "composition": dna.composition.strip(),
            "mood": [m.strip() for m in dna.mood if m.strip()][:5],
            "what_works": dna.what_works.strip(),
        },
        "layout": iden.layout.value,
        "font_pairing": iden.font_pairing.value,
        "shape": iden.shape.value,
        "brand_name": iden.brand_name.strip(),
        "eyebrow": iden.eyebrow.strip(),
        "tagline": iden.tagline.strip(),
        "bio": iden.bio.strip(),
        "specialties": [s.strip() for s in iden.specialties if s.strip()][:5],
        "palette": _safe_palette(iden.palette, design.DEFAULT_PALETTE),
    }
