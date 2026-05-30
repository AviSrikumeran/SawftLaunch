import difflib
import json
import random
import urllib.error
import urllib.request

from mcp.server.fastmcp import FastMCP

API_URL = "https://avisrikumeran.github.io/SawftLaunch/identities.json"

mcp = FastMCP("SawftLaunch Identity")


def _fetch_directions():
    """GET the live identities JSON and return its list of directions."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "sawftlaunch-mcp"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    return data["directions"]


def _format_direction(d):
    """Render one direction as clean, readable text."""
    fonts = d["fonts"]
    palette = d["palettes"][0]
    palette_str = "  ".join(f"{k}={v}" for k, v in palette.items())
    return (
        f"Design identity: {d['name']}\n"
        f"{d['description']}\n\n"
        f"Fonts\n"
        f"  Display: {fonts['display']['name']} ({fonts['display']['weight']})\n"
        f"  Body:    {fonts['body']['name']} ({fonts['body']['weight']})\n\n"
        f"Palette\n"
        f"  {palette_str}"
    )


def _match_vibe(vibe, directions):
    """Loosely match a requested vibe to a direction. Returns a direction or None."""
    v = vibe.strip().lower()

    # 1) exact match on id or name
    for d in directions:
        if v == d["id"].lower() or v == d["name"].lower():
            return d

    # 2) substring match (e.g. "pastel" -> "Soft / Pastel")
    for d in directions:
        if v in d["id"].lower() or v in d["name"].lower():
            return d

    # 3) fuzzy match for typos (e.g. "editrial" -> "editorial")
    lookup = {}
    for d in directions:
        lookup[d["id"].lower()] = d
        lookup[d["name"].lower()] = d
    close = difflib.get_close_matches(v, list(lookup), n=1, cutoff=0.6)
    if close:
        return lookup[close[0]]

    return None


@mcp.tool()
def get_design_identity(vibe: str | None = None) -> str:
    """Fetch a design identity (fonts + color palette) from SawftLaunch.

    Pass an optional `vibe` (e.g. "editorial", "luxe", "playful") to get that
    specific direction; small typos are tolerated. Omit it to get a random one.
    """
    try:
        directions = _fetch_directions()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return f"Sorry, couldn't reach the SawftLaunch API right now ({e}). Please try again in a moment."
    except (KeyError, ValueError) as e:
        return f"The SawftLaunch API returned data in an unexpected format ({e})."

    if not directions:
        return "The SawftLaunch API returned no design directions."

    if vibe:
        chosen = _match_vibe(vibe, directions)
        if chosen is None:
            available = ", ".join(d["id"] for d in directions)
            return f"No design direction matches '{vibe}'. Available vibes: {available}."
    else:
        chosen = random.choice(directions)

    return _format_direction(chosen)


if __name__ == "__main__":
    mcp.run()
