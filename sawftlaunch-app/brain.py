"""The brain — turns a maker's photos + answers into a personalized identity.

Uses Claude (Opus 4.7, vision) with structured outputs to pick the best-fitting
aesthetic from the curated crayon box and personalize its palette, name, and
tagline. The model can only choose an aesthetic id that actually exists, and the
output is schema-validated, so the rest of the app gets clean, predictable data.
"""

import re
from enum import Enum

import anthropic
from pydantic import BaseModel

import aesthetics

MODEL = "claude-opus-4-7"

# Constrain the model's choice to aesthetics that actually exist in the box.
# (Enum member names can't contain hyphens, so sanitize the name but keep the
# real id as the value — e.g. member EDITORIAL_LUXE has value "editorial-luxe".)
AestheticId = Enum(
    "AestheticId",
    {aid.replace("-", "_"): aid for aid in aesthetics.aesthetic_ids()},
    type=str,
)

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class Palette(BaseModel):
    bg: str
    ink: str
    accent: str
    accent2: str
    soft: str


class Identity(BaseModel):
    aesthetic_id: AestheticId
    brand_name: str
    eyebrow: str
    tagline: str
    palette: Palette


def _catalog_text():
    lines = []
    for aid, a in aesthetics.AESTHETICS.items():
        lines.append(
            f"- id: {aid}\n"
            f"  name: {a['name']}\n"
            f"  description: {a['description']}\n"
            f"  fits people who feel: {', '.join(a['vibe_keywords'])}\n"
            f"  base_palette (a starting point you may re-tint): {a['base_palette']}"
        )
    return "\n".join(lines)


SYSTEM = (
    "You are SawftLaunch's design brain. SawftLaunch turns who a person is into a "
    "living brand identity — fonts, colors, and an aesthetic mood — that their "
    "website can wear.\n\n"
    "You will be given some photos of a maker (and/or their work) plus a few "
    "answers about themselves. Your job:\n"
    "1. Choose the SINGLE best-fitting aesthetic for them from the curated list "
    "below. You MUST return one of these exact ids.\n"
    "2. Personalize it: craft a short brand name (use the maker's stated name if "
    "they gave one; otherwise invent a fitting, memorable one), a tiny eyebrow "
    "label (2-4 words, e.g. a category or 'soft launch'), and ONE evocative "
    "tagline (a single sentence, ~12 words max).\n"
    "3. Produce a palette of 5 hex colors (bg, ink, accent, accent2, soft) that "
    "suit BOTH the chosen aesthetic AND this specific person. Start from the "
    "aesthetic's base_palette and adjust it toward them. Every value must be a "
    "6-digit hex like #1a2b3c. Ensure ink reads clearly against bg.\n\n"
    "Be tasteful and specific to the person — not generic. Here is the crayon box:\n\n"
    f"{_catalog_text()}"
)


def _safe_palette(model_palette, base_palette):
    """Trust the model's palette, but fall back to base for any malformed hex."""
    out = {}
    mp = model_palette.model_dump()
    for key, base_val in base_palette.items():
        val = mp.get(key, "")
        out[key] = val if isinstance(val, str) and _HEX_RE.match(val) else base_val
    return out


def generate_identity(images=None, answers=None):
    """Generate a personalized identity.

    images:  list of (media_type, base64_data) tuples (may be empty)
    answers: dict of question -> answer strings
    Returns a dict: {aesthetic_id, brand_name, eyebrow, tagline, palette}.
    """
    images = images or []
    answers = answers or {}

    content = []
    for media_type, b64 in images:
        content.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64},
            }
        )

    answer_text = "\n".join(f"- {k}: {v}" for k, v in answers.items() if v) or "(no answers provided)"
    content.append(
        {
            "type": "text",
            "text": (
                "Here is the maker. Their answers:\n"
                f"{answer_text}\n\n"
                "Design their SawftLaunch identity now."
            ),
        }
    )

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.parse(
        model=MODEL,
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": SYSTEM,
                "cache_control": {"type": "ephemeral"},  # catalog is stable -> cache it
            }
        ],
        messages=[{"role": "user", "content": content}],
        output_format=Identity,
    )

    identity = response.parsed_output
    aesthetic_id = identity.aesthetic_id.value
    base = aesthetics.get_aesthetic(aesthetic_id)["base_palette"]

    return {
        "aesthetic_id": aesthetic_id,
        "brand_name": identity.brand_name.strip(),
        "eyebrow": identity.eyebrow.strip(),
        "tagline": identity.tagline.strip(),
        "palette": _safe_palette(identity.palette, base),
    }
